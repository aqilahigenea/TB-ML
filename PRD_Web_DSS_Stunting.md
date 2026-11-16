# PRD: Aplikasi Web Pendukung Keputusan Prioritas Penanganan Stunting per Puskesmas

> **Product Requirements Document (PRD)**  
> **Tugas Besar Machine Learning — Kelompok 8, Universitas Andalas**  
> *Versi 2.0 (Disesuaikan dengan Model Terbaru — November 2026)*

---

## 1. Ringkasan Produk

Aplikasi Web Pendukung Keputusan (*Decision Support System* / DSS) Prioritas Penanganan Stunting adalah sistem berbasis web yang memanfaatkan model machine learning (`model_klaster_puskesmas_2026.pkl`) untuk membantu Dinas Kesehatan Kota Padang dan Kepala Puskesmas dalam memetakan **tingkat urgensi wilayah** dan **profil spesifik permasalahan stunting** di 24 puskesmas Kota Padang.

Sistem ini menyajikan:
1. **Hasil Utama:** Pemeringkatan **Indeks Urgensi Komposit (Skor Urgensi)** peringkat 1 s.d. 24 yang dikelompokkan ke dalam **Tiga Tingkat Urgensi Kebijakan** (Tingkat 1 - Urgensi Sangat Tinggi, Tingkat 2 - Urgensi Sedang, Tingkat 3 - Pemantauan Rutin).
2. **Hasil Pembanding (*Profiling* Multi-dimensi):** Klaster K-Means ($K=3$) untuk mengidentifikasi tipologi penanganan: **Tipe Krisis Klinis Balita** (Prioritas 1) vs **Tipe Beban Kasus Populasi Luas** (Prioritas 2).
3. **Status Kepastian:** Menandai tingkat stabilitas keanggotaan puskesmas (**Pasti** vs **Belum pasti**).

> [!NOTE]
> Aplikasi ini adalah **alat bantu pendukung keputusan (*decision support tool*) manajerial wilayah**, bukan alat diagnosis medis anak individual, dan bukan penentu tunggal alokasi anggaran tanpa konfirmasi lapangan.

---

## 2. Latar Belakang dan Masalah

* **Masalah Kebijakan:** Penanganan medis balita stunting (PMT, pemantauan pertumbuhan) pada dasarnya seragam per anak. Yang membutuhkan pertimbangan strategis adalah **wilayah mana yang harus didahulukan** dalam pendistribusian logistik dan intervensi khusus.
* **Beban Pengolahan Data Manual:** Setiap bulan, data penimbangan di Posyandu/Puskesmas menghasilkan ribuan baris data e-PPGBM / BNBA (*By Name By Address*). Mengagregasi, membersihkan, dan menganalisis tren antarpuskesmas secara manual memakan waktu berhari-hari.
* **Karakteristik Metodologis Model:** Model memiliki struktur klaster yang tergolong lemah (*Silhouette* 0,268; $p = 0{,}146$). Oleh karena itu, aplikasi harus **menampilkan Indeks Urgensi Komposit secara transparan** dan menyertakan **status kepastian (Pasti / Belum pasti)** agar pengguna tidak menganggap klaster sebagai sekat alami yang kaku.

---

## 3. Tujuan dan Metrik Keberhasilan

| Tujuan | Metrik Evaluasi | Target Kinerja |
| :--- | :--- | :--- |
| **Mempercepat pemetaan prioritas wilayah** | Waktu dari pengunggahan berkas BNBA `.xlsx` hingga hasil pemetaan tampil | Kurang dari **2 menit** untuk berkas 1.500 – 5.000 baris. |
| **Hasil transparan dan akuntabel** | Setiap puskesmas memiliki Skor Urgensi, Tingkat Urgensi (1-3), Kelompok Profil, dan Status Kepastian | **100% hasil** puskesmas memuat informasi lengkap. |
| **Penyajian bebas kebingungan** | Penjelasan penamaan prioritas dan peringatan pelaporan belum lengkap tampil di dashboard | **100% halaman hasil** menampilkan catatan konteks. |
| **Integritas penggunaan model** | Peringatan batasan model (potret 3 bulan, bukan prevalensi survei) tampil di antarmuka | Tampil di seluruh halaman hasil & ekspor Excel. |

---

## 4. Pengguna dan Hak Akses

| Pengguna | Karakteristik & Kebutuhan Utama | Hak Akses (*Role*) |
| :--- | :--- | :--- |
| **Dinas Kesehatan Kota Padang** (Pengambil Kebijakan) | Memeriksa peringkat urgensi 24 puskesmas, melihat ringkasan per kecamatan, membandingkan pergeseran antarbulan, dan mengunduh rekap Excel. Tidak perlu memahami teknis *machine learning*. | Melihat seluruh dashboard, perbandingan bulan, dan ekspor data. |
| **Kepala Puskesmas** | Melihat status puskesmasnya sendiri, indikator yang menonjol, dan usulan tindak lanjut spesifik. | Terbatas pada halaman profil puskesmasnya sendiri. |
| **Admin Sistem** (Operator Data Dinkes / Tim ML) | Mengunggah file BNBA bulanan, mengelola data rujukan sasaran balita dan persentase bumil KEK, serta mengunduh berkas log audit. | Akses penuh seluruh menu dan konfigurasi sistem. |

