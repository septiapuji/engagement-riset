import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Set UTF-8 untuk stdout & stderr di Windows Terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import SUPPORTED_PLATFORMS, load_env_config
from data_merger import merge_platform_data
from engagement_engine import EngagementEngine, generate_engagement_report
from es_scanner import ElasticsearchScanner
from get_data import crawl_platform_data


def run_full_pipeline(
    limit: int = 1000,
    batch_size: int = 1000,
    alpha: float = 1.0,
    platforms = None,
    output_dir = None,
    index_name = None,
    skip_crawl = False
):
    """
    Menjalankan seluruh alur kerja terpadu:
    1. Crawl data (1000 per platform) dari ES berdasarkan .env
    2. Gabung data (Merge) ke master dataset
    3. Hitung Engagement Score V1 & V2 berdasarkan dokumentasi riset
    4. Simpan output akhir & buat laporan statistik
    """
    config = load_env_config()
    target_index = index_name or config["index"]
    target_platforms = platforms or SUPPORTED_PLATFORMS

    base_dir = Path(__file__).resolve().parent
    data_root = Path(output_dir) if output_dir else (base_dir / "data" / target_index)
    data_root.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*75)
    print("🚀 PIPELINE OTOMATIS: CRAWL 1000 DATA + GABUNG DATA + ENGAGEMENT SCORE")
    print("="*75)
    print(f"  • Elasticsearch Host : {config['base_url']}")
    print(f"  • Index Target       : {target_index}")
    print(f"  • Limit per Platform : {limit:,} post")
    print(f"  • Platform List      : {', '.join(target_platforms)}")
    print(f"  • Alpha Smoothing V2 : {alpha}")
    print("="*75)

    # 1. CRAWLING DATA DARI ES
    if not skip_crawl:
        scanner = ElasticsearchScanner(
            host=config["host"],
            port=config["port"],
            index=target_index,
            user=config["user"],
            password=config["password"]
        )

        if not scanner.ping():
            print("❌ Gagal terhubung ke Elasticsearch server!", file=sys.stderr)
            sys.exit(1)

        print("\n[STEP 1/3] 📥 Mengambil data 1000 per platform dari Elasticsearch...")
        for p in target_platforms:
            try:
                crawl_platform_data(
                    scanner=scanner,
                    platform=p,
                    output_dir=data_root / p,
                    limit=limit,
                    batch_size=batch_size,
                    output_format="jsonl",
                    index_name=target_index
                )
            except Exception as e:
                print(f"⚠️ Melewati crawling platform {p}: {e}")
    else:
        print("\n[STEP 1/3] ⏩ Skip crawling data (menggunakan data yang sudah ada).")

    # 2. GABUNG DATA (MERGE ENGINE)
    print("\n[STEP 2/3] 🧩 Menggabungkan dan menstandarisasi data dari semua platform...")
    df_merged = merge_platform_data(
        data_dir=data_root,
        platforms=target_platforms,
        output_filepath=data_root / "merged_all_platforms",
        export_formats=["parquet", "jsonl", "csv"]
    )

    if df_merged.empty:
        print("❌ Data gabungan kosong. Pipeline dihentikan.", file=sys.stderr)
        return

    # 3. HITUNG ENGAGEMENT SCORE V1 & V2
    print("\n[STEP 3/3] 🧮 Menghitung Engagement Score V1 (Mba Ocim) & V2 (New Invers Weight)...")
    engine = EngagementEngine(alpha=alpha)
    df_scored, summary = engine.calculate_scores(df_merged)

    # Simpan Dataset Hasil Akhir dengan Skor
    scored_base = data_root / "dataset_with_engagement_scores"
    df_scored.to_parquet(scored_base.with_suffix(".parquet"), index=False)
    df_scored.to_json(scored_base.with_suffix(".jsonl"), orient="records", lines=True, force_ascii=False, date_format="iso")
    df_scored.to_csv(scored_base.with_suffix(".csv"), index=False, encoding="utf-8")

    # Simpan Ringkasan Bobot ke JSON
    summary_file = data_root / "engagement_weights_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        # Bersihkan float non-serializable jika ada
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Cetak Laporan Lengkap
    report_text = generate_engagement_report(df_scored, summary)
    print("\n" + report_text)

    print("\n🎉 PIPELINE SELESAI!")
    print(f"📁 File dataset lengkap tersimpan di: {scored_base}.parquet / .jsonl / .csv")
    print(f"📑 File bobot & ringkasan di: {summary_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline komprehensif crawling 1000 data per platform, penggabungan, dan perhitungan engagement score V1 & V2."
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=1000,
        help="Batas data per platform (default: 1000)"
    )
    parser.add_argument(
        "-b", "--batch-size",
        type=int,
        default=1000,
        help="Ukuran batch scan ES (default: 1000)"
    )
    parser.add_argument(
        "-a", "--alpha",
        type=float,
        default=1.0,
        help="Konstanta smoothing alpha V2 (default: 1.0)"
    )
    parser.add_argument(
        "-p", "--platform",
        type=str,
        default="all",
        help="Platform target (default: all)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help="Direktori output"
    )
    parser.add_argument(
        "-i", "--index",
        type=str,
        default=None,
        help="Override nama index dari .env"
    )
    parser.add_argument(
        "--skip-crawl",
        action="store_true",
        help="Lewati proses crawling, langsung lakukan merge & hitung skor dari data lokal"
    )

    args = parser.parse_args()

    platforms = None
    if args.platform.lower() != "all":
        platforms = [p.strip().lower() for p in args.platform.split(",") if p.strip()]

    run_full_pipeline(
        limit=args.limit,
        batch_size=args.batch_size,
        alpha=args.alpha,
        platforms=platforms,
        output_dir=args.output_dir,
        index_name=args.index,
        skip_crawl=args.skip_crawl
    )


if __name__ == "__main__":
    main()
