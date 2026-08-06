# Dokumen Metodologi Penelitian: Public Acceptance Index (PAI)
**Pengukuran Penerimaan Publik terhadap Narasi/Konten Lintas Platform Media Sosial**  
*Disusun untuk Keperluan Social Intelligence / Cognitive Warfare Analytics*  
*Tanggal: 5 Agustus 2026*

---

## 1. Latar Belakang dan Tujuan

Pengukuran engagement konvensional (*likes, views, comments*) tidak lagi memadai untuk menilai apakah sebuah narasi benar-benar diterima oleh publik. Metrik permukaan (*vanity metrics*) rentan dimanipulasi melalui *buzzer*, *bot*, dan pembelian *engagement*, sehingga tidak dapat dijadikan dasar pengambilan keputusan strategis—baik untuk keperluan kebijakan publik, manajemen reputasi, maupun deteksi dini potensi krisis narasi.

**Public Acceptance Index (PAI)** dirancang sebagai indeks komposit yang mengukur penerimaan publik terhadap suatu narasi atau konten dari perspektif pihak ketiga (bukan pemilik akun/konten), bekerja lintas platform, dan memperhitungkan kualitas interaksi—bukan sekadar volumenya.

### 1.1 Prinsip Desain
1. **Behavior over vanity metrics** — Perilaku pengguna (*menyimpan, membagikan, memberi stance*) lebih bernilai daripada sekadar jumlah *like*.
2. **Layered, tidak flatten engagement** — Setiap jenis interaksi dipetakan ke lapisan (*layer*) fungsional yang berbeda.
3. **Cross-platform normalized** — Skor dapat dibandingkan antarplatform meski struktur metrik berbeda.
4. **Bot & network aware** — Skor disesuaikan dengan probabilitas *bot* dan kualitas jaringan penyebar.
5. **Narrative-aware (stance-based)** — Mengukur arah dukungan (*support/oppose*), bukan hanya intensitas.

---

## 2. Arsitektur Sistem

Secara umum, pipeline PAI terdiri atas lima tahap utama:
1. **Data Ingestion**: Ingesti data mentah dari berbagai platform media sosial.
2. **Metric Mapping**: Pemetaan metrik ke skema kanonik lintas platform.
3. **Signal Processing**: Filtering *bot*, penanganan *outlier*, dan peluruhan waktu (*time decay*).
4. **Dimension Scoring (L0–L6)**: Penilaian per-dimensi berdasarkan fungsi matematis tertentu.
5. **Composite Index & Insight Layer**: Agregasi menjadi skor komposit PAI (0–100) yang menghasilkan lapisan *insight* (*early warning*, dominasi narasi, dan *risk flag*).

```
Data Ingestion 
     │
     ▼
Metric Mapping (Canonical Schema)
     │
     ▼
Signal Processing [Bot Filtering | Outlier Handling | Time Decay]
     │
     ▼
Dimension Scoring (L0–L6)
     │
     ▼
Composite Index (PAI Score 0–100)
     │
     ▼
Insight Layer [Early Warning | Narrative Dominance | Risk Flag]
```

---

## 3. Model Lapisan (Layer Model L0–L6)

Inti dari PAI adalah model berlapis yang memisahkan jenis interaksi berdasarkan intensitas komitmen kognitif pengguna—dari sekadar terpapar (*Exposure*) hingga bertindak nyata (*Action*). Pemisahan ini penting karena satu metrik tunggal (mis. *views*) tidak dapat merepresentasikan seluruh spektrum penerimaan.

| Layer | Nama | Tujuan | Contoh Metrik |
| :--- | :--- | :--- | :--- |
| **L0** | Exposure | Paparan | `impressions`, `reach` |
| **L1** | Attention | Perhatian | `watch_time`, `dwell_time`, `completion_rate` |
| **L2** | Reaction | Afinitas awal | `like`, `reaction` |
| **L3** | Retention | Nilai & niat simpan | `save`, `bookmark`, `follow` |
| **L4** | Amplification | Penyebaran | `share`, `repost`, `forward` |
| **L5** | Advocacy | Dukungan naratif | `stance: support / oppose` |
| **L6** | Action | Tindakan nyata | `click`, `join`, `event` |

