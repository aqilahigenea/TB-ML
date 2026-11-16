# app.py
"""Flask Web Application for Stunting Decision Support System (DSS) Kota Padang.

Tugas Besar Machine Learning - Kelompok 8, Universitas Andalas.
"""

import os
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from model_helper import (
    cek_pergeseran_indikator,
    load_model,
    proses_file_baru,
    prediksi_satu_puskesmas,
)
import pandas as pd

app = Flask(__name__)
app.secret_key = 'kunci-rahasia-stunting-kelompok-8'
app.config['UPLOAD_FOLDER'] = os.path.join(
    os.path.dirname(__file__), 'uploads'
)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Muat paket model sekali di awal
MODEL_PAKET = load_model()


def baca_data_acuan():
  """Membaca data acuan puskesmas dan kecamatan dengan proteksi kolom."""
  excel_path = os.path.join(
      os.path.dirname(__file__),
      'data',
      'Tabel_Final_Web_DSS_Puskesmas_2026.xlsx',
  )
  df_puskesmas = pd.read_excel(excel_path, sheet_name='Puskesmas')
  df_kecamatan = pd.read_excel(excel_path, sheet_name='Kecamatan')

  if 'Peringkat_Urgensi' not in df_puskesmas.columns:
    if 'Peringkat_Kota' in df_puskesmas.columns:
      df_puskesmas['Peringkat_Urgensi'] = df_puskesmas['Peringkat_Kota']
    else:
      df_puskesmas = df_puskesmas.sort_values(
          'Skor_Urgensi', ascending=False
      ).reset_index(drop=True)
      df_puskesmas['Peringkat_Urgensi'] = range(1, len(df_puskesmas) + 1)

  if 'Tingkat_Urgensi' not in df_puskesmas.columns:
    df_puskesmas['Tingkat_Urgensi'] = [
        'Tingkat 1 - Sangat Tinggi'
        if r <= 8
        else ('Tingkat 2 - Sedang' if r <= 16 else 'Tingkat 3 - Rutin')
        for r in df_puskesmas['Peringkat_Urgensi']
    ]

  # Proteksi kolom rekapitulasi kecamatan
  t1_map = (
      df_puskesmas[df_puskesmas['Tingkat_Urgensi'].str.contains('Tingkat 1')]
      .groupby('Kecamatan')
      .size()
      .to_dict()
  )
  t2_map = (
      df_puskesmas[df_puskesmas['Tingkat_Urgensi'].str.contains('Tingkat 2')]
      .groupby('Kecamatan')
      .size()
      .to_dict()
  )
  t3_map = (
      df_puskesmas[df_puskesmas['Tingkat_Urgensi'].str.contains('Tingkat 3')]
      .groupby('Kecamatan')
      .size()
      .to_dict()
  )

  df_kecamatan['Tingkat_1'] = df_kecamatan['Kecamatan'].map(
      lambda k: t1_map.get(k, 0)
  )
  df_kecamatan['Tingkat_2'] = df_kecamatan['Kecamatan'].map(
      lambda k: t2_map.get(k, 0)
  )
  df_kecamatan['Tingkat_3'] = df_kecamatan['Kecamatan'].map(
      lambda k: t3_map.get(k, 0)
  )

  return df_puskesmas, df_kecamatan


@app.route('/')
def index():
  """Halaman Utama: Dashboard 24 Puskesmas Data Acuan."""
  df_puskesmas, df_kecamatan = baca_data_acuan()

  puskesmas_list = df_puskesmas.to_dict(orient='records')
  kecamatan_list = df_kecamatan.to_dict(orient='records')

  # Statistik Ringkas
  total_puskesmas = len(puskesmas_list)
  jml_tingkat1 = sum(
      1 for p in puskesmas_list if 'Tingkat 1' in str(p['Tingkat_Urgensi'])
  )
  jml_tingkat2 = sum(
      1 for p in puskesmas_list if 'Tingkat 2' in str(p['Tingkat_Urgensi'])
  )
  jml_tingkat3 = sum(
      1 for p in puskesmas_list if 'Tingkat 3' in str(p['Tingkat_Urgensi'])
  )
  jml_pasti = sum(1 for p in puskesmas_list if p['Status_Kepastian'] == 'Pasti')

  stats = {
      'total': total_puskesmas,
      't1': jml_tingkat1,
      't2': jml_tingkat2,
      't3': jml_tingkat3,
      'pasti': jml_pasti,
      'belum_pasti': total_puskesmas - jml_pasti,
  }

  return render_template(
      'index.html',
      puskesmas=puskesmas_list,
      kecamatan=kecamatan_list,
      stats=stats,
  )


