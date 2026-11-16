# SRS: Aplikasi Web Pendukung Keputusan Prioritas Penanganan Stunting per Puskesmas

> **Software Requirements Specification (SRS)**  
> **Tugas Besar Machine Learning — Kelompok 8, Universitas Andalas**  
> *Versi 2.0 (Disesuaikan dengan Model Terbaru — November 2026)*

---

## 1. Pendahuluan

### 1.1 Tujuan Dokumen
Dokumen Spesifikasi Kebutuhan Perangkat Lunak (*Software Requirements Specification* / SRS) ini menetapkan kebutuhan fungsional dan non-fungsional secara terperinci untuk pengembangan Aplikasi Web Pendukung Keputusan (*Decision Support System* / DSS) Prioritas Penanganan Stunting berbasis model machine learning (`model_klaster_puskesmas_2026.pkl`). Dokumen ini ditujukan bagi tim pengembang perangkat lunak, dosen pembimbing/penilai, serta pemangku kepentingan di Dinas Kesehatan Kota Padang.

### 1.2 Ruang Lingkup Produk
Aplikasi web ini bertugas memproses berkas data bulanan e-PPGBM / BNBA (*By Name By Address*), membersihkan anomali pencatatan, menghitung lima indikator utama tingkat puskesmas, mengurutkan puskesmas berdasarkan **Indeks Urgensi Komposit (Hasil Utama)** ke dalam tiga tingkat urgensi kebijakan, memprediksi **Kelompok Profil Multi-dimensi K-Means** ($K=3$), serta menetapkan **Status Kepastian** (**Pasti** vs **Belum pasti**).

Aplikasi ini diposisikan sebagai **alat bantu pendukung keputusan manajerial wilayah**, bukan alat diagnosis medis anak individual, dan bukan penentu tunggal alokasi anggaran tanpa konfirmasi lapangan.

### 1.3 Definisi dan Singkatan
| Istilah / Singkatan | Definisi Operasional |
| :--- | :--- |
| **BNBA** | *By Name By Address*, data pencatatan balita tingkat posyandu/puskesmas. |
| **Dinkes** | Dinas Kesehatan Kota Padang. |
| **Bumil KEK** | Ibu Hamil Kurang Energi Kronis (lingkar lengan atas < 23,5 cm). |
| **Skor Urgensi** | Nilai kontinu rata-rata *z-score* 5 indikator pada puskesmas (positif = lebih urgen). |
| **Tingkat Urgensi** | Pembagian 24 puskesmas ke dalam 3 tingkat manajerial (Tingkat 1 - Urgensi Sangat Tinggi: 8 puskesmas; Tingkat 2 - Urgensi Sedang: 8 puskesmas; Tingkat 3 - Pemantauan Rutin: 8 puskesmas). |
| **Kelompok Profil (K-Means)** | Tipologi permasalahan stunting hasil pengelompokan K-Means ($K=3$). |
| **Status Kepastian** | Tingkat ketahanan keanggotaan kelompok: **Pasti** (stabil) atau **Belum pasti** (di perbatasan). |
| **Mode Relatif** | Standardisasi indikator terhadap nilai rata-rata dan simpangan baku periode data itu sendiri. |
| **Mode Ketat** | Standardisasi memakai nilai rata-rata dan simpangan baku dari data latih di dalam model `.pkl`. |
| **ARI** | *Adjusted Rand Index*, tingkat kemiripan dua pengelompokan (rentang 0 sampai 1). |

### 1.4 Dokumen Referensi
1. *Product Requirements Document (PRD) Aplikasi Web Pendukung Keputusan Prioritas Stunting*, Kelompok 8 (Versi 2.0).
2. *Dokumen Konteks Project: Klasterisasi Puskesmas Berdasarkan Indikator Stunting*, Kelompok 8 (Versi 2.0).
3. Notebook `Kelompok_8_ML_Stunting.ipynb` dan berkas `metadata_model_2026.json`.

---

## 2. Deskripsi Umum

### 2.1 Perspektif Produk
Aplikasi ini merupakan perangkat lunak berbasis web mandiri (*standalone web application*) yang mengintegrasikan *pipeline* model machine learning terlatih (`model_klaster_puskesmas_2026.pkl`). Sumber data masukan utama adalah berkas Microsoft Excel (`.xlsx`) data BNBA bulanan dan basis data rujukan (angka proyeksi sasaran balita dan persentase bumil KEK per puskesmas dari Dinas Kesehatan).

