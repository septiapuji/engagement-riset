# 📊 Perbandingan Engagement Score (V1, V2, V3) Tingkat Postingan

Dataset lengkap 596 postingan dari 6 platform (Facebook, Twitter/X, Instagram, TikTok, YouTube, Threads) telah diekstraksi dan dihitung skor engagement-nya menggunakan tiga metode:
1. **V1 (IDF Basic)**: Invers bobot frekuensi standar
2. **V2 (Smoothed IDF)**: Bobot invers ter-smoothing ($\alpha=1.0$)
3. **V3 (PAI)**: Public Acceptance Index komposit (L0–L6) skala 0–100

File dataset CSV lengkap tersimpan di:
👉 `d:\SPECTRA\Riset_enggagement\perbandingan_engagements_all_platforms.csv`

---

## 📋 Struktur Kolom / Schema Dataset

| Nama Kolom | Tipe | Deskripsi |
| :--- | :--- | :--- |
| `post_id` | String | Identifier unik postingan di platform |
| `link_post` | String | URL / tautan langsung ke postingan |
| `isi_post` | String | Cuplikan teks / caption / judul postingan |
| `akun` | String | Username / nama channel / author postingan |
| `platform` | String | Nama platform (`twitter`, `instagram`, `tiktok`, `youtube`, `threads`, `facebook`) |
| `likes` | Integer | Jumlah like / reaksi positif |
| `reply` | Integer | Jumlah komentar / reply |
| `shares` | Integer | Jumlah share / bagikan |
| `retweet_repost` | Integer | Jumlah retweet (Twitter) / repost (Threads/IG) |
| `views_play_count` | Integer | Jumlah tayangan video / view count / impressions |
| `quote` | Integer | Jumlah quote tweet / quote post |
| `saves` | Integer | Jumlah bookmark / simpan / favorit |
| **`engagement_score_v1`** | Float | **Skor Engagement Metode V1 (IDF Basic)** |
| **`engagement_score_v2`** | Float | **Skor Engagement Metode V2 (Smoothed IDF)** |
| **`engagement_score_v3_pai`** | Float | **Skor Engagement Metode V3 (PAI, Skala 0–100)** |

---

## 🔍 Sampel Komparasi Postingan per Platform

