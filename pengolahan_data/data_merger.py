import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from config import SUPPORTED_PLATFORMS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("data_merger")


def standardize_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standarisasi dan pembersihan dokumen engagement agar memiliki format metrik yang konsisten.
    """
    def to_int(val, default=0):
        try:
            if val is None or pd.isna(val):
                return default
            return int(float(val))
        except (ValueError, TypeError):
            return default

    def to_float(val, default=0.0):
        try:
            if val is None or pd.isna(val):
                return default
            return float(val)
        except (ValueError, TypeError):
            return default

    platform = str(doc.get("platform", "unknown")).lower().strip()

    # Ekstraksi metrik engagement standar & lanjutan
    likes = to_int(doc.get("likes_count"))
    replies = to_int(doc.get("reply_count"))
    shares = to_int(doc.get("shares_count"))
    views = to_int(doc.get("views_count"))
    
    # Quote: threads quote_count atau twitter quoted_user_statuses_count
    quotes = to_int(doc.get("quote_count") or doc.get("quoted_user_statuses_count"))
    
    # Repost: threads repost_count atau tiktok/instagram sub_type repost
    repost = to_int(doc.get("repost_count") or (shares if doc.get("sub_type") in ["repost", "retweet"] else 0))
    
    # Bookmark / Save: bookmark_count, bookmarks_count, save_count, collect_count
    bookmark = to_int(doc.get("bookmark_count") or doc.get("bookmarks_count") or doc.get("save_count") or doc.get("collect_count"))
    
    # Dislike (YouTube)
    dislikes = to_int(doc.get("dislike_count"))
    
    raw_engagements = to_float(doc.get("engagements"))
    watch_ratio = to_float(doc.get("watch_ratio"))
    sub_type_str = str(doc.get("sub_type", "")).lower()
    is_repost_flag = sub_type_str in ["repost", "retweet"] or repost > 0

    # Dokumen terstandarisasi
    standardized = {
        "id": str(doc.get("id", "")),
        "platform": platform,
        "username": str(doc.get("username", "")),
        "user_id": str(doc.get("user_id", "")),
        "user_full_name": str(doc.get("user_full_name", "")),
        "text": str(doc.get("text", "")),
        "created_at": doc.get("created_at"),
        "hour": str(doc.get("hour", "")),
        "dayname": str(doc.get("dayname", "")),
        "post_url": str(doc.get("post_url", "")),
        "user_followers_count": to_int(doc.get("user_followers_count")),
        "user_friends_count": to_int(doc.get("user_friends_count")),
        "likes_count": likes,
        "reply_count": replies,
        "shares_count": shares,
        "views_count": views,
        "quotes_count": quotes,
        "repost_count": repost,
        "bookmark_count": bookmark,
        "dislike_count": dislikes,
        "is_repost": is_repost_flag,
        "engagements_raw": raw_engagements,
        "watch_ratio": watch_ratio,
        "llm_flag": doc.get("llm_flag", None),
        "content_type": str(doc.get("content_type", "")),
        "sub_type": sub_type_str
    }
    return standardized


def load_platform_file(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Membaca file data platform (jsonl, json, csv, parquet) dan mengembalikan list of dict"""
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"File tidak ditemukan: {path}")
        return []

    docs = []
    if path.suffix == ".jsonl":
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        docs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    elif path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                docs = data
            elif isinstance(data, dict):
                docs = [data]
    elif path.suffix == ".csv":
        df = pd.read_csv(path)
        docs = df.to_dict(orient="records")
    elif path.suffix == ".parquet":
        df = pd.read_parquet(path)
        docs = df.to_dict(orient="records")

    return docs


