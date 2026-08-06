# 📐 Ringkasan Rumus Akhir — V1, V2 & V3

> Dokumen ini merangkum rumus akhir (final formula) dari **tiga metodologi engagement scoring** yang telah diuji pada dataset 6 platform media sosial (Facebook, Twitter/X, Instagram, TikTok, YouTube, Threads) dengan masing-masing N=100 post.

---

## 1. V1 — IDF Basic

### Formula Dasar

$$IDF = \log_2 \left( \frac{N}{DF} \right)$$

| Variabel | Definisi |
|:---|:---|
| **N** | Rata-rata total nilai faktor per timeframe (≈ `sum(faktor)` untuk 1 hari) |
| **DF** | Jumlah total post dalam timeframe |

**Normalisasi**: Min-Max ke rentang `[0, 1]`

**Skor Akhir**:

$$\text{Engagement Score}_{V1} = \sum (\text{nilai\_faktor} \times \text{IDF\_norm\_faktor})$$

### Rumus Akhir per Platform (V1)

| Platform | Rumus |
|:---|:---|
| **Facebook** | `ES = likes × 0.3333 + comment × 0.3333 + shares × 0.3333` |
| **Twitter/X** | `ES = likes × 0.3469 + reply × 0.0000 + retweet × 0.1382` |
| **Instagram** | `ES = likes × 1.0000 + reply × 0.0000` |
| **TikTok** | `ES = likes × 0.5339 + shares × 0.2153 + comment × 0.0000 + play_count × 1.0000` |
| **YouTube** | `ES = likes × 0.6992 + reply × 0.0000 + views × 1.0000` |
| **Threads** | `ES = likes × 1.0000 + reply × 0.5400 + repost × 0.4773 + quote × 0.0000 + shares × 0.4186` |

> [!WARNING]
> **Kelemahan V1**: Rawan `division-by-zero` / `log(0)` jika `DF = 0` atau `N = 0`. Pada dataset ini, Facebook menghasilkan skor 0 karena seluruh metrik dari raw data bernilai 0.

---

## 2. V2 — Smoothed IDF (α-Smoothing)

### Formula Dasar

$$IDF_{p,f} = \log_2 \left( \frac{N_p + \alpha}{DF_{p,f} + \alpha} \right)$$

| Variabel | Definisi |
|:---|:---|
| **N_p** | Total post di platform *p* |
| **DF_{p,f}** | Jumlah post di platform *p* yang memiliki engagement faktor *f* > 0 |
| **α** | Konstanta smoothing (default = `1.0`) |

**Normalisasi**: Min-Max ke rentang `[0, 1]`

**Skor Akhir**:

$$\text{Engagement Score}_{V2} = \sum (\text{nilai\_faktor} \times \text{IDF}_{p,f\_{norm}})$$

### Rumus Akhir per Platform (V2)

#### Facebook
| Faktor | DF > 0 | IDF Raw | IDF Norm |
|:---|---:|---:|---:|
| likes | 0 / 100 | 6.6582 | 0.3333 |
| comment | 0 / 100 | 6.6582 | 0.3333 |
| shares | 0 / 100 | 6.6582 | 0.3333 |

`ES = likes × 0.3333 + comment × 0.3333 + shares × 0.3333`

#### Twitter / X
| Faktor | DF > 0 | IDF Raw | IDF Norm |
|:---|---:|---:|---:|
| likes | 100 / 100 | 0.0000 | 0.0000 |
| reply | 98 / 100 | 0.0289 | 0.3939 |
| retweet | 95 / 100 | 0.0732 | **1.0000** |
| views | 100 / 100 | 0.0000 | 0.0000 |

`ES = likes × 0.0000 + reply × 0.3939 + retweet × 1.0000 + views × 0.0000`

#### Instagram
| Faktor | DF > 0 | IDF Raw | IDF Norm |
|:---|---:|---:|---:|
| likes | 100 / 100 | 0.0000 | 0.5000 |
| reply | 100 / 100 | 0.0000 | 0.5000 |
| shares | 0 / 100 | — | — |
| repost | 0 / 100 | — | — |

