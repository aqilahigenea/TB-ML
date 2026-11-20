# Dokumen Konteks Project: Klasterisasi Puskesmas Berdasarkan Indikator Stunting

> **Tugas Besar Machine Learning — Kelompok 8, Universitas Andalas**  
> *Versi 2.0 (Disesuaikan dengan Model Terbaru — November 2026)*

---

> **Revisi Model v1.1 (Silhouette 0,268 → 0,502):** kelompok kini dibentuk dari **2 indikator inti** (Kasus per sasaran balita dan Persen berat tidak naik) dengan K-Means K=3 (titik awal pusat Ward). Kelima indikator tetap dipakai untuk Skor Urgensi, peringkat, dan profil kelompok. Hasil: Prioritas 1 = Beban Kasus Tinggi (5 puskesmas), Prioritas 2 = Pertumbuhan Mandek & Balita Sangat Pendek (8), Prioritas 3 = Pemantauan Rutin (11); Silhouette K=2/3/4 = 0,411/0,502/0,446; Davies-Bouldin 0,612; uji data acak p = 0,34 (tidak signifikan); bootstrap 23/24 Pasti (Pauh = Belum pasti). Angka dan tabel kelompok pada bagian 5-7 di bawah masih versi lama, dan ARI antarperiode harus dihitung ulang dengan menjalankan notebook.


## 1. Ringkasan Singkat

Project ini mengolah data stunting balita Kota Padang untuk membantu Dinas Kesehatan (Dinkes) Kota Padang menentukan wilayah puskesmas mana yang perlu didahulukan dalam alokasi intervensi dan sumber daya penanganan stunting.

> **Cerita Utama Proyek Ini (3 Kalimat):**
> 1. Data BNBA dibersihkan, lalu diringkas jadi 5 angka per puskesmas.
> 2. K-Means ($K=3$) mengelompokkan 24 puskesmas, lalu kelompok diberi nama prioritas.
> 3. Hasil diuji dengan 4 cara dan disimpulkan jujur: pola ada tapi lemah.

* **Judul Kerja:** Klasterisasi Puskesmas Berdasarkan Indikator Stunting Menggunakan K-Means sebagai Pendukung Penentuan Wilayah Prioritas Penanganan di Dinas Kesehatan Kota Padang.
* **Jenis Tugas:** *Unsupervised Learning* (klasterisasi wilayah dan pemeringkatan indeks urgensi), tanpa label kebenaran (*ground truth*), sehingga tidak memiliki metrik akurasi.
* **Pertanyaan Utama:** Puskesmas mana yang sebaiknya diprioritaskan Dinas Kesehatan, dan seperti apa profil permasalahan stunting di wilayah tersebut?
* **Pengguna Utama:** Dinas Kesehatan Kota Padang dan Kepala Puskesmas.
* **Arsitektur Luaran:**
  1. **Hasil Utama:** **Skor Urgensi Komposit (Indeks Urgensi)** per puskesmas (Peringkat 1 s.d. 24) yang dibagi ke dalam **3 Tingkat Urgensi Kebijakan** (Tingkat 1 - Urgensi Sangat Tinggi, Tingkat 2 - Urgensi Sedang, Tingkat 3 - Pemantauan Rutin).
  2. **Hasil Pembanding (*Profiling* Multi-dimensi):** Model K-Means ($K=3$) untuk memetakan karakteristik spesifik masalah (Tipe Keparahan Klinis Balita vs Tipe Beban Kasus Populasi).
  3. **Berkas Pendukung:** Model `.pkl`, metadata batasan `.json`, rekap Excel untuk aplikasi web, dan aplikasi web pendukung keputusan (*Decision Support System*).

---

## 2. Tim dan Pembagian Kerja

| Anggota Tim | Tahap Kerja | Tanggung Jawab Utama |
| :--- | :---: | :--- |
| **Dhyva Aulia Hendri** | Tahap 1 – 5 | *Problem definition*, pengumpulan data, EDA, pembersihan data (*preprocessing*), dan pembuatan fitur (*feature engineering*). |
| **Madani Fitri Nur Hidayati** | Tahap 6 – 9 & Validasi Tahap 10 | Pengujian pembagian data (*data splitting*), pemilihan algoritma, pelatihan model K-Means ($K=3$), *tuning* $K$, dan validasi ketahanan model. |
| **Aqila Higenea Taufik** | Visualisasi Tahap 10 & Tahap 11 – 12 | Visualisasi evaluasi, finalisasi model & ekspor, perancangan *deployment*, pemantauan (*monitoring*), dan integrasi web DSS. |

