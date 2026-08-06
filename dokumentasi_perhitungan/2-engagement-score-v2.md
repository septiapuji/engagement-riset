# Engagement Score V2 — Invers Weight (New)

## Formula

$$IDF_{p,f} = \log_2 \left( \frac{N_p + \alpha}{DF_{p,f} + \alpha} \right)$$

| Variabel | Definisi |
|---|---|
| **N_p** | Total post di platform *p* = jumlah seluruh postingan dalam 1 platform, untuk 1 isu, pada timeframe yang sama |
| **DF_{p,f}** | Document frequency versi engagement = jumlah postingan di platform *p* yang memiliki nilai engagement pada faktor *f* > 0 |
| **α (alpha)** | Konstanta smoothing untuk menghindari division-by-zero / log(0) |

$$DF_{p,f} = \left| \{ post \in p \mid engagement_f(post) > 0 \} \right|$$

## Faktor per Platform

| Platform | Faktor |
|---|---|
| Facebook | Shares, Likes, Reply |
| Twitter | Shares, Views, Reply, Likes, Retweet |
| Instagram | Shares, Reply, Likes, Repost|
| TikTok | Shares, Views, Reply, Likes |
| YouTube | Shares, Views, Reply/Comment, Likes+Dislikes |
| Threads | Shares, Reply, Repost, Quote, Likes |

## Engagement Score

$$\text{Engagement Score} = \sum (\text{nilai\_faktor} \times \text{bobot\_faktor})$$

---

## Alur Proses V2

```
1. Get data dari Elasticsearch
   -> post + raw engagement per platform

   [Jalur harian - ringan]
2. Update counter incremental
   -> N_p dan DF_p,f di-update harian, bukan full rescan

3. Sliding window bucket
   -> tambah bucket hari baru, buang bucket paling lama

   [Jalur batch - berat, terjadwal mingguan/bulanan]
4. Hitung IDF dengan smoothing
   -> log2((N_p + alpha) / (DF_p,f + alpha))

5. Simpan ke cache
   -> tabel bobot_faktor[platform][faktor]

   [Jalur harian - ringan, kembali]
6. Lookup bobot dari cache
   -> tanpa hitung ulang IDF

7. Engagement score
   -> sum(nilai_faktor x bobot_faktor)

8. Skor tersimpan
```

**Karakteristik alur V2**: dipecah menjadi dua kecepatan berbeda.
- **Jalur harian (ringan)**: update counter incremental + lookup cache — murah, bisa jalan tiap hari tanpa membebani pipeline.
- **Jalur batch (berat)**: hitung ulang IDF dengan smoothing — hanya jalan berkala (mingguan/bulanan), dijadwalkan di luar jam sibuk.

## Perbaikan dari V1

- **Smoothing dengan α** mencegah error division-by-zero / log(0).
- **Definisi DF lebih presisi**: dihitung berdasarkan jumlah post yang benar-benar memiliki engagement pada faktor tersebut (bukan sekadar total post).
- **Diindeks per-platform (p) dan per-faktor (f)**, sehingga perhitungan tidak lagi tercampur skalanya antar platform/faktor seperti di V1.
- **Cakupan faktor lebih kaya**: menambahkan Shares di Instagram, Views di Twitter & YouTube yang sebelumnya tidak ada di V1.
- **Pipeline lebih efisien**: proses berat (rekalkulasi IDF) dipisah dari proses harian, sehingga tidak perlu full recompute setiap hari.

---

## Sumber / Landasan Metode

Struktur formula V2 mengikuti pendekatan **smoothed IDF (add-α smoothing)** yang lazim dipakai untuk mengatasi kelemahan formula IDF dasar (division-by-zero, log(0)) di literatur information retrieval modern:

1. **Scikit-learn — TfidfVectorizer / TfidfTransformer documentation**. Mendefinisikan smoothed IDF sebagai penambahan konstanta pada numerator dan denominator untuk mencegah division-by-zero: *"Smooth idf weights by adding one to document frequencies, as if an extra document was seen containing every term in the collection exactly once, which prevents zero divisions."* Formula: `idf(t) = log[(1+n)/(1+df(t))] + 1`.
   https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