`ES = likes × 0.5000 + reply × 0.5000`

#### TikTok
| Faktor | DF > 0 | IDF Raw | IDF Norm |
|:---|---:|---:|---:|
| likes | 100 / 100 | 0.0000 | 0.2500 |
| shares | 100 / 100 | 0.0000 | 0.2500 |
| comment | 100 / 100 | 0.0000 | 0.2500 |
| play_count | 100 / 100 | 0.0000 | 0.2500 |

`ES = likes × 0.2500 + shares × 0.2500 + comment × 0.2500 + play_count × 0.2500`

#### YouTube
| Faktor | DF > 0 | IDF Raw | IDF Norm |
|:---|---:|---:|---:|
| likes | 100 / 100 | 0.0000 | 0.0000 |
| reply | 0 / 100 | 6.6582 | **1.0000** |
| views | 100 / 100 | 0.0000 | 0.0000 |

`ES = likes × 0.0000 + reply × 1.0000 + views × 0.0000`

> [!IMPORTANT]
> **YouTube V2 = 0**: Karena `reply` di raw data seluruhnya bernilai 0, meskipun diberi bobot 1.0, skor akhir tetap 0. Di produksi, metrik yang tidak tersedia/selalu 0 harus dikeluarkan dari kalkulasi IDF.

#### Threads
| Faktor | DF > 0 | IDF Raw | IDF Norm |
|:---|---:|---:|---:|
| likes | 100 / 100 | 0.0000 | 0.0000 |
| reply | 99 / 100 | 0.0144 | 0.0191 |
| repost | 91 / 100 | 0.1346 | 0.1792 |
| quote | 59 / 100 | 0.7513 | **1.0000** |
| shares | 88 / 100 | 0.1825 | 0.2429 |

`ES = likes × 0.0000 + reply × 0.0191 + repost × 0.1792 + quote × 1.0000 + shares × 0.2429`

> [!TIP]
> **Keunggulan V2**: Smoothing α menjamin stabilitas numerik. Bobot otomatis memprioritaskan metrik yang *langka* (susah didapatkan) → mencerminkan **usaha audiens**, bukan sekadar paparan pasif.

---

## 3. V3 — Public Acceptance Index (PAI)

### Formula Dasar

$$\text{PAI} = \left( \sum_{i=0}^{6} w_i \times L_i \right) \times 100$$

### Bobot Layer

| Layer | Nama | Bobot | Metrik Utama |
|:---|:---|---:|:---|
| **L0** | Exposure | 10% | impressions, views |
| **L1** | Attention | 20% | watch_time, completion_rate (proxy: comment_rate) |
| **L2** | Reaction | 15% | likes, reactions |
| **L3** | Retention | 15% | saves, follows |
| **L4** | Amplification | 20% | shares, reposts |
| **L5** | Advocacy | 15% | support_ratio − oppose_ratio (NLP Stance Classifier) |
| **L6** | Action | 5% | link_clicks |

**Normalisasi per dimensi**: Min-Max ke `[0, 1]` sebelum agregasi.

### Rumus Dimensi per Platform (V3)

#### Facebook
| Layer | Formula |
|:---|:---|
| L0 | `norm(log(impressions))` |
| L2 | `norm(likes / impressions)` |
| L3 | `norm(saves / impressions)` |
| L4 | `norm(shares / impressions)` |
| L5 | `support_ratio − oppose_ratio` *(NLP)* |
| L6 | `norm(link_click / impressions)` |

#### Twitter / X
| Layer | Formula |
|:---|:---|
| L0 | `norm(log(impressions))` |
| L1 | `norm(reply_rate)` |
| L2 | `norm(likes / impressions)` |
| L3 | `norm(bookmarks / impressions)` |
| L4 | `0.6 × (reposts / imp) + 0.4 × (quotes / imp)` |
| L5 | `support_ratio − oppose_ratio` *(NLP)* |
| L6 | `norm(url_click / impressions)` |

