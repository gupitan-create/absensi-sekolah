from datetime import date
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Set Konfigurasi Halaman Web
st.set_page_config(
    page_title="Absensi Siswa Sekolah", page_icon="🏫", layout="centered"
)

# --- KONEKSI KE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)


# Fungsi Membaca Data dari Google Sheets
def load_data():
  try:
    data = conn.read(worksheet="Sheet1", ttl="0s")
    if (
        data.empty
        or list(data.columns) != ["Tanggal", "Kelas", "Nama Siswa", "Status"]
    ):
      return pd.DataFrame(columns=["Tanggal", "Kelas", "Nama Siswa", "Status"])
    return data
  except Exception:
    return pd.DataFrame(columns=["Tanggal", "Kelas", "Nama Siswa", "Status"])


# Fungsi Menyimpan Data ke Google Sheets
def save_data(df):
  conn.update(worksheet="Sheet1", data=df)


# Inisialisasi Data
df_absensi = load_data()

# Data Master Siswa per Kelas
DATA_MASTER_SISWA = {
    "Kelas 1": [
        "ABIZARD ALFARIZI PERMANA",
        "DAVINA BILQIS RAMADHANI",
        "FA’IS NAZWAN SETIAWAN",
        "FARHAN FAHREZA ALFATURIZKY",
        "GIBRAN ALFA RIZQI",
        "KEISYA NOVIA FIRDAUS",
        "KESYA AYU KHALISA",
        "KHALISA AULIA ANJANI",
        "MUHAMAD FAJRIN FEBRIANA FIRMANSYAH",
        "MUHAMMAD ALBASYARI MAULANA",
        "SITI MASIITHOH MUNAWWAROH",
        "TANZILUROHMAN",
        "TIO ARIF AL-PARIZI",
    ],
    "Kelas 2": [
        "ALTHAF ABRISAM",
        "AQILA ALFATUNISA",
        "AQMAR ZAYYAN",
        "DELISHA DZIKRANIA PUTRI",
        "EL-ZAIDAN AFZAL",
        "INDAH SULISTYANI",
        "MUHAMAD FAHMI LUFINO KUSMAYADI",
        "MUHAMMAD SYAHRUL MUBAROK",
        "SHEYRA AZRA NUR AMALIAH",
    ],
    "Kelas 3": [
        "ABDUR ROHIM AHMAD FARHAN MUBAAROK",
        "AULIA NURAENI RAZMY",
        "AZKA NAUFAL RIZQI",
        "AZWA AZZAHRA",
        "DAUD MAULANA ROMADON",
        "FADHLIKAL AZHIM KHOIRI",
        "GASENDRA GANDANA RASYID",
        "HAUFAL FAISAL ARDANA",
        "HILAL KIFAYATUL AKBAR",
        "ISMA NUR INTAN",
        "KAISYAKIRA AQILA RAHMA",
        "PANJI OKTAVIA SAPUTRA",
        "RAIHANA FAKHIRA MUSTOFA",
        "RAYA FITRIANI",
        "RIZA ABDI AL HAKIMI",
        "SYILLA KHANZANIA MUSTHAFA",
    ],
    "Kelas 4": [
        "ABDUL HAYY ISA KAAMIL",
        "ADE TSANI SITI AQILA",
        "ADINDA NUR ADZANI",
        "ADITYA NUGRAHA SAEPUL BAR",
        "ALBI LUTHFI FAHRI",
        "ARSAKHA VIRENDRA ADHYATSA",
        "DAVA PURNAMA PUTRA",
        "DEFHAN AL FARIZZI",
        "MUHAMAD BERYL ARYA RAFFARDHAN",
        "MUHAMAD IBNU KAMIL",
        "MUHAMAD RAFA AZKA PUTRA",
        "MUHAMMAD ABIDZAR ALFARIZQI",
        "NADHIFA ALFIRA",
        "NAURA HASNA RAHMADHANI",
        "TIARA ZAHSY DWI RAMADHANI",
        "ZASKIA ZAINA AWALIA",
    ],
    "Kelas 5": [
        "ABDUL AZIZ ASSIDIQ",
        "AKBAR RIZQY PRATAMA",
        "AZKA MAULANA AL-GHIFARI",
        "AZZALEA TALENTA PUTRI",
        "ERN ZAHIRA AS SHIDQIA",
        "HANUN HALWA NURJANAH",
        "KHAYLANISSA AZZAHRA",
        "QIYA NURAISAH",
        "RAISYA APRILIA FAUJIYAH",
        "RAKA WARSONO",
        "RATIFA INNARA GHAISANI",
        "SALSA KARIMATUN NISWAH",
        "SITI FATIMAH",
    ],
    "Kelas 6": [
        "AKBAR ZAQI MUBAROK",
        "AMJAD AINUL MUBAROK",
        "GAVIN NAGITA RASYID",
        "GHANU RAIGHA FEBRYAN PUTRA",
        "KHAIRUNISA NAYYA FAIRANI",
        "KHALIFA SALSABILA",
        "KHAYIRA NAILAL HUSNA",
        "MUHAMMAD ADITYA ADIYANTO",
        "NABIILAH AKIFATUL ZANNAH",
        "NAUVALIN FIKRIA ROBBANI",
        "NURUL QOLBI",
        "PELISA CAHYA MAHARANI",
        "SEPTIAN PRATAMA",
        "ZIYAD MUHAMMAD FAHRURROJI",
    ],
}

