# model_helper.py
"""Helper functions for Stunting Decision Support System (DSS) Kota Padang.

Handles BNBA Excel processing, indicator calculations, and ML model inference.
"""

import os
import joblib
import numpy as np
import pandas as pd

# Kamus Sasaran Balita & % Bumil KEK per Puskesmas (Rekap Resmi Dinkes Kota Padang)
SASARAN_DICT = {
    'IKUR KOTO': 1194,
    'ANAK AIR': 2106,
    'RAWANG': 1186,
    'AIR TAWAR': 651,
    'SEBERANG PADANG': 643,
    'PADANG PASIR': 1446,
    'NANGGALO': 1740,
    'LUBUK KILANGAN': 4276,
    'BUNGUS': 1872,
    'ALAI': 2107,
    'AIR DINGIN': 3234,
    'TUNGGUL HITAM': 2423,
    'PAUH': 3136,
    'PARAK KARAKAH': 1398,
    'ANDALAS': 3261,
    'PEMANCUNGAN': 1237,
    'AMBACANG': 2345,
    'BELIMBING': 3653,
    'KURANJI': 2126,
    'LUBUK BEGALUNG': 4483,
    'LAPAI': 986,
    'LB.BUAYA': 5818,
    'PEGAMBIRAN': 5251,
    'ULAK KARANG': 934,
}

BUMIL_KEK_DICT = {
    'IKUR KOTO': 15.7,
    'ANAK AIR': 11.6,
    'RAWANG': 12.0,
    'AIR TAWAR': 9.9,
    'SEBERANG PADANG': 16.4,
    'PADANG PASIR': 12.2,
    'NANGGALO': 11.7,
    'LUBUK KILANGAN': 11.7,
    'BUNGUS': 16.2,
    'ALAI': 25.4,
    'AIR DINGIN': 9.6,
    'TUNGGUL HITAM': 7.2,
    'PAUH': 13.4,
    'PARAK KARAKAH': 10.6,
    'ANDALAS': 11.3,
    'PEMANCUNGAN': 10.4,
    'AMBACANG': 10.7,
    'BELIMBING': 10.2,
    'KURANJI': 10.9,
    'LUBUK BEGALUNG': 9.2,
    'LAPAI': 8.5,
    'LB.BUAYA': 2.9,
    'PEGAMBIRAN': 11.2,
    'ULAK KARANG': 9.7,
}

FITUR_KLASTER = [
    'Kasus per sasaran balita',
    'Persen sangat pendek',
    'Persen stunting + kurus',
    'Persen berat tidak naik',
    'Persen bumil KEK',
]


def load_model():
  """Memuat paket model ML klasterisasi puskesmas."""
  model_path = os.path.join(
      os.path.dirname(__file__), 'model', 'model_klaster_puskesmas_2026.pkl'
  )
  return joblib.load(model_path)


def bersihkan_data_bnba(file_path):
  """Membersihkan data mentah BNBA e-PPGBM sesuai aturan Tahap 4."""
  df = pd.read_excel(file_path, sheet_name='Application List')

  # Filter wilayah Kota Padang jika ada kolom Kab/Kota
  if 'Kab/Kota' in df.columns:
    df = df[df['Kab/Kota'].astype(str).str.strip().str.upper() == 'KOTA PADANG']

  # Standarisasi kolom numerik
  for kol in ['Berat', 'Tinggi', 'ZS BB/U', 'ZS TB/U', 'ZS BB/TB']:
    if kol in df.columns:
      df[kol] = pd.to_numeric(df[kol], errors='coerce')

  # Hitung usia bulan
  df['Tgl Lahir'] = pd.to_datetime(df['Tgl Lahir'], errors='coerce')
  df['Tanggal Pengukuran'] = pd.to_datetime(
      df['Tanggal Pengukuran'], errors='coerce'
  )
  df['Usia_Bulan'] = (
      (df['Tanggal Pengukuran'] - df['Tgl Lahir']).dt.days / 30.4375
  ).round(1)

  # Koreksi gram ke kilogram jika nilai > 100
  df['Berat'] = np.where(df['Berat'] > 100, df['Berat'] / 1000.0, df['Berat'])

  # Buang baris tidak wajar (Tahap 4)
  kondisi_valid = (
      (df['ZS TB/U'].abs() <= 10)
      & (df['Berat'] <= 35)
      & (df['Usia_Bulan'] > 0)
      & (df['Usia_Bulan'] <= 60)
  )
  df = df[kondisi_valid].copy()

  # Rapikan teks nama puskesmas & kecamatan
  df['Pukesmas'] = df['Pukesmas'].astype(str).str.strip().str.upper()
  df['Kec'] = df['Kec'].astype(str).str.strip().str.upper()

  # Cocokkan dengan kamus sasaran
  df = df[df['Pukesmas'].isin(SASARAN_DICT.keys())].copy()

  # Kunci unik anak per bulan
  df = df.drop_duplicates(subset=['Nama', 'Tgl Lahir'])
  return df


