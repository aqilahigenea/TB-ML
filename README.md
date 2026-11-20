# Sistem Pendukung Keputusan (DSS) Prioritas Penanganan Stunting Kota Padang

> **Tugas Besar Machine Learning — Kelompok 8, Departemen Sistem Informasi, Universitas Andalas**  

> *Aplikasi Web Berbasis Python Flask & Machine Learning (K-Means Clustering)*

> **Revisi Model v1.1 (Silhouette 0,268 → 0,502):** kelompok kini dibentuk dari **2 indikator inti** (Kasus per sasaran balita dan Persen berat tidak naik) dengan K-Means K=3 (titik awal pusat Ward). Kelima indikator tetap dipakai untuk Skor Urgensi, peringkat, dan profil kelompok. Hasil: Prioritas 1 = Beban Kasus Tinggi (5 puskesmas), Prioritas 2 = Pertumbuhan Mandek & Balita Sangat Pendek (8), Prioritas 3 = Pemantauan Rutin (11); Silhouette K=2/3/4 = 0,411/0,502/0,446; Davies-Bouldin 0,612; uji data acak p = 0,34 (tidak signifikan); bootstrap 23/24 Pasti (Pauh = Belum pasti). Angka dan tabel kelompok pada bagian 5-7 di bawah masih versi lama, dan ARI antarperiode harus dihitung ulang dengan menjalankan notebook.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![Bootstrap](https://img.shields.io/badge/UI-Bootstrap%205-purple.svg)](https://getbootstrap.com/)

---

## 📌 Cerita Utama Proyek Ini (3 Kalimat)
1. **Data BNBA** dibersihkan, lalu diringkas jadi **5 angka per puskesmas**.
2. **K-Means ($K=3$)** mengelompokkan 24 puskesmas, lalu kelompok diberi nama prioritas.
3. Hasil diuji dengan **4 cara** dan disimpulkan jujur: **pola ada tapi lemah**.

---

## 🚀 Fitur Utama Sistem

1. **Dashboard Indeks Urgensi Komposit (Hasil Utama):**
   * Pemeringkatan 24 Puskesmas se-Kota Padang berdasarkan rata-rata *z-score* 5 indikator utama (Peringkat 1 s.d. 24).
   * Segmentasi ke dalam **3 Tingkat Urgensi Kebijakan**:
     * **Tingkat 1 - Urgensi Sangat Tinggi (8 Puskesmas teratas):** Alai, Bungus, Ikur Koto, Nanggalo, Anak Air, Seberang Padang, Air Tawar, Rawang.
     * **Tingkat 2 - Urgensi Sedang (8 Puskesmas menengah):** Lubuk Kilangan, Padang Pasir, Ambacang, Andalas, Belimbing, Pauh, Air Dingin, Pemancungan.
     * **Tingkat 3 - Pemantauan Rutin (8 Puskesmas terbawah):** LB.Buaya, Parak Karakah, Kuranji, Pegambiran, Tunggul Hitam, Lapai, Lubuk Begalung, Ulak Karang.
2. **Hasil Pembanding Profiling K-Means ($K=3$):**
   * **Prioritas 1 (Krisis Klinis Balita):** Persen balita sangat pendek, berat tidak naik, dan bumil KEK sangat tinggi.
   * **Prioritas 2 (Beban Kasus Tinggi):** Volume penemuan kasus stunting terbesar di Kota Padang (prevalensi tercatat tertinggi).
   * **Prioritas 3 (Pemantauan Rutin):** Seluruh indikator berada di bawah rata-rata.
3. **Status Kepastian Keanggotaan:**
   * Menandai stabilitas keanggotaan puskesmas (**Pasti** vs **Belum pasti**) hasil pengujian *bootstrap* 300x.
4. **Modul Unggah & Pemrosesan Data BNBA Baru:**
   * Menerima berkas Microsoft Excel e-PPGBM bulanan (`.xlsx`), membersihkan anomali, mengagregasi fitur, dan memprediksi prioritas secara otomatis.
5. **Pemantauan Pergeseran Indikator (*Drift Monitoring*):**
   * Memantau deviasi indikator data baru terhadap acuan: Normal ($< 0{,}5$ SD), Waspada ($0{,}5 - 1{,}0$ SD), dan Kritis ($\ge 1{,}0$ SD).
6. **Ekspor Laporan Rekapitulasi:**
   * Unduhan tabel hasil 24 puskesmas dan 11 kecamatan ke format Microsoft Excel.

---

## 📊 Lima Indikator Utama

Semua indikator dibaca: **makin tinggi = makin buruk / makin butuh perhatian**.

| Nama Indikator | Cara Perhitungan | Arti |
| :--- | :--- | :--- |
| **`Kasus per sasaran balita`** | $\frac{\text{Kasus BNBA}}{\text{Sasaran Balita} \times \text{Bulan}} \times 100\%$ | Proporsi kasus tercatat dibanding total sasaran balita (%). |
| **`Persen sangat pendek`** | $\frac{\text{Balita Sangat Pendek (TB/U)}}{\text{Total Kasus}} \times 100\%$ | Tingkat keparahan stunting balita (%). |
| **`Persen stunting + kurus`** | $\frac{\text{Balita Gizi Kurang/Buruk (BB/TB)}}{\text{Total Kasus}} \times 100\%$ | Balita stunting sekaligus kurus / *wasting* (%). |
| **`Persen berat tidak naik`** | $\frac{\text{Balita BB Tidak Naik (T)}}{\text{Total Kasus}} \times 100\%$ | Pertumbuhan balita yang mandek (%). |
| **`Persen bumil KEK`** | Rekap resmi Dinas Kesehatan | Risiko kurang energi kronis dari sisi ibu hamil (%). |

---

## 📂 Struktur Proyek

```text
TB-ML/
│
├── app.py                                   # Aplikasi utama Flask (routing & controllers)
├── model_helper.py                          # Logika pembersihan BNBA & inferensi ML
├── requirements.txt                         # Dependensi pustaka Python
├── .gitignore                               # Berkas yang dikecualikan dari Git
├── README.md                                # Dokumentasi proyek
│
├── Kelompok_8_ML_Stunting.ipynb             # Notebook pelatihan ML di Google Colab (42 sel)
├── Dokumen_Konteks_Project.md               # Laporan metodologi & konteks proyek
├── PRD_Web_DSS_Stunting.md                  # Product Requirements Document
├── SRS_Web_DSS_Stunting.md                  # Software Requirements Specification
│
├── model/
│   └── model_klaster_puskesmas_2026.pkl     # Paket model pipeline terlatih
│
├── data/
│   └── Tabel_Final_Web_DSS_Puskesmas_2026.xlsx # Data acuan 24 puskesmas & kecamatan
│
├── templates/                               # Tampilan antarmuka HTML (Bootstrap 5)
│   ├── base.html                            # Kerangka utama, navbar, footer
│   ├── index.html                           # Dashboard peringkat 24 puskesmas & kecamatan
│   ├── upload.html                          # Formulir unggah berkas e-PPGBM bulanan
│   ├── hasil.html                           # Hasil prediksi data baru & pemantauan drift
│   ├── informasi.html                       # Metrik evaluasi & batasan model
│   └── detail.html                          # Rincian 5 indikator per puskesmas
│
└── uploads/                                 # Direktori penampung unggahan sementara
```

---

## 🛠️ Panduan Menjalankan Sistem di Komputer Lokal

### 1. Clone Repositori
```bash
git clone https://github.com/aqilahigenea/TB-ML.git
cd TB-ML
```

### 2. Buat dan Aktifkan Virtual Environment
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Pasang Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Server Flask
```bash
python app.py
```

Buka peramban (*browser*) Anda dan akses alamat:
```
http://127.0.0.1:5000
```

---

## 👥 Tim Pengembang (Kelompok 8)

* **Dhyva Aulia Hendri** — *Problem Definition, Data Collection, EDA, Preprocessing, Feature Engineering.*
* **Madani Fitri Nur Hidayati** — *Data Splitting, Model Selection, Model Training, Hyperparameter Tuning, Backend Integration.*
* **Aqila Higenea Taufik** — *Model Evaluation & Visualization, Deployment & Monitoring, Frontend DSS UI.*