---

## 3. Latar Belakang dan Evolusi Topik

1. **Topik Awal Ditinggalkan:** Semula direncanakan klasifikasi risiko kehamilan dengan *Random Forest*. Dibatalkan karena label target dibentuk dari rumus skor deterministik, sehingga model hanya menebak ulang rumus buatan tersebut.
2. **Pergeseran dari Individu ke Wilayah:** Usulan berikutnya mengelompokkan 1.631 balita secara individual. Disesuaikan menjadi **tingkat puskesmas (wilayah)** karena protokol penanganan medis stunting per anak pada dasarnya seragam; keputusan strategis yang dapat dibedakan oleh Dinas Kesehatan adalah **alokasi prioritas wilayah mana yang didahulukan**.
3. **Agregasi Kecamatan:** Hasil puskesmas dirangkum ke dalam 11 kecamatan di Kota Padang untuk memenuhi arahan perbandingan wilayah manajerial.

---

## 4. Spesifikasi Data dan Indikator

### A. Karakteristik Data Mentah
* **Sumber Data:** Data sekunder e-PPGBM / BNBA (*By Name By Address*) Balita Stunting Kota Padang bulan Maret, April, dan Mei 2026, serta rekapitulasi data sasaran balita dan persentase Ibu Hamil KEK resmi dari Dinas Kesehatan Kota Padang.
* **Volume Baris:** 4.603 baris mentah $\rightarrow$ **4.471 baris valid** setelah pembersihan (mencakup 2.417 anak unik lintas bulan).
* **Cakupan Wilayah:** 24 puskesmas di 11 kecamatan (103 kelurahan).
* **Aturan Pembersihan Data (Tahap 4 - Tetap Lengkap):**
  * Konversi satuan berat gram ke kilogram (> 100 dibagi 1.000).
  * Pembersihan nilai mutlak Z-Score tidak wajar ($|Z| > 10$ atau kosong: 37 baris).
  * Pembersihan berat badan tidak masuk akal (> 35 kg).
  * Pembersihan usia tidak wajar ($0$ bulan/kosong: 91 baris; $> 60$ bulan: 33 baris).
  * Penghapusan duplikat pencatatan balita dalam satu bulan yang sama (2 baris).
  * Kunci identifikasi anak unik: `Nama + Tanggal Lahir` (NIK tidak digunakan karena banyak yang tidak valid atau kosong).

### B. Lima Indikator Utama (Nama Baru yang Mudah Dibaca)
Semua indikator dibaca: **makin tinggi nilainya = makin buruk kondisinya / makin butuh perhatian**.

| Nama Indikator | Cara Perhitungan | Arti dalam Satu Kalimat |
| :--- | :--- | :--- |
| **`Kasus per sasaran balita`** | $\frac{\text{Total Kasus Stunting Tercatat}}{\text{Sasaran Balita} \times \text{Jumlah Bulan}} \times 100\%$ | Banyaknya kasus stunting yang tercatat dibanding total sasaran balita (%). |
| **`Persen sangat pendek`** | $\frac{\text{Balita Sangat Pendek (TB/U)}}{\text{Total Kasus Tercatat}} \times 100\%$ | Proporsi balita berstatus sangat pendek di antara kasus tercatat (%). |
| **`Persen stunting + kurus`** | $\frac{\text{Balita Gizi Kurang/Buruk (BB/TB)}}{\text{Total Kasus Tercatat}} \times 100\%$ | Proporsi balita yang stunting sekaligus kurus / *wasting* (%). |
| **`Persen berat tidak naik`** | $\frac{\text{Balita dengan BB Tidak Naik (T)}}{\text{Total Kasus Tercatat}} \times 100\%$ | Proporsi balita yang pertumbuhannya mandek / berat badan tidak naik (%). |
| **`Persen bumil KEK`** | Angka rekap resmi Dinas Kesehatan | Persentase ibu hamil kurang energi kronis di wilayah puskesmas (%). |