> **Interpretasi Strategis:** L0–L2 mencerminkan jangkauan dan minat awal; L3–L4 mencerminkan nilai yang diberikan pengguna terhadap konten (*worth keeping/sharing*); sedangkan L5–L6 adalah lapisan paling kritis karena mengukur arah sikap (*stance*) dan konversi menjadi tindakan nyata—dua hal yang paling sulit dimanipulasi secara masif dan paling relevan untuk kesimpulan intelijen.

---

## 4. Ketersediaan Metrik Lintas Platform

Tantangan utama normalisasi lintas platform adalah bahwa tidak semua metrik kanonik tersedia secara *native* di setiap platform. 

**Notasi Ketersediaan:**
* ✅ : Tersedia sebagai fitur/metrik utama
* ◐ : Tersedia bersyarat (akun bisnis/kreator atau API tertentu)
* ❌ : Tidak tersedia atau bukan fitur *native*

### 4.1 Matriks Ketersediaan Metrik Utama

| Metrik | Instagram | Facebook | X | TikTok | YouTube | LinkedIn | Reddit | Threads | Telegram |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Impressions** | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ❌ | ◐ | ❌ |
| **Reach** | ✅ | ✅ | ❌ | ◐ | ❌ | ✅ | ❌ | ◐ | ❌ |
| **Views** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Watch Time** | ◐ | ◐ | ❌ | ✅ | ✅ | ◐ | ❌ | ❌ | ❌ |
| **Completion Rate** | ❌ | ◐ | ❌ | ✅ | ✅ | ◐ | ❌ | ❌ | ❌ |
| **Likes / Reactions**| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Comments** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ |
| **Shares / Reposts** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Saves / Bookmarks**| ✅ | ✅ | ✅ | Favorite | Playlist | ❌ | ✅ | ❌ | Saved Msg |
| **Follow / Subscribe**| ✅ | ✅ | ✅ | ✅ | Subscribe| Follow | Join | ✅ | Join Ch. |
| **Link Click** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ |
| **Community Join** | Broadcast | Group | Community | ❌ | Membership| Group | Subreddit | ❌ | Group/Ch. |

> **Implikasi Metodologis:** Karena tidak semua platform memiliki metrik yang sama (mis. Reddit dan Telegram tidak memiliki *impressions/reach native*), skema PAI harus mampu menoleransi *missing data* melalui **bobot dinamis (*reweighting*)**—bobot dimensi yang datanya tidak tersedia dialihkan secara proporsional ke dimensi lain yang tersedia pada platform tersebut, alih-alih mengasumsikan nilai nol yang akan bias menurunkan skor secara tidak adil.

### 4.2 Pemetaan Skema Kanonik (Contoh 4 Platform Utama)

| Skema Kanonik | Instagram | TikTok | X | YouTube |
| :--- | :--- | :--- | :--- | :--- |
| **impressions** | `impressions` | `views` | `impressions` | `impressions` |
| **attention** | `reel_watch_time` | `avg_watch_time` | – | `watch_time` |
| **reaction** | `like` | `like` | `like` | `like` |
| **retention** | `save` | `favorite` | `bookmark` | `subscribe` |
| **amplification** | `share` | `share` | `repost` | `share` |
| **advocacy** | `comment stance` | `comment` | `reply` | `comment` |
| **action** | `link_click` | `bio_click` | `url_click` | `link_click` |

---

## 5. Normalisasi Lintas Platform

Karena skala metrik antarplatform berbeda jauh (mis. views TikTok vs. Reddit), normalisasi bersifat wajib sebelum agregasi. PAI menggunakan tiga pendekatan yang dikombinasikan secara berbobot:

