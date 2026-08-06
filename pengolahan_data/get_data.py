import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set UTF-8 untuk stdout & stderr di Windows Terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import pandas as pd
from tqdm import tqdm

from config import DEFAULT_SOURCE_FIELDS, SUPPORTED_PLATFORMS, load_env_config
from es_scanner import ElasticsearchScanner


def crawl_platform_data(
    scanner: ElasticsearchScanner,
    platform: str,
    output_dir: Path,
    limit: Optional[int] = None,
    batch_size: int = 1000,
    output_format: str = "jsonl",
    source_fields: Optional[List[str]] = None,
    index_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crawling data untuk satu platform tertentu menggunakan ES Scan dan menyimpannya ke file.
    """
    platform_name = platform.lower().strip()
    target_index = index_name or scanner.index
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{platform_name}_{target_index}_{timestamp}.{output_format}"
    filepath = output_dir / filename

    print(f"\n{'='*60}")
    print(f"🚀 Memulai crawling platform: [{platform_name.upper()}]")
    print(f"📁 Target Output : {filepath}")
    print(f"📑 Index ES      : {target_index}")
    print(f"📦 Batch Size    : {batch_size} | Limit: {limit or 'Semua (Unlimited)'}")
    print(f"{'='*60}")

    # Cek estimasi total count jika memungkinkan
    est_count = scanner.get_count(platform=platform_name, index=target_index)
    total_expected = min(est_count, limit) if (est_count and limit) else (est_count or limit)

    pbar = tqdm(
        total=total_expected,
        desc=f"📥 {platform_name.capitalize():<10}",
        unit=" doc",
        ncols=90,
        dynamic_ncols=True
    )

    t_start = time.time()
    count = 0
    buffer = []
    
    # Buka file stream untuk jsonl
    jsonl_file = None
    if output_format == "jsonl":
        jsonl_file = open(filepath, "w", encoding="utf-8")

    try:
        data_generator = scanner.scan(
            platform=platform_name,
            source_fields=source_fields or DEFAULT_SOURCE_FIELDS,
            batch_size=batch_size,
            limit=limit,
            index=target_index
        )

        for doc in data_generator:
            count += 1
            pbar.update(1)

            if output_format == "jsonl":
                jsonl_file.write(json.dumps(doc, ensure_ascii=False) + "\n")
            else:
                buffer.append(doc)

    except Exception as e:
        print(f"\n❌ Error saat crawling platform {platform_name}: {e}", file=sys.stderr)
        raise
    finally:
        pbar.close()
        if jsonl_file:
            jsonl_file.close()

    duration = time.time() - t_start

    # Simpan untuk format selain jsonl (json, csv, parquet)
    if output_format != "jsonl":
        if output_format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(buffer, f, ensure_ascii=False, indent=2)
        elif output_format == "csv":
            df = pd.DataFrame(buffer)
            df.to_csv(filepath, index=False, encoding="utf-8")
        elif output_format == "parquet":
            df = pd.DataFrame(buffer)
            df.to_parquet(filepath, index=False)

    file_size_mb = filepath.stat().st_size / (1024 * 1024) if filepath.exists() else 0

    print(f"✅ Selesai: {count:,} dokumen disimpan ({file_size_mb:.2f} MB) dalam {duration:.2f} detik.")
    return {
        "platform": platform_name,
        "total_docs": count,
        "duration_sec": round(duration, 2),
        "file_size_mb": round(file_size_mb, 2),
        "file_path": str(filepath)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Crawling data per-platform dari Elasticsearch menggunakan Scan/Scroll API (.env config)."
    )
    parser.add_argument(
        "-p", "--platform",
        type=str,
        default="all",
        help="Platform target: twitter, instagram, tiktok, youtube, threads, facebook, atau 'all' (default: all)"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=1000,
        help="Maksimal jumlah dokumen per platform (default: 1000 data per platform)"
    )
    parser.add_argument(
        "-b", "--batch-size",
        type=int,
        default=1000,
        help="Ukuran batch request scan/scroll (default: 1000)"
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["jsonl", "json", "csv", "parquet"],
        default="jsonl",
        help="Format file output (default: jsonl)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help="Direktori penyimpanan file data (default: pengolahan_data/data)"
    )
    parser.add_argument(
        "-i", "--index",
        type=str,
        default=None,
        help="Override nama index Elasticsearch dari .env"
    )

    args = parser.parse_args()

    # Load konfigurasi dari .env
    config = load_env_config()
    target_index = args.index or config["index"]

    print("="*60)
    print("📋 KONFIGURASI ELASTICSEARCH DARI .env")
    print("="*60)
    print(f"  • DB_HOST     : {config['host']}")
    print(f"  • DB_PORT     : {config['port']}")
    print(f"  • INDEX       : {target_index}")
    print(f"  • BASE_URL    : {config['base_url']}")
    print("="*60)

    # Inisialisasi Scanner
    scanner = ElasticsearchScanner(
        host=config["host"],
        port=config["port"],
        index=target_index,
        user=config["user"],
        password=config["password"]
    )

    if not scanner.ping():
        print("❌ Gagal terhubung ke Elasticsearch server! Pastikan IP/Port dan koneksi VPN/jaringan aktif.")
        sys.exit(1)

    print("🔌 Koneksi ke Elasticsearch OK!\n")

    # Tentukan platform yang akan di-crawl
    if args.platform.lower() == "all":
        platforms_to_crawl = SUPPORTED_PLATFORMS
    else:
        selected = [p.strip().lower() for p in args.platform.split(",") if p.strip()]
        invalid = [p for p in selected if p not in SUPPORTED_PLATFORMS]
        if invalid:
            print(f"⚠️ Platform tidak dikenal: {invalid}. Platform yang didukung: {SUPPORTED_PLATFORMS}")
        platforms_to_crawl = [p for p in selected if p in SUPPORTED_PLATFORMS]

    if not platforms_to_crawl:
        print("Tidak ada platform valid yang dipilih untuk crawling.")
        sys.exit(1)

    # Direktori output
    base_dir = Path(__file__).resolve().parent
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = base_dir / "data" / target_index

    out_dir.mkdir(parents=True, exist_ok=True)

    summary_list = []
    total_start = time.time()

    for p in platforms_to_crawl:
        try:
            summary = crawl_platform_data(
                scanner=scanner,
                platform=p,
                output_dir=out_dir / p,
                limit=args.limit,
                batch_size=args.batch_size,
                output_format=args.format,
                index_name=target_index
            )
            summary_list.append(summary)
        except KeyboardInterrupt:
            print("\n⚠️ Crawling dihentikan oleh pengguna.")
            break
        except Exception as e:
            print(f"⚠️ Melewati platform {p} karena error: {e}")
            summary_list.append({
                "platform": p,
                "total_docs": 0,
                "duration_sec": 0,
                "file_size_mb": 0,
                "file_path": "ERROR"
            })

    total_time = time.time() - total_start

    # Cetak Rangkuman Akhir
    print("\n" + "="*70)
    print(f"📊 RANGKUMAN CRAWLING DATA ({target_index})")
    print("="*70)
    print(f"{'Platform':<12} | {'Total Docs':<12} | {'Ukuran (MB)':<12} | {'Waktu (s)':<10} | {'Status'}")
    print("-"*70)
    grand_total_docs = 0
    for s in summary_list:
        grand_total_docs += s["total_docs"]
        status = "✅ OK" if s["total_docs"] > 0 else ("⚠️ 0 Dokumen" if s["file_path"] != "ERROR" else "❌ Error")
        print(f"{s['platform']:<12} | {s['total_docs']:<12,d} | {s['file_size_mb']:<12.2f} | {s['duration_sec']:<10.2f} | {status}")
    print("-"*70)
    print(f"{'TOTAL':<12} | {grand_total_docs:<12,d} | {'':<12} | {total_time:<10.2f} detik")
    print("="*70)
    print(f"📁 Semua file tersimpan di: {out_dir}\n")


if __name__ == "__main__":
    main()