> [!IMPORTANT]
> **Kejujuran Definisi "Kasus per Sasaran Balita":**  
> Pembilangnya adalah kasus yang tercatat di dokumen BNBA, bukan survei acak populasi. Oleh karena itu, fitur ini dinamai secara jujur sebagai **Kasus per sasaran balita (%)**, bukan "Prevalensi Sebenarnya". Pada puskesmas dengan cakupan penimbangan Posyandu ($D/S$) rendah, angka ini bisa tampak rendah karena pelaporan pasif (*under-reporting*), bukan karena wilayah tersebut bebas stunting.

---

## 5. Metode Pemodelan dan Keputusan Desain

1. **Pemilihan Model (Tahap 7):**
   * Tiga algoritma diuji pada $K=3$: K-Means, Hierarchical (Ward), dan GMM.
   * **Keputusan:** K-Means dipilih sebagai model acuan utama karena menghasilkan distribusi kelompok yang seimbang dan memiliki pusat kelompok (*centroid*) yang dapat diinterpretasikan secara langsung ke dalam angka riil untuk kebijakan Dinkes.
2. **Pemilihan Nilai $K$ (Tahap 9):**
   * Diuji pada $K=2, 3, 4$ dengan parameter $n\_init = 30$ (stabil 100% dan efisien waktu).
   * **Keputusan:** $K=3$ dipilih karena Dinas Kesehatan membutuhkan **tiga tingkat prioritas** kebijakan penanganan, dan nilai Silhouette pada rentang $K=2$ hingga $K=4$ berada pada tingkat yang hampir sama ($0{,}247 - 0{,}268$).
3. **Standarisasi Fitur:** Menggunakan `StandardScaler` (rata-rata $= 0$, simpangan baku $= 1$) sehingga kelima indikator memiliki bobot kontribusi yang adil di ruang berdimensi lima.

---

## 6. Hasil Pemodelan

### A. Hasil Utama: Tabel Pemeringkatan Indeks Urgensi (24 Puskesmas)
Setiap puskesmas dinilai berdasarkan **Skor Urgensi Komposit** (rata-rata *z-score* 5 indikator). Peringkat 1 sampai 24 dibagi ke dalam 3 Tingkat Urgensi Kebijakan:

