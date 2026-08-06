# Dokumentasi Perhitungan Engagement Score: Invers Weight V1 & V2

## Latar Belakang

Kedua versi formula ini mengadaptasi konsep **IDF (Inverse Document Frequency)** dari information retrieval / TF-IDF ke konteks social media engagement. Prinsip dasarnya:

> Semakin sering suatu faktor engagement muncul, semakin kecil bobot yang diberikan. Asumsinya, semakin banyak kemunculan faktor berarti semakin mudah user memberikan faktor tersebut, sehingga faktor tersebut menjadi tidak sepenting faktor yang kemunculannya lebih sedikit.

---

## V1 — Invers Weight (Mba Ocim)

### Formula

$$IDF = \log_2 \frac{N}{DF}$$

### Definisi Variabel

| Variabel | Definisi |
|---|---|
| **N** | Rata-rata masing-masing faktor per hari = Jumlah Likes, Comment, atau Shares / TimeFrame (day) |
| **DF** | Document Frequency, diasumsikan sebagai banyaknya post dalam setiap TimeFrame = Total Post |

### Faktor per Platform

| Platform | Faktor |
|---|---|
| Facebook | Jumlah Likes, Comment, Shares |
| Twitter | Jumlah Likes, Reply, dan Retweet |
| Instagram | Jumlah Likes dan Reply |
| TikTok | Jumlah Likes, Shares, Comment, Play Count |
| YouTube | Jumlah Likes+Dislikes, Reply, View |
| Threads | Shares, Reply, Repost, Quote, Likes |

### Engagement Score

$$\text{Engagement Score} = \sum (\text{nilai\_faktor} \times \text{bobot\_faktor})$$

### Catatan/Keterbatasan

- Berisiko **division-by-zero atau log(0)** jika DF = 0 atau N = 0.
- **N** dihitung agregat per faktor, belum dipecah per-platform/per-isu, sehingga skala antar faktor bisa tidak sebanding.
- **DF** didefinisikan sebagai total post keseluruhan, bukan jumlah post yang benar-benar memiliki faktor tersebut — sedikit menyimpang dari makna DF asli di TF-IDF.

---

## V2 — Invers Weight (New)

### Formula

$$IDF_{p,f} = \log_2 \left( \frac{N_p + \alpha}{DF_{p,f} + \alpha} \right)$$

### Definisi Variabel

| Variabel | Definisi |
|---|---|
| **N_p** | Total post di platform *p* = jumlah seluruh postingan dalam 1 platform, untuk 1 isu, pada timeframe yang sama |
| **DF_{p,f}** | Document frequency versi engagement = jumlah postingan di platform *p* yang memiliki nilai engagement pada faktor *f* > 0 |
| **α (alpha)** | Konstanta smoothing untuk menghindari division-by-zero / log(0) |

$$DF_{p,f} = \left| \{ post \in p \mid engagement_f(post) > 0 \} \right|$$

### Faktor per Platform

| Platform | Faktor |
|---|---|
| Facebook | Shares, Likes, Reply |
| Twitter | Shares, Views, Reply, Likes, Retweet |
| Instagram | Shares, Reply, Likes |
| TikTok | Shares, Views, Reply, Likes |
| YouTube | Shares, Views, Reply, Likes+Dislikes |
| Threads | Shares, Reply, Repost, Quote, Likes |

### Engagement Score

$$\text{Engagement Score} = \sum (\text{nilai\_faktor} \times \text{bobot\_faktor})$$

### Perbaikan dari V1

- **Smoothing dengan α** mencegah error division-by-zero / log(0).
- **Definisi DF lebih presisi**: dihitung berdasarkan jumlah post yang benar-benar memiliki engagement pada faktor tersebut (bukan sekadar total post), sesuai konsep DF asli di TF-IDF.
- **Diindeks per-platform (p) dan per-faktor (f)**, sehingga perhitungan tidak lagi tercampur skalanya antar platform/faktor seperti di V1.
- **Cakupan faktor lebih kaya**: menambahkan Shares di Instagram, Views di Twitter & YouTube yang sebelumnya tidak ada di V1.

---

## Perbandingan V1 vs V2

| Aspek | V1 | V2 |
|---|---|---|
| Smoothing | Tidak ada | Ada (+α) |
| Risiko log(0) / div-0 | Tinggi | Rendah / teratasi |
| Definisi DF | Total post (kurang presisi) | Post dengan engagement > 0 (presisi) |
| Granularitas | Global (belum per-platform/faktor) | Per-platform & per-faktor (p, f) |
| Konsistensi skala antar faktor | Rentan bias | Lebih terkontrol |
| Faktor Instagram | Likes, Reply | + Shares |
| Faktor Twitter | Likes, Reply, Retweet | + Views |
| Faktor YouTube | Likes+Dislikes, Reply, View | + Shares |

---

## Rekomendasi Lanjutan

1. **Pemilihan nilai α** perlu dijustifikasi secara empiris — nilai α=1 (Laplace smoothing klasik) atau α kecil (0.1–0.5) tergantung skala rata-rata N_p. Jika N_p besar, pengaruh α relatif kecil; jika N_p kecil, α besar bisa mendominasi hasil.
2. Perlu **validasi/clamping** agar IDF tidak bernilai negatif — meskipun jarang terjadi, kasus DF_{p,f} + α > N_p + α perlu diantisipasi.
3. **Normalisasi nilai_faktor** (misalnya dengan log-scale atau min-max scaling) sebelum dikalikan bobot IDF, agar faktor dengan angka mentah besar (misalnya Views) tidak otomatis mendominasi Engagement Score meskipun bobot IDF-nya kecil.
