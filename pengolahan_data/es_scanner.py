import logging
import time
from typing import Any, Dict, Generator, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("es_scanner")


class ElasticsearchScanner:
    """
    Elasticsearch Scanner client menggunakan Scroll API & sort: ["_doc"]
    untuk crawling data berkecepatan tinggi tanpa dependency numpy/elasticsearch client mismatch.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5200,
        index: str = "smm-data-hot-20260804",
        user: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        self.host = host.strip()
        self.port = port
        self.index = index.strip()
        self.user = user
        self.password = password
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}"

        # Inisialisasi HTTP Session dengan Retry
        self.session = requests.Session()
        if self.user and self.password:
            self.session.auth = (self.user, self.password)

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def ping(self) -> bool:
        """Memeriksa koneksi ke cluster Elasticsearch"""
        try:
            r = self.session.get(self.base_url, timeout=5)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Gagal terhubung ke Elasticsearch di {self.base_url}: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """Mendapatkan informasi node / cluster Elasticsearch"""
        r = self.session.get(self.base_url, timeout=10)
        r.raise_for_status()
        return r.json()

    def get_count(self, platform: Optional[str] = None, index: Optional[str] = None) -> Optional[int]:
        """Mendapatkan estimasi jumlah data berdasarkan platform"""
        target_index = index or self.index
        url = f"{self.base_url}/{target_index}/_count"
        payload: Dict[str, Any] = {}
        if platform:
            payload = {"query": {"term": {"platform": platform}}}

        try:
            r = self.session.post(url, json=payload, timeout=20)
            if r.status_code == 200:
                return r.json().get("count")
        except Exception as e:
            logger.warning(f"Tidak dapat mengambil count untuk platform '{platform}': {e}")
        return None

    def clear_scroll(self, scroll_id: str):
        """Membersihkan scroll context pada cluster Elasticsearch untuk menghemat resource RAM/cache"""
        if not scroll_id:
            return
        try:
            self.session.delete(
                f"{self.base_url}/_search/scroll",
                json={"scroll_id": scroll_id},
                timeout=5
            )
        except Exception:
            pass

    def scan(
        self,
        platform: Optional[str] = None,
        source_fields: Optional[List[str]] = None,
        batch_size: int = 1000,
        scroll_time: str = "2m",
        limit: Optional[int] = None,
        custom_query: Optional[Dict[str, Any]] = None,
        index: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generator untuk crawling data menggunakan metode scan/scroll.
        
        Args:
            platform: Nama platform ('twitter', 'instagram', 'tiktok', 'youtube', 'threads', 'facebook').
            source_fields: List field yang ingin diambil (proyeksi _source).
            batch_size: Ukuran batch per request (default: 1000).
            scroll_time: Waktu simpan konteks scroll (default: '2m').
            limit: Batas maksimum dokumen yang diambil (None = ambil semua).
            custom_query: Query kustom jika ingin filter tambahan.
            index: Nama index jika ingin override default index.

        Yields:
            Dict dokumen (_source).
        """
        target_index = index or self.index
        search_url = f"{self.base_url}/{target_index}/_search?scroll={scroll_time}"
        scroll_url = f"{self.base_url}/_search/scroll"

        # Bangun query filter
        if custom_query:
            query = custom_query
        elif platform:
            query = {"term": {"platform": platform}}
        else:
            query = {"match_all": {}}

        # Payload inisial dengan sort _doc (prinsip scan di ES)
        payload: Dict[str, Any] = {
            "size": batch_size,
            "query": query,
            "sort": ["_doc"]
        }

        if source_fields:
            payload["_source"] = source_fields

        scroll_id = None
        total_yielded = 0

        try:
            logger.info(f"Memulai Scan Elasticsearch | Index: {target_index} | Platform: {platform or 'ALL'} | Batch: {batch_size}")
            r = self.session.post(search_url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            res_data = r.json()

            scroll_id = res_data.get("_scroll_id")
            hits_data = res_data.get("hits", {})
            hits = hits_data.get("hits", [])
            total_hits = hits_data.get("total", 0)

            if isinstance(total_hits, dict):  # Format ES 7+
                total_hits = total_hits.get("value", 0)

            logger.info(f"Total dokumen terdeteksi: {total_hits:,} | Scroll ID dibuat")

            while hits:
                for hit in hits:
                    source = hit.get("_source", {})
                    # Tambahkan _id jika belum ada di source
                    if "id" not in source and "_id" in hit:
                        source["id"] = hit["_id"]
                    
                    yield source
                    total_yielded += 1

                    if limit is not None and total_yielded >= limit:
                        logger.info(f"Mencapai limit {limit} dokumen.")
                        return

                if not scroll_id:
                    break

                # Fetch batch berikutnya dengan Scroll ID
                scroll_payload = {
                    "scroll": scroll_time,
                    "scroll_id": scroll_id
                }
                
                r = self.session.post(scroll_url, json=scroll_payload, timeout=self.timeout)
                r.raise_for_status()
                res_data = r.json()
                scroll_id = res_data.get("_scroll_id", scroll_id)
                hits = res_data.get("hits", {}).get("hits", [])

        except Exception as e:
            logger.error(f"Error saat scan Elasticsearch: {e}")
            raise
        finally:
            if scroll_id:
                self.clear_scroll(scroll_id)
                logger.debug("Scroll context dibersihkan dari server ES.")
            logger.info(f"Selesai Scan | Total dokumen diambil: {total_yielded:,}")