### 1. Twitter / X
| Post ID & Link | Akun & Isi Post | Faktor Raw Engagement | V1 (IDF Basic) | V2 (Smoothed IDF) | V3 (PAI 0–100) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `2081654509244465370`<br>[Link Post](https://x.com/detikcom/status/2081654509244465370) | **@detikcom**<br>_Kampung yang hilang kembali terlihat saat air Bendungan Karian, Kabupaten Lebak, menyusut..._ | Likes: 67<br>Reply: 3<br>Retweet: 18<br>Views: 37.756 | **37.781,73** | **19,18** | **5,75** |
| `2080956415569793519`<br>[Link Post](https://x.com/i/status/2080956415569793519) | **Twitter User**<br>_Anggun, harimau putih yang menjadi ikon Semarang Zoo, mati setelah dipindahkan..._ | Likes: 2.873<br>Reply: 100<br>Retweet: 888<br>Views: 148.905 | **150.024,37** | **927,39** | **16,41** |
| `2081514758776476140`<br>[Link Post](https://x.com/detikcom/status/2081514758776476140) | **@detikcom**<br>_Viral video seorang wanita di Medan dianiaya oleh mantan pacarnya di dalam kamar kos..._ | Likes: 1.001<br>Reply: 85<br>Retweet: 211<br>Views: 125.762 | **126.138,40** | **244,48** | **11,82** |

> 💡 **Analisis Twitter**:
> * **V1** sangat didominasi oleh `views` (125k – 150k), sehingga skor V1 mencerminkan jumlah penonton daripada interaksi.
> * **V2** fokus pada interaksi aktif (`retweet` berbobot 1.0 dan `reply` berbobot 0.3939). Post dengan 888 retweet melonjak ke skor **927,39**.
> * **V3 (PAI)** menormalisasi seluruh rasio interaksi per-impression menghasilkan skor standar **11 – 16**.

---

### 2. Instagram
| Post ID & Link | Akun & Isi Post | Faktor Raw Engagement | V1 (IDF Basic) | V2 (Smoothed IDF) | V3 (PAI 0–100) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `3945335906368748139`<br>[Link Post](https://www.instagram.com/p/DbAphqCs_pr/) | **@detikcom**<br>_Meisya Siregar mengungkapkan suaminya, Bebi Romeo, mengalami tekanan batin..._ | Likes: 15.121<br>Reply: 299<br>Views: 1.700.212 | **15.121,00** | **7.710,00** | **9,94** |
| `3945114193244628114`<br>[Link Post](https://www.instagram.com/p/Da_3HTmsqSS/) | **@detikcom**<br>_Presiden Amerika Serikat Donald Trump turut menjadi sorotan di final Piala..._ | Likes: 42.638<br>Reply: 1.313<br>Views: 1.127.417 | **42.638,00** | **21.975,50** | **11,07** |
| `3944648782048970716`<br>[Link Post](https://www.instagram.com/p/Da-PGuQsyfc/) | **@detikcom**<br>_Polisi menangkap pria berinisial A (32) yang membunuh wanita di sebuah hotel..._ | Likes: 9.873<br>Reply: 420<br>Views: 852.190 | **9.873,00** | **5.146,50** | **9,15** |

---

### 3. TikTok
| Post ID & Link | Akun & Isi Post | Faktor Raw Engagement | V1 (IDF Basic) | V2 (Smoothed IDF) | V3 (PAI 0–100) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `v14025g50000d9iprb7og65j6chl3iq0`<br>[Link Post](https://www.tiktok.com/@kumparan/video/v14025g50000d9iprb7og65j6chl3iq0) | **@kumparan**<br>_Warga Desa Kembang Kuning, Jatiluhur, Purwakarta, digegerkan penemuan jasad..._ | Likes: 21.855<br>Reply: 535<br>Shares: 401<br>Views: 633.316 | **645.070,72** | **164.026,75** | **13,41** |
| `v14044g50000d9kspffog65jss982id0`<br>[Link Post](https://www.tiktok.com/@kompascom/video/v14044g50000d9kspffog65jss982id0) | **@kompascom**<br>_Istri satpam Perum Jasa Tirta II Sumarna, Siti Maryam, mengenang pertemuan..._ | Likes: 43.292<br>Reply: 1.085<br>Shares: 518<br>Views: 830.851 | **854.076,12** | **218.936,50** | **12,04** |

---

### 4. Threads
| Post ID & Link | Akun & Isi Post | Faktor Raw Engagement | V1 (IDF Basic) | V2 (Smoothed IDF) | V3 (PAI 0–100) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `3950303349140834269`<br>[Link Post](https://www.threads.net/@willie27_/post/DbSS_dok0fd) | **@willie27_**<br>_Terima kasih atas sambutan hangatnya, Pesantren Dalwa. ❤️ MasyaAllah..._ | Likes: 1.608<br>Reply: 58<br>Repost: 27<br>Quote: 1<br>Shares: 30 | **1.664,77** | **13,23** | **9,75** |
| `3949549035124304142`<br>[Link Post](https://www.threads.net/@willie27_/post/DbPnev9kikO) | **@willie27_**<br>_MAAF YA 😜..._ | Likes: 326<br>Reply: 105<br>Repost: 11<br>Quote: 4<br>Shares: 7 | **390,88** | **6,68** | **7,64** |

---

### 5. YouTube
| Post ID & Link | Akun & Isi Post | Faktor Raw Engagement | V1 (IDF Basic) | V2 (Smoothed IDF) | V3 (PAI 0–100) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `026961c1469f31aff...`<br>[Link Post](https://www.youtube.com/watch?v=026961c1469f31aff5094ab41ce8c8cf) | **Deddy Corbuzier**<br>_KALAU GUE SUDAH BEGINI, INI SUDAH FATAL‼️ - RUBEN ONSU_ | Likes: 144.722<br>Reply: 0<br>Views: 4.361.354 | **4.462.543,62** | **0,00** | **17,89** |
| `bqLZAKUfOSM`<br>[Link Post](https://www.youtube.com/watch?v=bqLZAKUfOSM) | **Canção & Louvor**<br>_Canção e Louvor - Ah, Eu Vou Falar..._ | Likes: 109.797<br>Reply: 0<br>Views: 8.584.085 | **8.660.855,06** | **0,00** | **8,81** |

---

### 6. Facebook
| Post ID & Link | Akun & Isi Post | Faktor Raw Engagement | V1 (IDF Basic) | V2 (Smoothed IDF) | V3 (PAI 0–100) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `1602123338172838`<br>[Link Post](https://www.facebook.com/reel/1352748830305406/) | **Atta Halilintar**<br>_Cobain tahu yang viral di Bandung🤤🤤..._ | Likes: 0<br>Reply: 0<br>Shares: 0<br>Views: 0 | **0,00** | **0,00** | **2,24** |
| `1700084251473729`<br>[Link Post](https://www.facebook.com/reel/2133351523934139/) | **Raffi Ahmad**<br>_Rafathar 🥊🥊🥊..._ | Likes: 0<br>Reply: 0<br>Shares: 0<br>Views: 0 | **0,00** | **0,00** | **-0,62** |