1. **Rate-based Normalization**  
   Mengubah nilai absolut menjadi rasio terhadap eksposur, agar konten dengan *reach* kecil tidak otomatis kalah dari konten viral.
   $$	ext{rate} = rac{	ext{metric}}{	ext{impressions}}$$

2. **Log Scaling**  
   Meredam bias dari lonjakan viral ekstrem agar tidak mendominasi skor komposit secara tidak proporsional.
   $$	ext{norm} = \log(1 + 	ext{metric})$$

3. **Min-Max Normalization (per Platform)**  
   Menyetarakan rentang nilai antarplatform berdasarkan distribusi historis platform tersebut.
   $$	ext{norm} = rac{x - 	ext{min}}{	ext{max} - 	ext{min}}$$

4. **Kombinasi Akhir**  
   $$	ext{normalized\_score} = 	ext{weighted}(	ext{rate}, 	ext{log\_scale}, 	ext{minmax})$$

---

## 6. Perhitungan Skor per Dimensi (Generik & Per Platform)

Setiap dimensi (L0–L6) dihitung dari kombinasi berbobot metrik ternormalisasi yang relevan.

### 6.1 Formulasi Generik Utama

* **Attention Score (L1)**
  $$	ext{Attention} = 0.4 	imes 	ext{completion\_rate} + 0.3 	imes 	ext{avg\_watch\_time\_norm} + 0.3 	imes 	ext{dwell\_time\_norm}$$
* **Retention Score (L3)**
  $$	ext{Retention} = 0.5 	imes 	ext{save\_rate} + 0.5 	imes 	ext{follow\_rate}$$
* **Amplification Score (L4)**
  $$	ext{Amplification} = 0.6 	imes 	ext{share\_rate} + 0.4 	imes 	ext{repost\_rate}$$
* **Advocacy Score (L5) — Dimensi Kritis**  
  Mengukur arah dukungan publik, bukan sekadar volume komentar. Membutuhkan klasifikasi *stance* (*support/oppose/netral*) via model NLP/Stance Classifier.
  $$	ext{Advocacy} = rac{	ext{positive\_comments} - 	ext{negative\_comments}}{	ext{total\_comments}} = 	ext{support\_ratio} - 	ext{oppose\_ratio}$$

---

### 6.2 Formula Spesifik Per Platform (Rincian Pra-Index)

*Notasi:* $E_p$ = Denominator Utama Platform (Eksposur Basis). $	ext{norm}(x)$ = Fungsi normalisasi gabungan (rate → log scaling → min-max).

#### A. Exposure (L0)
| Platform | Denominator ($E_p$) | Formula | Catatan / Fallback |
| :--- | :--- | :--- | :--- |
| **Instagram** | `impressions` | $	ext{norm}(\log(1 + 	ext{impressions}))$ | Fallback ke `reach` bila `impressions` tak tersedia |
| **Facebook** | `impressions` | $	ext{norm}(\log(1 + 	ext{impressions}))$ | — |
| **X** | `impressions` | $	ext{norm}(\log(1 + 	ext{impressions}))$ | — |
| **TikTok** | `views` | $	ext{norm}(\log(1 + 	ext{views}))$ | `views` dipakai sebagai default |
| **YouTube** | `impressions` | $	ext{norm}(\log(1 + 	ext{impressions}))$ | — |
| **LinkedIn** | `impressions` | $	ext{norm}(\log(1 + 	ext{impressions}))$ | — |
| **Reddit** | `views` | $	ext{norm}(\log(1 + 	ext{views}))$ | Tier-2 confidence (tidak ada `impressions/reach native`) |
| **Threads** | `impressions`* | $	ext{norm}(\log(1 + 	ext{impressions}))$ | Fallback ke `views` bila `impressions` tak tersedia |
| **Telegram** | `views` | $	ext{norm}(\log(1 + 	ext{views}))$ | Tier-2 confidence |