#### Instagram
| Layer | Formula |
|:---|:---|
| L0 | `norm(log(impressions))` |
| L2 | `norm(likes / impressions)` |
| L3 | `0.5 × (saves / imp) + 0.5 × (follows / imp)` |
| L4 | `norm(shares / impressions)` |
| L5 | `support_ratio − oppose_ratio` *(NLP)* |
| L6 | `norm(link_click / impressions)` |

#### TikTok
| Layer | Formula |
|:---|:---|
| L0 | `norm(log(views))` |
| L1 | `0.4 × completion + 0.3 × norm(watch_time) + 0.3 × norm(dwell)` |
| L2 | `norm(likes / views)` |
| L3 | `0.5 × (favorites / views) + 0.5 × (follows / views)` |
| L4 | `norm(shares / views)` |
| L5 | `support_ratio − oppose_ratio` *(NLP)* |
| L6 | `norm(bio_click / views)` |

#### YouTube
| Layer | Formula |
|:---|:---|
| L0 | `norm(log(impressions))` |
| L1 | `0.4 × completion + 0.3 × norm(watch_time)` |
| L2 | `norm(likes / impressions)` |
| L3 | `0.5 × (playlist / imp) + 0.5 × (subscribe / imp)` |
| L4 | `norm((link_clicks + subscribe_delta) / impressions)` |
| L5 | `support_ratio − oppose_ratio` *(NLP)* |
| L6 | `norm(link_click / impressions)` |

#### Threads
| Layer | Formula |
|:---|:---|
| L0 | `norm(log(impressions))` |
| L1 | `0.5 × reply_rate + 0.5 × engagement_depth` |
| L2 | `norm(likes / impressions)` |
| L3 | `norm(follows / impressions)` |
| L4 | `norm(reposts / impressions)` |
| L5 | `support_ratio − oppose_ratio` *(NLP)* |
| L6 | `norm(link_click / impressions)` |

> [!NOTE]
> **L5 (Advocacy)** membutuhkan **NLP Stance Classifier** untuk menentukan rasio dukungan vs penolakan. Dalam riset ini, L5 disimulasikan dengan distribusi normal `N(0, 0.3)` yang di-clip ke `[-1, 1]`.

> [!CAUTION]
> **Banyak metrik PAI tidak tersedia di API publik** (seperti `watch_time`, `completion_rate`, `link_clicks`, `follows`). Di implementasi nyata, digunakan mekanisme *reweighting* otomatis: `w_adj = w_orig / Σ(w_available)` untuk mempertahankan proporsionalitas bobot saat metrik tertentu tidak tersedia.

---

## 4. Perbandingan Ringkas Ketiga Metode

| Aspek | V1 (IDF Basic) | V2 (Smoothed IDF) | V3 (PAI) |
|:---|:---|:---|:---|
| **Formula Inti** | `log₂(N/DF)` | `log₂((N+α)/(DF+α))` | `Σ(wᵢ × Lᵢ) × 100` |
| **Skala Skor** | Tidak terbatas | Tidak terbatas | 0 – 100 |
| **Stabilitas Numerik** | ❌ Rawan `log(0)` | ✅ Aman (smoothing α) | ✅ Aman (normalisasi) |
| **Adaptivitas Bobot** | ❌ Statis | ✅ Otomatis per platform | ⚠️ Manual (7 layer fixed) |
| **Cocok untuk Streaming** | ❌ | ✅ | ❌ (terlalu berat) |
| **Cocok untuk Batch** | ⚠️ | ✅ | ✅ |
| **Ketergantungan NLP** | ❌ | ❌ | ✅ (L5 = Stance) |
| **Latensi Eksekusi** | Rendah | **Sangat Rendah** | Tinggi |

> [!IMPORTANT]
> **Rekomendasi**: Gunakan **V2 (Smoothed IDF)** sebagai engine utama pipeline streaming real-time, dan **V3 (PAI)** untuk analisis batch / dashboard eksekutif yang membutuhkan insight mendalam per dimensi engagement.