### 2.2 Karakteristik Pengguna
1. **Admin (Operator Data Dinkes / Tim Pengembang):** Memahami struktur data BNBA, mengelola unggahan data bulanan, memperbarui kamus sasaran, dan memantau log sistem.
2. **Pejabat Dinas Kesehatan Kota Padang:** Membaca dashboard peringkat wilayah, membandingkan pergeseran antarbulan, dan mengunduh laporan eksekutif Excel.
3. **Kepala Puskesmas:** Mengakses dashboard khusus puskesmasnya untuk melihat indikator yang menonjol dan usulan intervensi spesifik.

### 2.3 Batasan Perangkat Lunak
1. Model memproses tepat **lima indikator** dengan urutan baku:
   `['Kasus per sasaran balita', 'Persen sangat pendek', 'Persen stunting + kurus', 'Persen berat tidak naik', 'Persen bumil KEK']`.
2. Model dilatih dari data 24 puskesmas Kota Padang periode Maret – Mei 2026 (potret 3 bulan).
3. Lingkungan eksekusi web wajib menggunakan versi pustaka `scikit-learn` yang kompatibel dengan versi saat berkas `.pkl` diekspor.
4. **Privasi Data:** Data pribadi anak individual diproses sementara di memori dan tidak disimpan permanen di basis data.

---

## 3. Kebutuhan Antarmuka Eksternal

### 3.1 Antarmuka Pengguna (*UI*)
* Antarmuka berbahasa Indonesia yang bersih dan responsif.
* Halaman utama: *Login*, *Dashboard Ringkasan Eksekutif*, *Unggah BNBA Bulanan*, *Hasil per Puskesmas*, *Ringkasan per Kecamatan*, *Tabel Pemeringkatan Indeks Urgensi*, *Pemantauan Pergeseran (Drift)*, *Informasi Model & Keterbatasan*, dan *Pengelolaan Data Rujukan*.
* Penandaan tingkat prioritas menggunakan teks eksplisit dan palet warna standar (Merah = Tingkat 1 / Sangat Tinggi, Oranye = Tingkat 2 / Sedang, Hijau = Tingkat 3 / Rutin).
* Status kepastian ditampilkan dalam bentuk lencana (*badge*) teks: **Pasti** atau **Belum pasti**.

### 3.2 Antarmuka Perangkat Lunak
* **Paket Model:** Berkas `model_klaster_puskesmas_2026.pkl` berisi kamus objek: `pipeline` (`StandardScaler` + `KMeans`), `mapping`, `features`, `rekomendasi`, `referensi_fitur`, `versi`, dan `tanggal_latih`.
* **Berkas Masukan:** Format `.xlsx` (lembar kerja wajib: `Application List`).
* **Berkas Keluaran:** Format `.xlsx` untuk unduhan laporan eksekutif.

---

## 4. Kebutuhan Fungsional

Format ID Kebutuhan: **SRS-F[Nomor]**.