#### B. Attention (L1)
| Platform | Denominator ($E_p$) | Formula | Catatan / Fallback |
| :--- | :--- | :--- | :--- |
| **Instagram** | `impressions` | $0.4 \cdot 	ext{completion\_rate} + 0.3 \cdot 	ext{norm}(	ext{avg\_watch\_time}) + 0.3 \cdot 	ext{norm}(	ext{dwell\_time})$ | Hanya berlaku untuk Reel/Story |
| **Facebook** | `impressions` | $0.4 \cdot 	ext{completion\_rate} + 0.3 \cdot 	ext{norm}(	ext{avg\_watch\_time}) + 0.3 \cdot 	ext{norm}(	ext{dwell\_time})$ | Video only |
| **X** | `impressions` | $0.5 \cdot 	ext{norm}(	ext{reply\_rate}) + 0.5 \cdot 	ext{norm}(	ext{engagement\_depth})$ | Formula tereduksi (tanpa watch-time) |
| **TikTok** | `views` | $0.4 \cdot 	ext{completion\_rate} + 0.3 \cdot 	ext{norm}(	ext{avg\_watch\_time}) + 0.3 \cdot 	ext{norm}(	ext{dwell\_time})$ | Formula penuh |
| **YouTube** | `impressions` | $0.4 \cdot 	ext{completion\_rate} + 0.3 \cdot 	ext{norm}(	ext{avg\_watch\_time}) + 0.3 \cdot 	ext{norm}(	ext{dwell\_time})$ | completion_rate = Audience Retention |
| **LinkedIn** | `impressions` | $0.5 \cdot 	ext{norm}(	ext{avg\_watch\_time}) + 0.5 \cdot 	ext{norm}(	ext{profile\_visit\_rate})$ | Dwell disubstitusi `profile_visit_rate` |
| **Reddit** | `views` | $0.5 \cdot 	ext{norm}(	ext{reply\_rate}) + 0.5 \cdot 	ext{norm}(	ext{engagement\_depth})$ | Formula tereduksi |
| **Threads** | `impressions`* | $0.5 \cdot 	ext{norm}(	ext{reply\_rate}) + 0.5 \cdot 	ext{norm}(	ext{engagement\_depth})$ | Formula tereduksi |
| **Telegram** | `views` | $0.5 \cdot 	ext{norm}(	ext{reply\_rate}) + 0.5 \cdot 	ext{norm}(	ext{engagement\_depth})$ | Formula tereduksi |

> *Catatan Formula Tereduksi:*  
> $	ext{reply\_rate} = rac{	ext{replies}}{E_p}$  
> $	ext{engagement\_depth} = rac{	ext{comments} + 	ext{saves}}{E_p}$

#### C. Reaction (L2)
| Platform | Denominator ($E_p$) | Formula | Catatan / Fallback |
| :--- | :--- | :--- | :--- |
| **Instagram** | `impressions` | $	ext{norm}\left(rac{	ext{likes}}{E_p}ight)$ | — |
| **Facebook** | `impressions` | $	ext{norm}\left(rac{	ext{likes} + 	ext{reactions\_multi}}{E_p}ight)$ | Reactions multi-tipe dijumlahkan |
| **X** | `impressions` | $	ext{norm}\left(rac{	ext{likes}}{E_p}ight)$ | — |
| **TikTok** | `views` | $	ext{norm}\left(rac{	ext{likes}}{E_p}ight)$ | — |
| **YouTube** | `impressions` | $	ext{norm}\left(rac{	ext{likes}}{E_p}ight)$ | — |
| **LinkedIn** | `impressions` | $	ext{norm}\left(rac{	ext{likes} + 	ext{reactions\_multi}}{E_p}ight)$ | — |
| **Reddit** | `views` | $	ext{norm}(	ext{comment\_rate})$ [proxy] | Reddit native memakai upvote/karma |
| **Threads** | `impressions`* | $	ext{norm}\left(rac{	ext{likes}}{E_p}ight)$ | — |
| **Telegram** | `views` | $	ext{norm}\left(rac{	ext{reactions}}{E_p}ight)$ | — |