---

## 5. Ruang Lingkup Produk

### Termasuk dalam Ruang Lingkup (Versi 1):
1. Pengunggahan file Excel BNBA bulanan (format standar e-PPGBM).
2. Pembersihan otomatis data anomali (tanggal, batasan umur 60 bulan, berat badan > 35 kg, Z-score ekstrem).
3. Penghitungan otomatis 5 indikator utama:
   * `Kasus per sasaran balita`
   * `Persen sangat pendek`
   * `Persen stunting + kurus`
   * `Persen berat tidak naik`
   * `Persen bumil KEK`
4. Pemeringkatan **Indeks Urgensi Komposit (1 s.d. 24)** dan pembagian ke dalam **3 Tingkat Urgensi Kebijakan**.
5. Prediksi kelompok profil K-Means ($K=3$) menggunakan model `.pkl` (mode relatif dan mode ketat).
6. Penetapan status kepastian: **Pasti** vs **Belum pasti**.
7. Dashboard ringkasan per 11 kecamatan di Kota Padang.
8. Modul pemantauan pergeseran level indikator (*drift*) dan perpindahan kelompok antarbulan.
9. Ekspor rekapitulasi ke format Excel `.xlsx`.

### Di Luar Ruang Lingkup:
1. Prediksi klinis atau diagnosis per anak individual.
2. Integrasi data sosial-ekonomi (kemiskinan, sanitasi, air bersih) karena belum tersedia data resmi per puskesmas.
3. Proyeksi tren masa depan (data masukan saat ini berupa potret 3 bulan).
4. Pelatihan ulang model (*retraining*) otomatis tanpa supervisi manusia.

---

## 6. Kebutuhan Fungsional Produk

*Prioritas: **P0** (Wajib), **P1** (Penting), **P2** (Tambahan).*

| ID | Fitur Produk | Prioritas | Kriteria Penerimaan (*Acceptance Criteria*) |
| :---: | :--- | :---: | :--- |
| **F1** | Autentikasi dan Pembatasan Peran | P0 | Pengguna login sesuai peran; Kepala Puskesmas hanya dapat mengakses puskesmas miliknya; sesi aman. |
| **F2** | Unggah Berkas BNBA Bulanan (`.xlsx`) | P0 | Sistem memvalidasi keberadaan sheet `Application List` dan kolom wajib; menolak berkas non-xlsx dengan pesan informatif. |
| **F3** | Pembersihan Data Otomatis | P0 | Menjalankan aturan pembersihan Tahap 4; menyajikan laporan audit: jumlah baris mentah, baris dibuang per alasan, dan baris valid yang diproses. |
| **F4** | Penghitungan 5 Indikator per Puskesmas | P0 | Menghitung 5 indikator sesuai rumus terbaru; mencocokkan nama puskesmas dengan kamus sasaran Dinkes. |
| **F5** | Prediksi Kelompok Profil Multi-dimensi | P0 | Memuat `model_klaster_puskesmas_2026.pkl`; mendukung mode relatif ($\ge 10$ puskesmas) dan mode ketat; menampilkan usulan kebijakan awal. |
| **F6** | Dashboard Hasil per Puskesmas | P0 | Menampilkan Tingkat Urgensi, Skor Urgensi, Kelompok Profil, Status Kepastian (**Pasti / Belum pasti**), dan indikator spesifik. |
| **F7** | Tabel Pemeringkatan Indeks Urgensi (Hasil Utama) | P0 | Menampilkan tabel 24 puskesmas terurut dari Skor Urgensi tertinggi ke terendah, lengkap dengan pembagian 3 Tingkat Urgensi. |
| **F8** | Ringkasan per Kecamatan (11 Kecamatan) | P1 | Menampilkan agregasi per kecamatan: jumlah puskesmas per tingkat urgensi, total kasus bulanan, total sasaran, dan kasus per sasaran kecamatan (%). |
| **F9** | Pemantauan Pergeseran Indikator & Wilayah | P1 | Menghitung pergeseran simpangan baku (*drift*): Normal ($< 0{,}5$ SD), Waspada ($0{,}5 - 1{,}0$ SD), Kritis ($\ge 1{,}0$ SD); mendeteksi puskesmas yang berpindah kelompok. |
| **F10** | Perbandingan Antarbulan (*Historical View*) | P1 | Pengguna dapat memilih dua periode bulan untuk membandingkan perubahan skor dan perpindahan prioritas puskesmas. |
| **F11** | Ekspor Laporan Excel Terpadu | P1 | Mengunduh berkas `.xlsx` berisi tabel hasil 24 puskesmas, ringkasan kecamatan, profil kelompok, dan catatan batasan metodologis. |
| **F12** | Pengelolaan Data Rujukan Sasaran & Bumil KEK | P1 | Admin dapat memperbarui angka sasaran balita dan % bumil KEK per puskesmas ketika rekapitulasi baru Dinkes terbit, tercatat dalam riwayat perubahan (*audit log*). |
| **F13** | Halaman Informasi Model & Keterbatasan | P0 | Menyajikan ringkasan model: metrik (Silhouette 0,268; $p = 0{,}146$), 4 cara pengujian inti, batasan potret data, dan penjelasan penamaan prioritas. |
| **F14** | Visualisasi Peta PCA 2D | P2 | Menampilkan sebaran 24 puskesmas pada ruang 2 Komponen Utama (PC1 & PC2) untuk melihat pengelompokan secara visual. |
| **F15** | Pengunduhan Data Gabungan untuk Retraining | P2 | Admin dapat mengunduh data gabungan multi-bulan terstandarisasi untuk keperluan pelatihan ulang model secara terpandu di notebook. |