| ID | Kebutuhan Fungsional | Kriteria Pengujian / Penerimaan |
| :---: | :--- | :--- |
| **SRS-F01** | Sistem mengautentikasi pengguna berdasarkan peran (*Admin*, *Dinkes*, *Kepala Puskesmas*). | Akses menu dibatasi sesuai hak; Kepala Puskesmas hanya dapat melihat detail puskesmasnya sendiri. |
| **SRS-F02** | Sistem menerima satu berkas unggahan berformat `.xlsx` per sesi pemrosesan. | Berkas non-xlsx atau berkas melebihi batas ukuran (mis. > 20 MB) ditolak dengan pesan kesalahan yang jelas. |
| **SRS-F03** | Sistem memvalidasi struktur berkas: keberadaan lembar `Application List`, kelengkapan kolom wajib, dan kolom `Kab/Kota` bernilai `KOTA PADANG`. | Berkas dengan kolom bergeser atau wilayah di luar Kota Padang ditolak; baris di luar wilayah dibuang dan dilaporkan. |
| **SRS-F04** | Sistem membersihkan data anomali secara otomatis sesuai aturan bisnis (Bagian 6.1) dan menyajikan ringkasan audit data. | Menampilkan jumlah baris mentah, baris dibuang per kategori anomali, dan total baris valid yang diproses. |
| **SRS-F05** | Sistem menghitung lima indikator utama per puskesmas sesuai rumus terbaru (Bagian 6.2). | Nilai yang dihasilkan identik dengan fungsi `hitung_fitur` pada notebook acuan. |
| **SRS-F06** | Sistem memprediksi kelompok profil K-Means menggunakan paket model `.pkl` (mendukung mode relatif dan mode ketat). | Mode relatif aktif jika puskesmas $\ge 10$; menghasilkan nama kelompok prioritas profil dan rekomendasi kebijakan. |
| **SRS-F07** | Sistem memeriksa nama puskesmas terhadap kamus sasaran Dinkes. | Puskesmas yang tidak terdaftar dilewati dengan pesan peringatan tanpa menghentikan pemrosesan puskesmas lain. |
| **SRS-F08** | Sistem menyajikan halaman detail per puskesmas: Tingkat Urgensi, Skor Urgensi, Kelompok Profil, Status Kepastian (**Pasti / Belum pasti**), nilai 5 indikator, dan usulan intervensi. | Seluruh atribut tampil lengkap dan sinkron dengan hasil agregasi bulanan. |
| **SRS-F09** | Sistem menetapkan status kepastian puskesmas: **Pasti** jika kepastian *bootstrap* $\ge 70\%$ dan nilai *silhouette sample* $\ge 0$; **Belum pasti** jika berada di bawah ambang batas tersebut. | Klasifikasi kepastian tepat merefleksikan puskesmas di perbatasan (mis. Lubuk Kilangan berstatus Belum pasti). |
| **SRS-F10** | Sistem menyajikan **Tabel Pemeringkatan Indeks Urgensi (Hasil Utama)**: 24 puskesmas diurutkan dari Skor Urgensi tertinggi ke terendah, dibagi ke dalam 3 Tingkat Urgensi Kebijakan. | Tabel terurut transparan; Top 8 berstatus Tingkat 1, Mid 8 Tingkat 2, Low 8 Tingkat 3. |
| **SRS-F11** | Sistem menyajikan ringkasan per kecamatan (11 kecamatan): jumlah puskesmas per tingkat urgensi, total kasus tercatat, sasaran balita, dan persentase kasus per sasaran kecamatan. | Agregasi kecamatan tepat menjumlahkan puskesmas di bawah naungannya. |
| **SRS-F12** | Sistem menghitung pergeseran indikator (*drift*) data bulan baru terhadap acuan dalam satuan simpangan baku (SD): Normal ($< 0{,}5$ SD), Waspada ($0{,}5 - 1{,}0$ SD), Kritis ($\ge 1{,}0$ SD). | Status pergeseran tertera jelas di dashboard pemantauan. |
| **SRS-F13** | Sistem mendeteksi persentase puskesmas yang sekelompok dengan data acuan dan menampilkan daftar puskesmas yang berpindah kelompok. | Daftar perpindahan kelompok tampil informatif. |
| **SRS-F14** | Sistem menyediakan fitur perbandingan antarbulan (*side-by-side comparison*) untuk dua periode bulan yang tersimpan. | Pengguna dapat memilih dua bulan dan melihat pergeseran skor serta perubahan status prioritas. |
| **SRS-F15** | Sistem mengekspor rekapitulasi hasil pemetaan ke berkas Microsoft Excel (`.xlsx`) yang memuat lembar *Puskesmas*, *Kecamatan*, dan *Catatan Batasan*. | Berkas Excel dapat diunduh dan dibuka tanpa kesalahan format. |
| **SRS-F16** | Admin dapat memperbarui kamus sasaran balita dan persentase bumil KEK per puskesmas dengan pencatatan riwayat perubahan (*audit trail*). | Setiap perubahan mencatat nama admin, waktu modifikasi, nilai lama, dan nilai baru. |
| **SRS-F17** | Sistem menyediakan halaman **Informasi Model & Keterbatasan**: metrik internal (Silhouette 0,268; $p = 0{,}146$), ringkasan 4 cara pengujian inti, batasan potret data, dan penjelasan penamaan prioritas. | Informasi dapat diakses oleh seluruh peran pengguna. |
| **SRS-F18** | Sistem menampilkan visualisasi peta sebaran 2 Komponen Utama (PCA) pada halaman hasil. | Visualisasi 2D PCA tampil jelas dengan penanda nama puskesmas. |
| **SRS-F19** | Admin dapat mengunduh data gabungan multi-bulan terstandarisasi untuk keperluan pelatihan ulang (*retraining*) model secara berkala. | Berkas data gabungan dapat diunduh dengan struktur yang sesuai format pelatihan. |