#### D. Retention (L3)
| Platform | Denominator ($E_p$) | Formula | Catatan / Fallback |
| :--- | :--- | :--- | :--- |
| **Instagram** | `impressions` | $0.5 \cdot \left(rac{	ext{saves}}{E_p}ight) + 0.5 \cdot \left(rac{	ext{follows}}{E_p}ight)$ | — |
| **Facebook** | `impressions` | $0.5 \cdot \left(rac{	ext{saves}}{E_p}ight) + 0.5 \cdot \left(rac{	ext{follows}}{E_p}ight)$ | — |
| **X** | `impressions` | $0.5 \cdot \left(rac{	ext{bookmarks}}{E_p}ight) + 0.5 \cdot \left(rac{	ext{follows}}{E_p}ight)$ | 'Saves' = Bookmarks |
| **TikTok** | `views` | $0.5 \cdot \left(rac{	ext{favorites}}{E_p}ight) + 0.5 \cdot \left(rac{	ext{follows}}{E_p}ight)$ | 'Saves' = Favorites |
| **YouTube** | `impressions` | $0.5 \cdot \left(rac{	ext{playlist\_adds}}{E_p}ight) + 0.5 \cdot \left(rac{	ext{subscribes}}{E_p}ight)$ | 'Saves' = Playlist Add |
| **LinkedIn** | `impressions` | $rac{	ext{follows}}{E_p}$ (bobot 100%) | Tidak ada `save` → reweighting ke `follow` |
| **Reddit** | `views` | $0.5 \cdot \left(rac{	ext{saves}}{E_p}ight) + 0.5 \cdot \left(rac{	ext{joins}}{E_p}ight)$ | 'Follow' = Join subreddit |
| **Threads** | `impressions`* | $rac{	ext{follows}}{E_p}$ (bobot 100%) | Tidak ada `save` → reweighting ke `follow` |
| **Telegram** | `views` | $0.5 \cdot \left(rac{	ext{saved\_message}}{E_p}ight) + 0.5 \cdot \left(rac{	ext{channel\_joins}}{E_p}ight)$ | — |

#### E. Amplification (L4)
| Platform | Denominator ($E_p$) | Formula | Catatan / Fallback |
| :--- | :--- | :--- | :--- |
| **Instagram** | `impressions` | $rac{	ext{shares}}{E_p}$ (bobot 100%) | Bobot repost direalokasi ke share |
| **Facebook** | `impressions` | $rac{	ext{shares}}{E_p}$ (bobot 100%) | Sama seperti Instagram |
| **X** | `impressions` | $0.6 \cdot \left(rac{	ext{reposts}}{E_p}ight) + 0.4 \cdot \left(rac{	ext{quote\_posts}}{E_p}ight)$ | Formula penuh berlaku |
| **TikTok** | `views` | $rac{	ext{shares}}{E_p}$ (bobot 100%) | — |
| **YouTube** | `impressions` | $rac{	ext{norm}(	ext{link\_clicks} + 	ext{subscribe\_delta})}{E_p}$ [proxy] ⚠ | Confidence rendah |
| **LinkedIn** | `impressions` | $0.6 \cdot \left(rac{	ext{shares}}{E_p}ight) + 0.4 \cdot \left(rac{	ext{reposts}}{E_p}ight)$ | — |
| **Reddit** | `views` | $	ext{cross\_post\_rate}$ [proxy] ⚠ | Jika tak tertelusur, dimensi di-reweight |
| **Threads** | `impressions`* | $rac{	ext{reposts}}{E_p}$ (bobot 100%) | — |
| **Telegram** | `views` | $rac{	ext{forwards}}{E_p}$ (bobot 100%) | 'Share' = Forward |