def proses_file_baru(file_path, paket_model):
  """Memproses file BNBA bulan baru menjadi tabel peringkat & prediksi klaster."""
  df_bersih = bersihkan_data_bnba(file_path)

  # Agregasi data per puskesmas
  grp = df_bersih.groupby(['Kec', 'Pukesmas'])
  agg = (
      grp.agg(
          Total_Kasus=('Nama', 'count'),
          Total_SP=(
              'TB/U',
              lambda s: (s.astype(str).str.strip() == 'Sangat Pendek').sum(),
          ),
          Total_SW=(
              'BB/TB',
              lambda s: s.astype(str)
              .str.strip()
              .isin(['Gizi Kurang', 'Gizi Buruk'])
              .sum(),
          ),
          Total_BBT=(
              'Naik Berat Badan',
              lambda s: (s.astype(str).str.strip() == 'T').sum(),
          ),
      )
      .reset_index()
      .rename(columns={'Kec': 'Kecamatan', 'Pukesmas': 'Puskesmas'})
  )

  # Tambahkan data sasaran dan hitung 5 indikator utama
  agg['Sasaran_Balita'] = agg['Puskesmas'].map(SASARAN_DICT)
  agg['Kasus per sasaran balita'] = (
      agg['Total_Kasus'] / agg['Sasaran_Balita'] * 100
  ).round(2)
  agg['Persen sangat pendek'] = (
      agg['Total_SP'] / agg['Total_Kasus'] * 100
  ).round(1)
  agg['Persen stunting + kurus'] = (
      agg['Total_SW'] / agg['Total_Kasus'] * 100
  ).round(1)
  agg['Persen berat tidak naik'] = (
      agg['Total_BBT'] / agg['Total_Kasus'] * 100
  ).round(1)
  agg['Persen bumil KEK'] = agg['Puskesmas'].map(BUMIL_KEK_DICT)

  # Hitung Skor Urgensi Komposit (rata-rata z-score 5 indikator)
  X_in = agg[FITUR_KLASTER].astype(float)
  z_scores = (X_in - X_in.mean()) / X_in.std(ddof=0)
  agg['Skor_Urgensi'] = z_scores.mean(axis=1).round(2)

  # Prediksi Klaster K-Means (Mode Relatif)
  inti = paket_model.get('fitur_klaster_model', FITUR_KLASTER)
  z_array = z_scores[inti].to_numpy()
  cluster_ids = paket_model['pipeline'].named_steps['kmeans'].predict(z_array)
  agg['Kelompok_Prioritas'] = pd.Series(cluster_ids).map(paket_model['mapping'])

  # Usulan Kebijakan
  agg['Usulan_Kebijakan'] = agg['Kelompok_Prioritas'].map(
      paket_model.get('rekomendasi', {})
  )

  # Status Kepastian (Pasti vs Belum pasti)
  agg['Status_Kepastian'] = np.where(
      agg['Puskesmas'].isin(paket_model.get('belum_pasti', [])),
      'Belum pasti',
      'Pasti',
  )

  # Urutkan berdasarkan Skor Urgensi (Peringkat 1 s.d. 24)
  agg = agg.sort_values('Skor_Urgensi', ascending=False).reset_index(drop=True)
  agg['Peringkat_Urgensi'] = range(1, len(agg) + 1)

  # Pembagian 3 Tingkat Urgensi Kebijakan
  tingkat = []
  for r in agg['Peringkat_Urgensi']:
    if r <= 8:
      tingkat.append('Tingkat 1 - Urgensi Sangat Tinggi')
    elif r <= 16:
      tingkat.append('Tingkat 2 - Urgensi Sedang')
    else:
      tingkat.append('Tingkat 3 - Pemantauan Rutin')
  agg['Tingkat_Urgensi'] = tingkat

  return agg