---

## 5. Kebutuhan Non-Fungsional

| ID | Kategori | Kebutuhan Spesifik |
| :---: | :--- | :--- |
| **SRS-N01** | Kinerja | Waktu pemrosesan satu berkas BNBA (1.500 – 5.000 baris) dari unggah hingga dashboard tampil selesai dalam waktu $< 2$ menit. |
| **SRS-N02** | Keamanan | Autentikasi berbasis kata sandi terenkripsi (*hash bcrypt*); pembatasan hak akses berbasis peran (*RBAC*); perlindungan dari serangan umum (CSRF, XSS). |
| **SRS-N03** | Privasi Data | Data individual anak (Nama, NIK, Tanggal Lahir) hanya diproses sementara di memori (*RAM*) selama agregasi dan **tidak disimpan ke basis data permanen**. |
| **SRS-N04** | Keterlacakan | Setiap pemrosesan hasil mencatat ID pengguna, tanggal pemrosesan, bulan data, mode standardisasi, dan versi model. |
| **SRS-N05** | Keterbacaan | Menggunakan bahasa Indonesia yang komunikatif; istilah teknis machine learning dilengkapi dengan *tooltip* penjelasan singkat. |
| **SRS-N06** | Kompatibilitas | Dependensi pustaka `scikit-learn`, `numpy`, dan `pandas` di aplikasi web harus kompatibel dengan versi saat pelatihan model `.pkl`. |
| **SRS-N07** | Keandalan | Terjadinya galat pada data unggahan tidak boleh merusak atau menghapus data riwayat bulan-bulan sebelumnya. |
| **SRS-N08** | Kemudahan Pakai | Pejabat Dinas Kesehatan dapat menavigasi dari login, mengunggah data, hingga membaca tabel prioritas tanpa memerlukan pelatihan teknis rumit. |

---

## 6. Aturan Bisnis dan Spesifikasi Data

### 6.1 Aturan Pembersihan Data (Tahap 4)
1. Kolom numerik: konversi `Berat`, `Tinggi`, `ZS BB/U`, `ZS TB/U`, dan `ZS BB/TB` ke float numerik.
2. Hitung `Usia_Bulan` = $(\text{Tanggal Pengukuran} - \text{Tanggal Lahir}) / 30{,}4375\text{ hari}$.
3. Koreksi nilai berat: jika `Berat` $> 100$, asumsikan satuan gram dan bagi $1.000$.
4. Kriteria eliminasi baris:
   * Nilai mutlak Z-Score $> 10$ atau kosong.
   * `Berat` $> 35\text{ kg}$.
   * `Usia_Bulan` $\le 0$ atau kosong.
   * `Usia_Bulan` $> 60\text{ bulan}$ (BNBA dikhususkan untuk balita 0–59 bulan).
5. Kunci anak unik: `Nama Anak + Tanggal Lahir`. Balita yang sama yang tercatat lebih dari satu kali dalam bulan yang sama hanya dihitung satu kali.

### 6.2 Rumus Penghitungan 5 Indikator per Puskesmas (Periode $n$ Bulan)
| Indikator | Rumus Perhitungan Matematis | Penjelasan |
| :--- | :--- | :--- |
| **`Kasus per sasaran balita`** | $\frac{\sum \text{Total Kasus Stunting}}{\text{Sasaran Balita per Bulan} \times n} \times 100\%$ | Proporsi kasus tercatat terhadap sasaran (%). |
| **`Persen sangat pendek`** | $\frac{\sum (\text{TB/U} == \text{'Sangat Pendek'})}{\sum \text{Total Kasus Stunting}} \times 100\%$ | Persentase keparahan stunting balita (%). |
| **`Persen stunting + kurus`** | $\frac{\sum (\text{BB/TB} \in \{\text{'Gizi Kurang'}, \text{'Gizi Buruk'}\})}{\sum \text{Total Kasus Stunting}} \times 100\%$ | Persentase stunting sekaligus wasting (%). |
| **`Persen berat tidak naik`** | $\frac{\sum (\text{Naik Berat Badan} == \text{'T'})}{\sum \text{Total Kasus Stunting}} \times 100\%$ | Persentase pertumbuhan yang mandek (%). |
| **`Persen bumil KEK`** | Diambil langsung dari kamus data rujukan resmi Dinkes | Persentase ibu hamil KEK di wilayah puskesmas (%). |