#### F. Advocacy (L5)
| Platform | Denominator ($E_p$) | Formula | Catatan / Fallback |
| :--- | :--- | :--- | :--- |
| **Instagram** | `comments` | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Stance classifier pada comments |
| **Facebook** | `comments` | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Stance classifier pada comments |
| **X** | `replies` | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Wajib lolos Bot Adjustment dulu |
| **TikTok** | `comments` | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Stance classifier pada comments |
| **YouTube** | `comments` | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Stance classifier pada comments |
| **LinkedIn** | `comments` | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Classifier butuh tuning domain B2B |
| **Reddit** | `comments` | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Gunakan top-level comments |
| **Threads** | `replies` | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Stance classifier pada replies |
| **Telegram** | `replies`* | $	ext{support\_ratio} - 	ext{oppose\_ratio}$ | Bersyarat (tergantung opsi channel) |

> *Aturan Sampling Advocacy:* Minimum sample size disarankan $\ge 30$ komentar/balasan per konten sebelum skor advocacy dianggap valid/reliabel secara statistik.

#### G. Action (L6)
| Platform | Denominator ($E_p$) | Formula | Catatan / Fallback |
| :--- | :--- | :--- | :--- |
| **Instagram** | `impressions` | $rac{	ext{link\_click}}{E_p}$ | — |
| **Facebook** | `impressions` | $rac{	ext{link\_click}}{E_p}$ | — |
| **X** | `impressions` | $rac{	ext{url\_click}}{E_p}$ | — |
| **TikTok** | `views` | $rac{	ext{bio\_click}}{E_p}$ | — |
| **YouTube** | `impressions` | $rac{	ext{link\_click}}{E_p}$ | — |
| **LinkedIn** | `impressions` | $rac{	ext{link\_click}}{E_p}$ | — |
| **Reddit** | `views` | $rac{	ext{link\_click}}{E_p}$ | — |
| **Threads** | `impressions`* | $rac{	ext{link\_click}}{E_p}$ | Confidence rendah |
| **Telegram** | `views` | $rac{	ext{link\_click}}{E_p}$ | — |

---

## 7. Skor Komposit PAI (0–100)

Skor akhir merupakan agregasi berbobot dari ketujuh dimensi. Bobot berikut merupakan *baseline* yang dapat dikalibrasi ulang sesuai konteks domain (mis. isu politik vs. kampanye kesehatan publik).

### 7.1 Distribusi Bobot Baseline

| Dimensi | Bobot | Rasional |
| :--- | :---: | :--- |
| **Exposure (L0)** | **10%** | Prasyarat, bukan indikator penerimaan langsung |
| **Attention (L1)** | **20%** | Menyaring paparan pasif dari keterlibatan nyata |
| **Reaction (L2)** | **15%** | Sinyal afinitas awal, rentan manipulasi bot |
| **Retention (L3)** | **15%** | Niat menyimpan/mengikuti = nilai jangka menengah |
| **Amplification (L4)** | **20%** | Indikator penyebaran, perlu dicek *network/bot* |
| **Advocacy (L5)** | **15%** | Dimensi paling kritis: arah *stance* publik |
| **Action (L6)** | **5%** | Konversi nyata, bobot kecil karena jarang tersedia |

$$	ext{PAI} = (0.10 	imes L_0) + (0.20 	imes L_1) + (0.15 	imes L_2) + (0.15 	imes L_3) + (0.20 	imes L_4) + (0.15 	imes L_5) + (0.05 	imes L_6)$$

$$	ext{PAI}_{	ext{final}} = 	ext{PAI} 	imes 100$$

### 7.2 Interpretasi Skala Evaluasi

```
 0           30          50          70          85         100
 ├───────────┼───────────┼───────────┼───────────┼───────────┤
 │ Rejected  │   Weak    │ Moderate  │  Strong   │ Dominant  │
```

