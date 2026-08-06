# Engagement Score V1 — Invers Weight (Mba Ocim)

## Formula

$$IDF = \log_2 \frac{N}{DF}$$

| Variabel | Definisi |
|---|---|
| **N** | Rata-rata masing-masing faktor per hari = Jumlah Likes, Comment, atau Shares / TimeFrame (day) |
| **DF** | Document Frequency, diasumsikan sebagai banyaknya post dalam setiap TimeFrame = Total Post |

## Faktor per Platform

| Platform | Faktor |
|---|---|
| Facebook | Jumlah Likes, Comment, Shares |
| Twitter | Jumlah Likes, Reply, dan Retweet |
| Instagram | Jumlah Likes dan Reply |
| TikTok | Jumlah Likes, Shares, Comment, Play Count |
| YouTube | Jumlah Likes+Dislikes, Reply, View |
| Threads | Shares, Reply, Repost, Quote, Likes |

## Engagement Score

$$\text{Engagement Score} = \sum (\text{nilai\_faktor} \times \text{bobot\_faktor})$$

---

## Alur Proses V1

```
1. Get data dari Elasticsearch
   -> post + raw engagement per platform

2. Hitung N per faktor
   -> likes/comment/shares dibagi timeframe

3. Hitung DF
   -> total post dalam timeframe

4. Hitung IDF = log2(N/DF)
   -> tanpa smoothing, rawan log(0) / division by zero

5. Engagement score
   -> sum(nilai_faktor x bobot_faktor)

6. Skor tersimpan
```

**Karakteristik alur V1**: satu jalur linear, dihitung ulang penuh setiap kali dijalankan (full recompute). Cocok untuk data kecil, tapi berat jika dijalankan setiap hari pada volume data besar karena tidak ada pemisahan antara proses ringan (harian) dan proses berat (agregasi ulang).

## Keterbatasan V1

- Berisiko **division-by-zero atau log(0)** jika DF = 0 atau N = 0.
- **N** dihitung agregat per faktor, belum dipecah per-platform/per-isu, sehingga skala antar faktor bisa tidak sebanding.
- **DF** didefinisikan sebagai total post keseluruhan, bukan jumlah post yang benar-benar memiliki faktor tersebut — sedikit menyimpang dari makna DF asli di literatur information retrieval.
- Tidak ada pemisahan proses ringan vs berat, sehingga pipeline harian berpotensi mahal jika dijalankan sebagai full recompute.

---

## Sumber / Landasan Metode

Formula IDF yang dipakai di V1 (`log2(N/DF)`) adalah bentuk dasar **Inverse Document Frequency** yang pertama kali diperkenalkan dalam riset information retrieval:

1. **Spärck Jones, K. (1972)**. *A statistical interpretation of term specificity and its application in retrieval*. Journal of Documentation, 28, 11-21 (dicetak ulang 2004, Journal of Documentation 60, 493-502). Paper asli yang pertama kali mendefinisikan konsep term specificity yang kemudian dikenal sebagai IDF — dasar dari seluruh formula invers weight yang dipakai di dokumen ini.
   Referensi arsip: https://www.staff.city.ac.uk/~sbrp622/idf.html

2. **Salton, G. & Yang, C. S. (1973)**. Mengombinasikan Term Frequency (TF) dengan formula IDF milik Spärck Jones menjadi skema **TF-IDF** yang dikenal luas saat ini.

3. Bentuk formula `IDF = log2(N/DF)` yang identik dengan V1 juga didokumentasikan sebagai bentuk paling sederhana dari IDF pada referensi akademik:
   Springer Nature — *Inverse Document Frequency*: "In its simplest form, the IDF weight of a term is assigned as follows: IDF = log2(N/DF), where N is the number of documents in the collection, and DF is the document frequency of the term."
   https://link.springer.com/rwe/10.1007/978-1-4614-8265-9_933

4. Robertson, S. (2004). *Understanding inverse document frequency: on theoretical arguments for IDF*. Journal of Documentation 60, analisis teoritis lanjutan atas dasar matematis IDF, termasuk turunan ke skema BM25.
   https://www.staff.city.ac.uk/~sbrp622/idfpapers/Robertson_idf_JDoc.pdf

**Catatan**: V1 menggunakan bentuk IDF paling dasar tanpa smoothing — sama seperti formula tekstual awal Spärck Jones sebelum berbagai varian smoothing dikembangkan di literatur-literatur berikutnya (lihat dokumen V2 untuk pembahasan smoothing).

---

## Riset Terbaru: Dampak Engagement-Based Ranking di Platform Sosmed

Perhitungan engagement score seperti V1 pada dasarnya masuk kategori metode yang dipakai oleh **sistem ranking berbasis sinyal engagement** (likes, comment, shares, dst) yang umum dipakai platform sosmed. Beberapa riset terbaru relevan membahas dampaknya:

1. **Value Alignment of Social Media Ranking Algorithms** (2025). Merangkum bahwa hampir semua platform sosmed saat ini memakai sinyal engagement (klik, waktu tonton, jumlah komentar) untuk *feed ranking*, dan dibandingkan dengan feed kronologis, ranking berbasis engagement <cite index="23-1">meningkatkan retensi pengguna</cite>. Namun, riset ini juga mencatat bahwa <cite index="23-1">berfokus semata pada sinyal engagement dapat menimbulkan dampak sosial negatif, termasuk marjinalisasi perspektif tertentu, penyebaran misinformasi, polarisasi politik, dan promosi konten ekstremis</cite>.
   https://arxiv.org/html/2509.14434v1

2. **Ranking for Engagement: How Social Media Algorithms Fuel Misinformation and Polarization** (ScienceDirect, 2026). Riset ini memodelkan bagaimana platform yang menaikkan bobot pada sinyal engagement/highlight <cite index="20-1">meningkatkan engagement dengan mempromosikan konten yang lebih mudah disukai dan dibagikan, namun mekanisme yang sama memperkuat visibilitas konten ekstrem</cite>, karena pengguna dengan pandangan lebih ekstrem cenderung lebih sering menyorot konten yang selaras dengan pandangan mereka sendiri.
   https://www.sciencedirect.com/science/article/pii/S0047272726000253

3. **The Prosocial Ranking Challenge** (2026, eksperimen lapangan pada Facebook, Reddit, dan X/Twitter selama pemilu AS 2024). Studi field-experiment berskala besar (9.386 pengguna) yang menguji algoritma ranking alternatif dibanding ranking berbasis engagement standar, menemukan <cite index="24-1">algoritma alternatif mengurangi indeks polarisasi afektif rata-rata 0.03 standar deviasi, dengan penurunan waktu aktif di Facebook dan Reddit, namun justru peningkatan waktu aktif di X/Twitter</cite>.
   https://arxiv.org/pdf/2603.19626

### Relevansi untuk V1

Formula V1 (IDF sederhana tanpa smoothing) menghasilkan bobot yang murni statistik berdasarkan frekuensi kemunculan faktor, tanpa mempertimbangkan potensi bias amplifikasi konten ekstrem atau viral yang disebutkan riset di atas. Ini artinya, jika engagement score V1 dipakai untuk *ranking/sorting* konten (bukan sekadar pelaporan/analitik), penerapannya berisiko mengikuti pola yang sama dengan algoritma-algoritma yang dikritik di riset ini — cenderung mengutamakan konten dengan interaksi tinggi tanpa mempertimbangkan kualitas atau dampak sosial dari konten tersebut.