| Peringkat | Puskesmas | Kecamatan | Tingkat Urgensi Kebijakan | Skor Urgensi | Status Kepastian | Kelompok Profil (K-Means) |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **1** | **ALAI** | PADANG UTARA | Tingkat 1 - Urgensi Sangat Tinggi | +1,16 | Pasti | Prioritas 1 (Krisis Klinis Balita) |
| **2** | **BUNGUS** | BUNGUS TELUK KABUNG | Tingkat 1 - Urgensi Sangat Tinggi | +0,92 | Pasti | Prioritas 1 (Krisis Klinis Balita) |
| **3** | **IKUR KOTO** | KOTO TANGAH | Tingkat 1 - Urgensi Sangat Tinggi | +0,62 | Pasti | Prioritas 2 (Beban Kasus Tinggi) |
| **4** | **NANGGALO** | NANGGALO | Tingkat 1 - Urgensi Sangat Tinggi | +0,62 | Pasti | Prioritas 1 (Krisis Klinis Balita) |
| **5** | **ANAK AIR** | KOTO TANGAH | Tingkat 1 - Urgensi Sangat Tinggi | +0,60 | Pasti | Prioritas 2 (Beban Kasus Tinggi) |
| **6** | **SEBERANG PADANG** | PADANG SELATAN | Tingkat 1 - Urgensi Sangat Tinggi | +0,52 | Pasti | Prioritas 2 (Beban Kasus Tinggi) |
| **7** | **AIR TAWAR** | PADANG UTARA | Tingkat 1 - Urgensi Sangat Tinggi | +0,45 | Pasti | Prioritas 2 (Beban Kasus Tinggi) |
| **8** | **RAWANG** | PADANG SELATAN | Tingkat 1 - Urgensi Sangat Tinggi | +0,24 | Pasti | Prioritas 2 (Beban Kasus Tinggi) |
| 9 | LUBUK KILANGAN | LUBUK KILANGAN | Tingkat 2 - Urgensi Sedang | +0,22 | Belum pasti | Prioritas 1 (Perbatasan) |
| 10 | PADANG PASIR | PADANG BARAT | Tingkat 2 - Urgensi Sedang | +0,17 | Pasti | Prioritas 2 (Beban Kasus Tinggi) |
| 11 | AMBACANG | KURANJI | Tingkat 2 - Urgensi Sedang | +0,09 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 12 | ANDALAS | PADANG TIMUR | Tingkat 2 - Urgensi Sedang | -0,02 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 13 | BELIMBING | KURANJI | Tingkat 2 - Urgensi Sedang | -0,07 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 14 | PAUH | PAUH | Tingkat 2 - Urgensi Sedang | -0,16 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 15 | AIR DINGIN | KOTO TANGAH | Tingkat 2 - Urgensi Sedang | -0,23 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 16 | PEMANCUNGAN | PADANG SELATAN | Tingkat 2 - Urgensi Sedang | -0,29 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 17 | LB.BUAYA | KOTO TANGAH | Tingkat 3 - Pemantauan Rutin | -0,38 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 18 | PARAK KARAKAH | PADANG TIMUR | Tingkat 3 - Pemantauan Rutin | -0,42 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 19 | KURANJI | KURANJI | Tingkat 3 - Pemantauan Rutin | -0,51 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 20 | PEGAMBIRAN | LUBUK BEGALUNG | Tingkat 3 - Pemantauan Rutin | -0,53 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 21 | TUNGGUL HITAM | KOTO TANGAH | Tingkat 3 - Pemantauan Rutin | -0,59 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 22 | LAPAI | NANGGALO | Tingkat 3 - Pemantauan Rutin | -0,70 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 23 | LUBUK BEGALUNG | LUBUK BEGALUNG | Tingkat 3 - Pemantauan Rutin | -0,83 | Pasti | Prioritas 3 (Pemantauan Rutin) |
| 24 | ULAK KARANG | PADANG UTARA | Tingkat 3 - Pemantauan Rutin | -0,90 | Pasti | Prioritas 3 (Pemantauan Rutin) |

### B. Profil Multi-dimensi Kelompok (Hasil Pembanding K-Means)

| Kelompok Profil | Jumlah | Anggota Puskesmas | Karakteristik Pusat Kelompok (*Centroid*) | Penjelasan Tipologi Intervensi |
| :--- | :---: | :--- | :--- | :--- |
| **Prioritas 1 (Urgensi Tertinggi)** | 4 | ALAI, BUNGUS, LUBUK KILANGAN, NANGGALO | Sangat Pendek: **36,5%** (+1,6 SD)<br>BB Tidak Naik: **51,0%** (+1,2 SD)<br>Bumil KEK: **16,3%** (+1,2 SD)<br>Kasus/Sasaran: **1,80%** (-0,6 SD) | **Tipe Krisis Klinis Balita & Risiko Ibu:** Memiliki keparahan balita ekstrem. Kasus per sasaran tampak rendah karena pada puskesmas berkasus sedikit (mis. Alai, 18 kasus/bln), hanya anak parah yang terdata. **Tindakan:** Rujukan medis kasus sangat pendek dan audit cakupan penimbangan posyandu ($D/S$). |
| **Prioritas 2 (Urgensi Menengah)** | 6 | AIR TAWAR, ANAK AIR, IKUR KOTO, PADANG PASIR, RAWANG, SEBERANG PADANG | Kasus/Sasaran: **6,86%** (+1,5 SD)<br>BB Tidak Naik: **46,1%** (+0,7 SD)<br>Bumil KEK: **13,0%** (+0,3 SD)<br>Sangat Pendek: **20,4%** (-0,3 SD) | **Tipe Beban Wilayah / Populasi Luas:** Memiliki volume penemuan kasus stunting terbesar di Kota Padang (Anak Air 166 kasus/bln, Ikur Koto 122 kasus/bln). **Tindakan:** Intervensi logistik berskala besar, PMT lokal massal, dan penguatan pos gizi. |
| **Prioritas 3 (Pemantauan Rutin)** | 14 | 14 Puskesmas lainnya | Seluruh 5 indikator berada di bawah atau mendekati rata-rata Kota Padang. Kasus/sasaran rata-rata: **2,07%**. | **Tipe Pemantauan Rutin:** Pemantauan pertumbuhan bulanan di posyandu dan edukasi gizi-sanitasi keluarga. |