# Header Utama
st.title("🏫 Aplikasi Absensi Siswa MI Sukadana")

# --- SIDEBAR NAVIGASI PERAN ---
st.sidebar.header("📌 Pilih Menu")
menu_pilihan = st.sidebar.radio(
    "Masuk Sebagai:", ["Wali Kelas (Input Absen)", "Admin (Rekap & Kelola)"]
)

# =========================================================
# 1. HALAMAN WALI KELAS (INPUT PER SISWA)
# =========================================================
if menu_pilihan == "Wali Kelas (Input Absen)":
  st.subheader("📝 Form Input Absensi Harian")

  col_k1, col_k2 = st.columns(2)
  with col_k1:
    kelas_terpilih = st.selectbox(
        "Pilih Kelas Anda:", list(DATA_MASTER_SISWA.keys())
    )
  with col_k2:
    tgl_absensi = st.date_input("Tanggal Absensi:", value=date.today())

  st.markdown("---")
  daftar_siswa = DATA_MASTER_SISWA[kelas_terpilih]
  st.write(f"**Daftar Siswa {kelas_terpilih}** ({len(daftar_siswa)} Siswa)")
  st.info(
      "Silakan pilih status kehadiran (Hadir / Sakit / Izin / Alpa) di bawah"
      " nama masing-masing siswa:"
  )

  tgl_str = tgl_absensi.strftime("%d-%m-%Y")

  df_existing = pd.DataFrame()
  if not df_absensi.empty:
    df_existing = df_absensi[
        (df_absensi["Tanggal"] == tgl_str)
        & (df_absensi["Kelas"] == kelas_terpilih)
    ]

  status_input = {}

  with st.form(key=f"form_absen_{kelas_terpilih}_{tgl_str}"):
    for i, siswa in enumerate(daftar_siswa, 1):
      status_awal_idx = 0
      options_list = ["Hadir", "Sakit", "Izin", "Alpa"]

      if not df_existing.empty:
        match = df_existing[df_existing["Nama Siswa"] == siswa]
        if not match.empty:
          val = match.iloc[0]["Status"]
          if val in options_list:
            status_awal_idx = options_list.index(val)

      st.markdown(f"**{i}. {siswa}**")
      status_input[siswa] = st.radio(
          f"Status {siswa}",
          options_list,
          index=status_awal_idx,
          horizontal=True,
          key=f"radio_{kelas_terpilih}_{siswa}",
          label_visibility="collapsed",
      )
      st.markdown("---")

    btn_simpan = st.form_submit_button("💾 Simpan Absensi", type="primary")

  if btn_simpan:
    with st.spinner("Menyimpan data ke Google Sheets..."):
      data_baru = []
      for siswa, status in status_input.items():
        data_baru.append({
            "Tanggal": tgl_str,
            "Kelas": kelas_terpilih,
            "Nama Siswa": siswa,
            "Status": status,
        })

      df_baru = pd.DataFrame(data_baru)

      if not df_absensi.empty:
        df_absensi = df_absensi[
            ~(
                (df_absensi["Tanggal"] == tgl_str)
                & (df_absensi["Kelas"] == kelas_terpilih)
            )
        ]

      df_absensi = pd.concat([df_absensi, df_baru], ignore_index=True)
      save_data(df_absensi)

      st.success(
          f"✅ Absensi {kelas_terpilih} tanggal {tgl_str} berhasil disimpan!"
      )
      st.rerun()

