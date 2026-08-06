# Pipeline Crawling & Engagement Score Engine (V1 & V2)

Sistem pengolahan data media sosial dari Elasticsearch (`.env`) yang dilengkapi dengan:
1. **Crawler Elasticsearch Scan/Scroll API (`sort: ["_doc"]`)**: Default **1.000 data per platform** (`twitter`, `instagram`, `tiktok`, `youtube`, `threads`, `facebook`).
2. **Data Merger Engine (`data_merger.py`)**: Standarisasi dan penggabungan dataset lintas platform menjadi satu master dataset (`parquet`, `jsonl`, `csv`).
3. **Engagement Calculation Engine (`engagement_engine.py`)**: Implementasi kalkulasi **Engagement Score V1 (Mba Ocim)** dan **V2 (New Invers Weight with Add-α Smoothing)** sesuai dokumen riset `dokumentasi_perhitungan/`.
4. **All-in-one Pipeline (`run_pipeline.py`)**: Menjalankan crawl, merge, dan scoring dalam satu perintah.

---

## 🛠️ Konfigurasi (`.env`)

File `.env` di `pengolahan_data/.env`:
```env
# ==========================================
# Access Elastic 51 AI 
# ==========================================
DB_HOST=192.168.180.190
DB_PORT=5200
# DB_USER=ingest_ai
# DB_PASSWORD=1ngest4i2o23
index = smm-data-hot-20260804
```

---

## 🚀 Cara Menjalankan

### 1. Menjalankan Seluruh Pipeline (Crawl 1000/Platform + Merge + Hitung Skor)
```bash
python run_pipeline.py
```
> *Secara default mengambil 1.000 data per platform, menggabungkan data, menghitung skor V1 & V2, dan mencetak laporan tabel bobot & statistik.*

Opsi tambahan pada pipeline:
```bash
# Ganti batas data (misal 500 data per platform)
python run_pipeline.py --limit 500

# Ganti konstanta smoothing alpha V2 (default: 1.0)
python run_pipeline.py --alpha 0.5

# Hitung skor dari data lokal tanpa crawl ulang
python run_pipeline.py --skip-crawl
```

---

### 2. Crawling Data Saja (`get_data.py`)
```bash
# Crawl 1.000 data untuk semua platform (default: limit 1000)
python get_data.py

# Hanya platform Twitter (1.000 data)
python get_data.py -p twitter

# Format output parquet / csv / jsonl
python get_data.py -p all -f parquet
```

---

### 3. Menggabungkan Data Saja (`data_merger.py`)
```bash
python data_merger.py
```
*Menggabungkan data terbaru dari tiap folder platform di `data/<index>/` menjadi `merged_all_platforms.parquet`.*

---

## 📐 Formula Perhitungan (Berdasarkan `dokumentasi_perhitungan/`)

### 1. Invers Weight V1 (Mba Ocim)
$$IDF_f = \log_2\left(\frac{N_f}{DF}\right)$$
- **$N_f$**: Rata-rata kemunculan faktor per hari = $\frac{\text{Total Faktor } f}{\text{Timeframe (Hari)}}$
- **$DF$**: Total post keseluruhan dalam timeframe
- **$\text{Score V1}$**: $\sum (\text{nilai\_faktor} \times \text{bobot\_faktor})$

### 2. Invers Weight V2 (New dengan Smoothing & Granularitas Platform)
$$IDF_{p,f} = \log_2 \left( \frac{N_p + \alpha}{DF_{p,f} + \alpha} \right)$$
- **$N_p$**: Total post di platform $p$
- **$DF_{p,f}$**: Jumlah post di platform $p$ yang memiliki nilai engagement faktor $f > 0$
- **$\alpha$**: Konstanta smoothing untuk mencegah division-by-zero / $\log(0)$ (default: `1.0`)
- **$\text{Score V2}$**: $\sum (\text{nilai\_faktor} \times \text{bobot\_faktor}_{p,f})$

---

## 📁 Struktur File Output

File hasil eksekusi disimpan di `pengolahan_data/data/<index>/`:
```
data/smm-data-hot-20260804/
├── twitter/
│   └── twitter_...jsonl          (1.000 data Twitter)
├── instagram/
│   └── instagram_...jsonl        (1.000 data Instagram)
├── tiktok/
│   └── tiktok_...jsonl           (1.000 data TikTok)
├── youtube/
│   └── youtube_...jsonl          (1.000 data YouTube)
├── threads/
│   └── threads_...jsonl          (1.000 data Threads)
├── facebook/
│   └── facebook_...jsonl         (1.000 data Facebook)
│
├── merged_all_platforms.parquet  (Master 6.000 data gabungan terstandarisasi)
├── dataset_with_engagement_scores.parquet / .jsonl / .csv (Dataset lengkap + kolom skor V1 & V2)
└── engagement_weights_summary.json (Metadata bobot IDF & statistik mean/max per platform)
```