2. **Melanie Walsh — Introduction to Cultural Analytics & Python, "TF-IDF with Scikit-Learn"**. Menjelaskan mekanisme smoothing sebagai penambahan dokumen "semu" yang mengandung setiap term satu kali, sehingga menstabilkan formula saat DF kecil atau nol.
   https://melaniewalsh.github.io/Intro-Cultural-Analytics/05-Text-Analysis/03-TF-IDF-Scikit-Learn.html

3. **ml4devs.com — Term Frequency-Inverse Document Frequency**. Merangkum varian smoothing IDF secara umum: *"Smoothing: To avoid division by zero (if df(t)=0) and to prevent the IDF score from becoming zero for terms appearing in all documents, smoothing is typically applied."*
   https://www.ml4devs.com/what-is/tf-idf/

4. Konsep dasar IDF yang menjadi fondasi (sebelum smoothing ditambahkan) tetap merujuk pada:
   **Spärck Jones, K. (1972)**. *A statistical interpretation of term specificity and its application in retrieval*. Journal of Documentation, 28, 11-21.
   https://www.staff.city.ac.uk/~sbrp622/idf.html

**Catatan penerapan pada V2**: Konstanta α di formula V2 memainkan peran yang sama dengan konstanta smoothing "+1" pada scikit-learn — bedanya, V2 memakai α sebagai parameter yang bisa disesuaikan (bukan tetap 1), sehingga besarnya efek smoothing bisa dikalibrasi terhadap skala rata-rata N_p pada masing-masing platform.

---

## Riset Terbaru: Dampak Engagement-Based Ranking di Platform Sosmed

Sama seperti V1, formula V2 pada dasarnya menghasilkan bobot yang bisa dipakai untuk sistem *ranking* berbasis sinyal engagement — pola yang sudah dipakai luas oleh platform sosmed dan menjadi objek kajian riset-riset terbaru berikut:

1. **Value Alignment of Social Media Ranking Algorithms** (2025). Mencatat bahwa <cite index="23-1">dibandingkan feed kronologis, feed berbasis engagement terbukti meningkatkan retensi pengguna</cite>, tetapi <cite index="23-1">fokus semata pada sinyal engagement berisiko menimbulkan marjinalisasi perspektif tertentu, penyebaran misinformasi, polarisasi politik, dan promosi konten ekstremis</cite>.
   https://arxiv.org/html/2509.14434v1

2. **Ranking for Engagement: How Social Media Algorithms Fuel Misinformation and Polarization** (ScienceDirect, 2026). Riset ini menunjukkan trade-off langsung: menaikkan bobot pada sinyal engagement <cite index="20-1">meningkatkan engagement secara keseluruhan, tapi juga memperkuat visibilitas konten ekstrem, sehingga distribusi konten yang dilihat dan diklik pengguna menjadi semakin bimodal/terpolarisasi</cite>.
   https://www.sciencedirect.com/science/article/pii/S0047272726000253

3. **The Prosocial Ranking Challenge** (2026). Eksperimen lapangan pada 9.386 pengguna Facebook, Reddit, dan X/Twitter menemukan bahwa mengganti algoritma ranking standar (berbasis engagement) dengan ranking alternatif <cite index="24-1">menurunkan indeks polarisasi afektif dan waktu penggunaan aktif di Facebook & Reddit, meski waktu aktif di X/Twitter justru naik</cite>.
   https://arxiv.org/pdf/2603.19626

### Relevansi untuk V2

Perbaikan teknis di V2 (smoothing, presisi DF, granularitas per-platform) membuat perhitungan bobot lebih stabil dan akurat secara statistik, tapi **tidak secara otomatis mengatasi risiko sosial** yang disebutkan riset di atas — karena keduanya (V1 dan V2) tetap murni berbasis frekuensi/statistik kemunculan faktor engagement, bukan kualitas atau konteks konten. Jika hasil engagement score ini nantinya dipakai untuk keperluan *ranking/sorting* konten ke pengguna (bukan sekadar pelaporan analitik), disarankan untuk mempertimbangkan lapisan tambahan (misalnya, faktor kualitas konten atau kontrol distribusi) di luar formula IDF ini, sebagaimana dibahas riset "Prosocial Ranking" di atas.