# =========================================================
# 2. HALAMAN ADMIN
# =========================================================
else:
  st.subheader("🔐 Login Admin")
  PASSWORD_ADMIN = "admin123"

  input_password = st.text_input(
      "Masukkan Password Admin:", type="password", key="admin_pass_input"
  )

  if input_password == PASSWORD_ADMIN:
    st.success("✅ Password benar. Selamat datang, Admin!")
    st.markdown("---")
    st.subheader("📊 Halaman Rekap Data & Kelola")

    if df_absensi.empty:
      st.info("Belum ada data absensi di Google Sheets.")
    else:
      col1, col2 = st.columns(2)
      with col1:
        pilihan_kelas = st.selectbox(
            "Filter Kelas:", ["Semua Kelas"] + list(DATA_MASTER_SISWA.keys())
        )
      with col2:
        daftar_tanggal_tersedia = ["Semua Tanggal"] + sorted(
            df_absensi["Tanggal"].unique().tolist()
        )
        pilihan_tanggal = st.selectbox(
            "Filter Tanggal:", daftar_tanggal_tersedia
        )

      df_tampil = df_absensi.copy()
      if pilihan_kelas != "Semua Kelas":
        df_tampil = df_tampil[df_tampil["Kelas"] == pilihan_kelas]
      if pilihan_tanggal != "Semua Tanggal":
        df_tampil = df_tampil[df_tampil["Tanggal"] == pilihan_tanggal]

      st.dataframe(df_tampil, use_container_width=True)

      csv_data = df_tampil.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="📥 Download Data Absensi (CSV)",
          data=csv_data,
          file_name=f"rekap_absensi_{pilihan_kelas.lower().replace(' ', '_')}_{pilihan_tanggal}.csv",
          mime="text/csv",
      )

      st.markdown("---")
      st.write("### 🗑️ Hapus Data Absensi")
      with st.expander("Klik di sini untuk menghapus data"):
        st.warning("Perhatian: Data yang dihapus tidak dapat dikembalikan.")

        daftar_tgl = df_absensi["Tanggal"].unique()
        tgl_hapus = st.selectbox("Pilih Tanggal:", daftar_tgl, key="hapus_tgl")
        kelas_hapus = st.selectbox(
            "Pilih Kelas:",
            ["Semua Kelas"] + list(DATA_MASTER_SISWA.keys()),
            key="hapus_kelas",
        )

        if st.button("🔴 Hapus Data Terpilih", type="primary"):
          with st.spinner("Menghapus data..."):
            if kelas_hapus == "Semua Kelas":
              df_absensi = df_absensi[df_absensi["Tanggal"] != tgl_hapus]
            else:
              df_absensi = df_absensi[
                  ~(
                      (df_absensi["Tanggal"] == tgl_hapus)
                      & (df_absensi["Kelas"] == kelas_hapus)
                  )
              ]

            save_data(df_absensi)
            st.success(
                f"Data tanggal {tgl_hapus} ({kelas_hapus}) berhasil dihapus!"
            )
            st.rerun()

  elif input_password == "":
    st.info("Silakan masukkan password admin di atas.")
  else:
    st.error("❌ Password salah!")