def cek_pergeseran_indikator(agg_baru, paket_model):
  """Memantau pergeseran level indikator data baru vs acuan (satuan SD)."""
  fts = paket_model['features']
  if 'referensi_fitur' in paket_model and paket_model['referensi_fitur']:
    ref_rerata = pd.Series(paket_model['referensi_fitur']['rerata'])
    ref_std = pd.Series(paket_model['referensi_fitur']['simpangan_baku'])
  else:
    scaler = paket_model['pipeline'].named_steps['scaler']
    ref_rerata = pd.Series(scaler.mean_, index=fts)
    ref_std = pd.Series(scaler.scale_, index=fts)

  baru_rerata = agg_baru[fts].mean()
  geser = ((baru_rerata - ref_rerata) / ref_std).round(2)

  drift_list = []
  for f in fts:
    val = geser.get(f, 0.0)
    if abs(val) >= 1.0:
      status = 'Kritis'
      warna = 'danger'
    elif abs(val) >= 0.5:
      status = 'Waspada'
      warna = 'warning'
    else:
      status = 'Normal'
      warna = 'success'
    drift_list.append(
        {'indikator': f, 'pergeseran_sd': val, 'status': status, 'warna': warna}
    )
  return drift_list


def prediksi_satu_puskesmas(fitur_input, paket_model):
  """Memprediksi klaster, skor urgensi, dan rekomendasi untuk 1 puskesmas secara manual."""
  fts = paket_model['features']
  # Konversi ke DataFrame berkolom sesuai urutan fitur
  df_input = pd.DataFrame([[float(fitur_input[f]) for f in fts]], columns=fts)

  # Ambil referensi rata-rata dan simpangan baku acuan kota
  if 'referensi_fitur' in paket_model and paket_model['referensi_fitur']:
    ref_rerata = pd.Series(paket_model['referensi_fitur']['rerata'])
    ref_std = pd.Series(paket_model['referensi_fitur']['simpangan_baku'])
  else:
    scaler = paket_model['pipeline'].named_steps['scaler']
    ref_rerata = pd.Series(scaler.mean_, index=fts)
    ref_std = pd.Series(scaler.scale_, index=fts)

  # Hitung z-score dan Skor Urgensi Komposit
  z_scores = ((df_input.iloc[0] - ref_rerata) / ref_std).round(2)
  skor_urgensi = round(float(z_scores.mean()), 2)

  # Prediksi Klaster dengan Pipeline ML (StandardScaler + KMeans)
  cluster_id = int(paket_model['pipeline'].predict(df_input)[0])
  nama_prioritas = paket_model['mapping'].get(
      cluster_id, f'Prioritas {cluster_id + 1}'
  )

  # Usulan Kebijakan Manajerial & Ciri Dominan
  usulan = paket_model.get('rekomendasi', {}).get(nama_prioritas, '-')
  ciri = paket_model.get('ciri', {}).get(nama_prioritas, '-')

  # Penentuan Tingkat Urgensi
  if skor_urgensi > 0.20:
    tingkat_urgensi = 'Tingkat 1 - Sangat Tinggi'
    warna_tingkat = 'danger'
  elif skor_urgensi >= -0.20:
    tingkat_urgensi = 'Tingkat 2 - Sedang'
    warna_tingkat = 'warning'
  else:
    tingkat_urgensi = 'Tingkat 3 - Rutin'
    warna_tingkat = 'success'

  # Status kepastian
  status_kepastian = 'Pasti (Stabil)'

  return {
      'skor_urgensi': skor_urgensi,
      'cluster_id': cluster_id,
      'kelompok_prioritas': nama_prioritas,
      'tingkat_urgensi': tingkat_urgensi,
      'warna_tingkat': warna_tingkat,
      'usulan_kebijakan': usulan,
      'ciri_dominan': ciri,
      'status_kepastian': status_kepastian,
      'z_scores': z_scores.to_dict(),
      'nilai_input': df_input.iloc[0].to_dict(),
      'rerata_kota': ref_rerata.round(2).to_dict(),
  }