---

## 7. Evaluasi Model: Seberapa Bisa Dipercaya?

Pengujian dilakukan melalui **4 cara pengujian inti** dan disimpulkan secara jujur:

| Cara Pengujian | Hasil Pengukuran | Penilaian Ilmiah | Kesimpulan Ringkas |
| :--- | :--- | :---: | :--- |
| **1. Dibandingkan dengan data yang diacak** | Silhouette = **0,268**<br>Davies-Bouldin = **1,234**<br>Uji acak (300x): **$p = 0{,}146$** | Struktur Lemah ($p > 0{,}05$) | K-Means tidak membuktikan adanya batas kelompok alami yang tegas. Pola ada, tetapi berupa kontinum (gradien tingkat keparahan). |
| **2. Kestabilan antarbulan** | Kemiripan pengelompokan (0 s.d. 1):<br>Mar-Apr = **0,42** \| Apr-Mei = **0,45** | Cukup (< 0,5) | Pengelompokan dari data satu bulan saja belum stabil; kebijakan wajib menggunakan rata-rata gabungan 3 bulan. |
| **3. Diulang dengan sampel anak berbeda (*bootstrap*)** | Rerata kemiripan = **0,72**<br>**19 Puskesmas Pasti**<br>**5 Puskesmas Belum pasti** | Sedang | Sebagian besar anggota kelompok stabil terhadap variasi sampel anak. Hanya puskesmas di perbatasan (mis. Lubuk Kilangan) yang belum pasti. |
| **4. Uji kepekaan / sensitivitas fitur** | Tanpa Kasus per Sasaran Balita: Kemiripan anjlok ke **0,45** | Paling Dominan | Indikator kasus per sasaran balita adalah penggerak utama pengelompokan; jika dihilangkan, struktur klaster berubah drastis. |

> [!CAUTION]
> **Kesimpulan Evaluasi Model:**
> Hasil ini **bukan penemuan kelompok alami yang mutlak di alam**, melainkan **alat bantu pendukung keputusan manajerial** berbasis Skor Urgensi Komposit dan profil karakteristik untuk memandu alokasi prioritas penanganan stunting Dinas Kesehatan Kota Padang.

---

## 8. Status Pekerjaan (12 Tahap Machine Learning)

* **Tahap 1 – 5:** Problem Definition, Data Collection, EDA, Preprocessing, Feature Engineering & Selection $\rightarrow$ **Selesai (Kode disederhanakan).**
* **Tahap 6 – 9:** Data Splitting, Model Selection, Model Training, Hyperparameter Tuning $\rightarrow$ **Selesai (Keputusan lugas, $n\_init = 30$).**
* **Tahap 10 – 12:** Model Evaluation (4 pengujian inti), Finalisasi Model (`.pkl`, `.json`, `.xlsx`), Deployment & Monitoring $\rightarrow$ **Selesai.**

---

## 9. Berkas Luaran

1. `Kelompok_8_ML_Stunting.ipynb`: Notebook kerja ringkas (42 sel terpadu).
2. `model_klaster_puskesmas_2026.pkl`: Pipeline terlatih (`StandardScaler` + `KMeans`), pemetaan prioritas, dan 5 fitur bersih.
3. `metadata_model_2026.json`: Catatan parameter teknis dan daftar batasan lengkap.
4. `Tabel_Final_Web_DSS_Puskesmas_2026.xlsx`: Rekapitulasi hasil 24 puskesmas dan 11 kecamatan untuk web DSS.
5. `peta_pca_puskesmas_padang_2026.png`: Visualisasi profil puskesmas pada ruang 2D PCA.
6. `hasil_klaster_stunting_2026.zip`: Arsip terpadu seluruh berkas luaran.