@app.route('/upload', methods=['GET', 'POST'])
def upload():
  """Halaman Unggah File BNBA Bulan Baru."""
  if request.method == 'POST':
    if 'file' not in request.files:
      flash('Tidak ada berkas yang dipilih.', 'danger')
      return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
      flash('Silakan pilih berkas Excel terlebih dahulu.', 'warning')
      return redirect(request.url)

    if file and file.filename.endswith(('.xlsx', '.xls')):
      file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
      file.save(file_path)

      try:
        # Proses file baru dengan model
        df_hasil = proses_file_baru(file_path, MODEL_PAKET)
        drift_list = cek_pergeseran_indikator(df_hasil, MODEL_PAKET)

        hasil_list = df_hasil.to_dict(orient='records')
        return render_template(
            'hasil.html',
            hasil=hasil_list,
            drift=drift_list,
            nama_file=file.filename,
        )
      except Exception as e:
        flash(f'Terjadi kendala saat membaca data: {str(e)}', 'danger')
        return redirect(request.url)
    else:
      flash(
          'Format berkas harus Microsoft Excel (.xlsx) standar e-PPGBM.',
          'danger',
      )
      return redirect(request.url)

  return render_template('upload.html')


@app.route('/puskesmas/<nama>')
def detail_puskesmas(nama):
  """Halaman Detail Profil Satu Puskesmas."""
  df_puskesmas, _ = baca_data_acuan()
  row = df_puskesmas[
      df_puskesmas['Puskesmas'].str.upper() == nama.strip().upper()
  ]

  if row.empty:
    flash(f'Puskesmas {nama} tidak ditemukan.', 'warning')
    return redirect(url_for('index'))

  p_data = row.iloc[0].to_dict()
  rerata_kota = (
      df_puskesmas[MODEL_PAKET['features']].mean().round(2).to_dict()
  )

  return render_template('detail.html', p=p_data, rerata=rerata_kota)


@app.route('/cek-manual', methods=['GET', 'POST'])
def cek_manual():
  """Halaman Cek Manual / Simulasi Satu Puskesmas."""
  hasil = None
  input_data = {}
  fts = MODEL_PAKET['features']
  ref_rerata = MODEL_PAKET.get('referensi_fitur', {}).get('rerata', {})
  if not ref_rerata:
    scaler = MODEL_PAKET['pipeline'].named_steps['scaler']
    ref_rerata = dict(zip(fts, [round(float(m), 2) for m in scaler.mean_]))

  if request.method == 'POST':
    try:
      nama_puskesmas = request.form.get(
          'nama_puskesmas', 'Puskesmas Simulasi'
      ).strip()
      if not nama_puskesmas:
        nama_puskesmas = 'Puskesmas Simulasi'

      fitur_input = {}
      for f in fts:
        val = request.form.get(f, '').replace(',', '.')
        fitur_input[f] = float(val)

      hasil = prediksi_satu_puskesmas(fitur_input, MODEL_PAKET)
      hasil['nama_puskesmas'] = nama_puskesmas
      input_data = fitur_input
      flash('Simulasi berhasil dihitung!', 'success')
    except Exception as e:
      flash(f'Harap isi semua kolom dengan angka yang valid: {e}', 'danger')

  return render_template(
      'cek_manual.html',
      hasil=hasil,
      input_data=input_data,
      features=fts,
      rerata_kota=ref_rerata,
  )


@app.route('/informasi-model')
def informasi_model():
  """Halaman Informasi Metrik & Keterbatasan Model."""
  return render_template('informasi.html')


@app.route('/ekspor')
def ekspor():
  """Unduh Berkas Excel Hasil Rekapitulasi."""
  excel_path = os.path.join(
      os.path.dirname(__file__),
      'data',
      'Tabel_Final_Web_DSS_Puskesmas_2026.xlsx',
  )
  return send_file(
      excel_path,
      as_attachment=True,
      download_name='Tabel_Prioritas_Stunting_Padang_2026.xlsx',
  )


if __name__ == '__main__':
  app.run(debug=True, port=5000)