* **0–30 (Rejected)**: Narasi ditolak atau tidak beresonansi dengan publik.
* **30–50 (Weak Acceptance)**: Penerimaan lemah, potensi butuh reformulasi pesan.
* **50–70 (Moderate)**: Penerimaan cukup, perlu pemantauan tren.
* **70–85 (Strong)**: Penerimaan kuat, layak dijadikan referensi *framing*.
* **85–100 (Dominant Narrative)**: Narasi dominan, berpotensi membentuk opini publik secara luas.

### 7.3 Aturan Reweighting Lintas Dimensi

Ketika sebuah dimensi tidak dapat dihitung sama sekali pada suatu platform (mis. Amplification pada Reddit jika *cross-post* tak tertelusur), bobot dimensi tersebut direalokasikan secara proporsional ke dimensi lain yang tersedia:

$$w_{i,	ext{adjusted}} = rac{w_{i,	ext{original}}}{\sum w_{	ext{tersedia}}}$$

*Contoh Kasus:* Jika Reddit kehilangan dimensi Amplification (bobot asli 0.20), total bobot tersisa adalah 0.80. Bobot baru untuk Advocacy menjadi:
$$w_{	ext{Advocacy, adjusted}} = rac{0.15}{0.80} = 0.1875$$

> **Persyaratan UI/UX:** Setiap kali *reweighting* diterapkan, dashboard wajib menampilkan *flag* **"Adjusted Weighting"** pada skor platform tersebut.

---

## 8. Lapisan Penyesuaian (Wajib Konteks Intelijen)

Skor mentah tanpa penyesuaian rawan bias oleh manipulasi buatan (*bot*, *buzzer*) dan oleh basis pengikut/jaringan yang tidak setara pengaruhnya.

1. **Bot Adjustment**  
   Skor diturunkan proporsional terhadap estimasi probabilitas keterlibatan *bot* (pola waktu posting, umur akun, rasio follower/following).
   $$	ext{Score}_{	ext{adjusted}} = 	ext{Score} 	imes (1 - 	ext{bot\_probability})$$

2. **Network Weighting**  
   Skor disesuaikan berdasarkan kualitas jaringan penyebar (*follower quality*, sentralitas dalam graf sosial, dan status akun terverifikasi/elite node).
   $$	ext{Score}_{	ext{adjusted}} = 	ext{Score} 	imes 	ext{influence\_weight}$$

3. **Time Decay**  
   Peluruhan eksponensial mencegah konten lama mendominasi skor agregat secara permanen.
   $$	ext{decay} = e^{-\lambda \cdot 	ext{time}}$$

---

## 9. Logika Peringatan Dini (Early Warning Logic)

Kombinasi tertentu antar-dimensi menghasilkan pola anomali yang bernilai sebagai sinyal peringatan dini, terlepas dari skor PAI absolut:

| Pola Sinyal | Kombinasi Metrik | Interpretasi Strategis |
| :--- | :--- | :--- |
| **False Virality** | Exposure tinggi + Advocacy rendah | Berpotensi kontroversi / *backlash*; viralitas tidak mencerminkan dukungan. |
| **Silent Build-Up** | Engagement rendah + Retention tinggi | Narasi 'tidur' yang berpotensi meledak kemudian (*sleeper narrative*). |
| **Coordinated Push**| Amplifikasi tinggi + Attention rendah | Indikasi jaringan *bot* / *buzzer* terkoordinasi. |

---

## 10. Rancangan Output & Dashboard

### 10.1 Komponen Visual Utama
1. **PAI Score (Headline)**: Skor komposit 0–100 dengan kategori kualitatif.
2. **Layer Breakdown**: Dekomposisi per dimensi untuk mengidentifikasi lapisan mana yang lemah.
3. **Narrative Signal**: Proporsi *support* vs. *oppose* dari klasifikasi *stance*.
4. **Amplification Map**: Visualisasi klaster akun/jaringan yang menyebarkan narasi.

### 10.2 Skema Data Output (JSON Schema)