def merge_platform_data(
    data_dir: Union[str, Path],
    platforms: Optional[List[str]] = None,
    output_filepath: Optional[Union[str, Path]] = None,
    export_formats: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Engine untuk menggabungkan data dari berbagai platform menjadi satu DataFrame master.
    
    Args:
        data_dir: Direktori root data (misal: pengolahan_data/data/smm-data-hot-20260804)
        platforms: List platform yang akan digabung (default: semua platform didukung)
        output_filepath: Path untuk menyimpan file gabungan (opsional)
        export_formats: List format export (default: ['jsonl', 'parquet', 'csv'])
        
    Returns:
        pd.DataFrame dataset gabungan terstandarisasi.
    """
    base_path = Path(data_dir)
    target_platforms = platforms or SUPPORTED_PLATFORMS
    all_standardized_docs = []
    summary_counts = {}

    logger.info(f"Memulai proses penggabungan data dari: {base_path}")

    for p in target_platforms:
        p_dir = base_path / p
        if not p_dir.exists():
            # Coba cari file langsung di base_path jika tidak berfolder
            matching_files = list(base_path.glob(f"{p}_*.jsonl")) + list(base_path.glob(f"{p}_*.parquet"))
        else:
            matching_files = list(p_dir.glob("*.jsonl")) + list(p_dir.glob("*.parquet")) + list(p_dir.glob("*.csv"))

        if not matching_files:
            logger.warning(f"Tidak ada file data untuk platform '{p}' di {p_dir}")
            summary_counts[p] = 0
            continue

        # Urutkan berdasarkan waktu modifikasi terbaru
        latest_file = sorted(matching_files, key=lambda x: x.stat().st_mtime)[-1]
        logger.info(f"Membaca platform [{p}]: {latest_file.name}")

        raw_docs = load_platform_file(latest_file)
        standardized = [standardize_document(d) for d in raw_docs]
        all_standardized_docs.extend(standardized)
        summary_counts[p] = len(standardized)

    df_merged = pd.DataFrame(all_standardized_docs)

    if df_merged.empty:
        logger.warning("Dataset gabungan kosong!")
        return df_merged

    # Format timestamp jika ada
    if "created_at" in df_merged.columns:
        df_merged["created_at_dt"] = pd.to_datetime(df_merged["created_at"], errors="coerce")

    logger.info(f"✅ Berhasil menggabungkan {len(df_merged):,} total dokumen dari {len(summary_counts)} platform.")

    # Export jika diminta
    if output_filepath or export_formats:
        out_base = Path(output_filepath) if output_filepath else (base_path / "merged_all_platforms")
        formats = export_formats or ["jsonl", "parquet", "csv"]

        if out_base.suffix:
            # Jika user sudah memberi ekstensi tertentu
            ext = out_base.suffix.lstrip(".")
            if ext == "jsonl":
                df_merged.to_json(out_base, orient="records", lines=True, force_ascii=False, date_format="iso")
            elif ext == "parquet":
                df_merged.to_parquet(out_base, index=False)
            elif ext == "csv":
                df_merged.to_csv(out_base, index=False, encoding="utf-8")
            logger.info(f"File gabungan disimpan di: {out_base}")
        else:
            for fmt in formats:
                target_file = out_base.with_suffix(f".{fmt}")
                if fmt == "jsonl":
                    df_merged.to_json(target_file, orient="records", lines=True, force_ascii=False, date_format="iso")
                elif fmt == "parquet":
                    df_merged.to_parquet(target_file, index=False)
                elif fmt == "csv":
                    df_merged.to_csv(target_file, index=False, encoding="utf-8")
                logger.info(f"File gabungan ({fmt}) disimpan di: {target_file}")

    return df_merged


if __name__ == "__main__":
    import sys
    from config import load_env_config
    config = load_env_config()
    index_name = config["index"]
    data_directory = Path(__file__).resolve().parent / "data" / index_name

    df = merge_platform_data(data_directory)
    print("\n--- RINGKASAN DATA GABUNGAN ---")
    if not df.empty:
        print(df["platform"].value_counts())
        print("\nContoh 5 baris pertama:")
        print(df[["id", "platform", "username", "likes_count", "reply_count", "shares_count", "views_count"]].head())