### 6.3 Standardisasi dan Inferensi Prediksi
* **Mode Ketat:**
  $$Z = \text{scaler}_{\text{model}}.\text{transform}(X)$$
  $$\text{Cluster\_ID} = \text{kmeans}_{\text{model}}.\text{predict}(Z)$$
* **Mode Relatif ($\ge 10$ Puskesmas):**
  $$Z = \frac{X - \mu_{\text{periode}}}{\sigma_{\text{periode}}\ (ddof=0)}$$
  $$\text{Cluster\_ID} = \text{kmeans}_{\text{model}}.\text{predict}(Z)$$
* **Penghitungan Skor Urgensi:**
  $$\text{Skor Urgensi} = \frac{1}{5} \sum_{i=1}^{5} z_i$$

### 6.4 Aturan Status Kepastian
1. **Pasti:** Kepastian *bootstrap* $\ge 70\%$ dan nilai *Silhouette* sampel $\ge 0$.
2. **Belum pasti:** Kepastian *bootstrap* $< 70\%$ atau nilai *Silhouette* sampel $< 0$ (berada di perbatasan klaster, misal Lubuk Kilangan).

### 6.5 Ambang Batas Pemantauan Pergeseran (*Drift*)
$$\text{Pergeseran (x SD)} = \frac{\mu_{\text{indikator baru}} - \mu_{\text{acuan}}}{\sigma_{\text{acuan}}}$$
* **Normal:** $|\text{Pergeseran}| < 0{,}5\text{ SD}$.
* **Waspada:** $0{,}5\text{ SD} \le |\text{Pergeseran}| < 1{,}0\text{ SD}$.
* **Kritis:** $|\text{Pergeseran}| \ge 1{,}0\text{ SD}$.

---

## 7. Penanganan Kesalahan (*Error Handling*)

| Kondisi Galat | Tindakan Sistem |
| :--- | :--- |
| Berkas bukan `.xlsx` atau ukuran melebihi batas | Sistem membatalkan proses dan menampilkan pesan: *"Format berkas tidak didukung. Harap unggah berkas Microsoft Excel (.xlsx)."* |
| Lembar `Application List` atau kolom wajib hilang | Sistem membatalkan proses dan menampilkan daftar kolom yang tidak ditemukan. |
| Puskesmas tidak tercatat di kamus sasaran Dinkes | Sistem melewati baris puskesmas tersebut, memproses puskesmas lain yang valid, dan menampilkan daftar puskesmas yang dilewati pada log audit. |
| Jumlah puskesmas valid $< 10$ pada Mode Relatif | Sistem otomatis menolak Mode Relatif dan mengalihkan ke Mode Ketat dengan notifikasi peringatan. |
| Berkas paket model `.pkl` rusak atau tidak kompatibel | Sistem menonaktifkan tombol pemrosesan dan menampilkan pesan: *"Paket model tidak dapat dimuat. Periksa kompatibilitas versi pustaka scikit-learn."* |

---

## 8. Skenario Pengujian Sistem Utama

| ID Uji | Skenario Pengujian | Hasil yang Diharapkan |
| :---: | :--- | :--- |
| **UT-01** | Unggah berkas data valid Mei 2026 (Mode Relatif). | Sebanyak 1.612 baris valid diproses; 24 puskesmas terpetakan; tabel peringkat urgensi 1-24 tampil; 92% puskesmas konsisten dengan acuan. |
| **UT-02** | Unggah berkas yang memuat baris di luar Kota Padang. | Sistem mengeliminasi baris tersebut dan melaporkan jumlah baris yang dieliminasi pada ringkasan pembersihan. |
| **UT-03** | Unggah berkas dengan format kolom yang salah. | Sistem menolak berkas sebelum pemrosesan tanpa menyebabkan aplikasi *crash*. |
| **UT-04** | Pengguna dengan peran Kepala Puskesmas membuka puskesmas lain. | Sistem menolak akses dan menampilkan halaman pembatasan hak (*Unauthorized Access*). |
| **UT-05** | Ekspor hasil ke Microsoft Excel. | Berkas `.xlsx` berhasil diunduh, memuat lembar *Puskesmas* (lengkap dengan Skor Urgensi, Tingkat Urgensi, Kelompok, dan Status Kepastian), lembar *Kecamatan*, dan catatan batasan. |