```json
{
  "content_id": "123",
  "platform": "tiktok",
  "metrics": {
    "impressions": 100000,
    "watch_time": 50000,
    "likes": 4000,
    "shares": 1200,
    "comments": 800,
    "saves": 900
  },
  "derived": {
    "attention_score": 0.72,
    "retention_score": 0.65,
    "amplification_score": 0.80,
    "advocacy_score": 0.60
  },
  "pai_score": 74.2
}
```

---

## 11. Keterbatasan dan Asumsi

1. **Ketimpangan Ketersediaan Data**: Platform seperti Reddit dan Telegram tidak menyediakan *impressions/reach native*, sehingga skor Exposure pada platform tersebut bersifat estimasi atau proxy.
2. **Ketergantungan pada Model NLP**: Akurasi dimensi Advocacy bergantung penuh pada kualitas model *stance classification*; bias model akan menular langsung ke skor akhir.
3. **Kontekstualitas Bobot**: Bobot komposit bersifat *baseline* dan perlu dikalibrasi ulang per domain isu (politik, kesehatan, komersial).
4. **Deteksi Bot Probabilistik**: `bot_probability` adalah estimasi; *false positive/negative* tetap mungkin terjadi, terutama pada *bot* generasi baru (*AI-driven*).
5. **Kebutuhan Time-Series**: Skor *snapshot* satu titik waktu tidak menggantikan analisis tren; *early warning logic* membutuhkan data *time-series*.

---

## 12. Klasifikasi Tingkat Kepercayaan Data (Tiering)

| Tier | Deskripsi | Platform |
| :---: | :--- | :--- |
| **Tier-1** | Data terlengkap; seluruh 7 dimensi tersedia dengan field *native* / *near-native*. | **TikTok, YouTube** |
| **Tier-2** | Mayoritas tersedia, 1–2 dimensi menggunakan proxy. | **Instagram, Facebook, LinkedIn, X** |
| **Tier-3** | Exposure & Amplification mayoritas *proxy*, confidence lebih rendah. | **Reddit, Telegram, Threads** |

> **Rekomendasi:** Cantumkan *tier* ini sebagai metadata pada setiap skor PAI yang dipublikasikan, agar pembaca laporan memahami perbedaan tingkat kepercayaan antarplatform.

---

## 13. Rekomendasi Pengembangan Lanjutan

1. **Narrative Graph**: Pemetaan aktor-ke-narasi untuk mengidentifikasi node kunci dan pola koordinasi.
2. **Cross-Platform Propagation Tracking**: Melacak perpindahan narasi antarplatform (mis. TikTok → X → Telegram) untuk memahami jalur eskalasi.
3. **Actor Weighting**: Membedakan bobot pengaruh akun elite/berpengaruh dari akun biasa dalam perhitungan Amplification dan Advocacy.
4. **Geo-Segmentation**: Memecah skor PAI berdasarkan wilayah geografis untuk pemetaan risiko spesifik lokasi.
5. **Perluasan Ontologi Metrik**: Pengembangan *Social Media Metric Ontology* yang lebih komprehensif (estimasi 180–250 metrik) melingkupi platform tambahan seperti Discord, Bluesky, dll.

---

## 14. Kesimpulan

**Public Acceptance Index (PAI)** menawarkan pendekatan yang jauh lebih valid secara metodologis dibandingkan *engagement metrics* konvensional karena:
1. Berbasis perilaku berlapis (*L0–L6*), bukan sekadar volume mentah.
2. Menyetarakan metrik melalui normalisasi lintas platform.
3. Memperhitungkan manipulasi buatan melalui *bot adjustment* dan *network weighting*.
4. Siap digunakan untuk analisis intelijen (*cognitive warfare & social intelligence*).

Langkah konkrit berikutnya adalah menurunkan spesifikasi metodologi ini ke dalam *query* implementasi database (SQL/Elasticsearch), desain *dashboard map-centric*, atau integrasi langsung dengan *Political Risk Index*.