---

## 7. Kebutuhan Non-Fungsional

1. **Privasi & Keamanan Data (Kritis):**
   * Berkas BNBA mentah memuat informasi pribadi balita (Nama, NIK, Tanggal Lahir, Alamat).
   * **Aturan Privasi:** Data per anak hanya diproses sementara di memori (*RAM*) selama eksekusi pembersihan dan agregasi. Aplikasi **tidak menyimpan data individual anak ke dalam basis data permanen**. Hanya data agregat tingkat puskesmas yang disimpan.
2. **Kinerja Sistem:**
   * Waktu pemrosesan satu berkas BNBA bulanan (1.500 – 5.000 baris) hingga tabel hasil tampil selesai dalam waktu kurang dari 2 menit.
3. **Keterbacaan & Bahasa:**
   * Antarmuka berbahasa Indonesia yang ramah bagi pengguna non-teknis. Istilah teknis (seperti *z-score*, *drift*) selalu disertai tooltip penjelasan singkat.
4. **Kompatibilitas Pustaka Machine Learning:**
   * Lingkungan eksekusi web harus menggunakan versi pustaka `scikit-learn` yang kompatibel dengan versi saat pelatihan model `.pkl`.

---

## 8. Spesifikasi Data Masukan dan Keluaran

### Masukan:
1. Berkas Excel BNBA satu bulan (`.xlsx`, sheet `Application List`).
2. Data rujukan Dinas Kesehatan (Kamus Sasaran Balita dan % Ibu Hamil KEK per puskesmas).

### Lima Fitur Model (Urutan Baku):
1. `Kasus per sasaran balita`
2. `Persen sangat pendek`
3. `Persen stunting + kurus`
4. `Persen berat tidak naik`
5. `Persen bumil KEK`

### Keluaran per Puskesmas:
1. `Peringkat_Urgensi` (1 s.d. 24)
2. `Tingkat_Urgensi` (Tingkat 1 - Urgensi Sangat Tinggi, Tingkat 2 - Urgensi Sedang, Tingkat 3 - Pemantauan Rutin)
3. `Skor_Urgensi` (nilai kontinu rata-rata z-score)
4. `Kelompok_Prioritas` (Prioritas 1 / 2 / 3 K-Means)
5. `Status_Kepastian` (**Pasti** vs **Belum pasti**)
6. `Usulan_Kebijakan` (rekomendasi intervensi manajerial)

---

## 9. Manajemen Risiko dan Mitigasi

| Potensi Risiko | Dampak terhadap Pengguna | Strategi Mitigasi dalam Aplikasi |
| :--- | :--- | :--- |
| **Struktur klaster lemah (Silhouette 0,268)** | Pengguna salah menganggap kelompok klaster sebagai klasifikasi mutlak di alam. | Tampilkan **Indeks Urgensi Komposit (Peringkat 1-24)** sebagai hasil utama; posisikan klaster sebagai profil pembanding; tampilkan status kepastian. |
| **Prioritas 1 prevalensinya lebih rendah dibanding Prioritas 2** | Kebingungan di pihak Dinas Kesehatan saat membaca nama kelompok. | Sertakan penjelasan penamaan transparan: Prioritas 1 didorong keparahan klinis ganda; sertakan peringatan bahwa puskesmas berkasus sedikit (mis. Alai) berpotensi mengalami pelaporan belum lengkap ($D/S$ rendah). |
| **Kebocoran data identitas balita** | Pelanggaran privasi dan kerahasiaan medis. | Data per anak diproses murni di memori dan langsung dibuang setelah agregasi; hanya simpan data agregat puskesmas. |
| **Perubahan format berkas BNBA oleh kementerian** | Kesalahan pembacaan data (*parsing error*). | Validasi skema kolom sebelum pemrosesan; jika kolom wajib hilang, tolak dengan pesan galat yang menyebutkan nama kolom secara spesifik. |
