from datetime import date
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# Set Konfigurasi Halaman Web
st.set_page_config(
    page_title="Absensi Siswa Sekolah", page_icon="🏫", layout="centered"
)

# --- KONEKSI KE GOOGLE SHEETS MENGGUNAKAN GSPREAD ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def get_gsheet_client():
  # Membaca Service Account dari st.secrets["connections"]["gsheets"]
  credentials_info = st.secrets["connections"]["gsheets"]
  creds = Credentials.from_service_account_info(
      credentials_info, scopes=SCOPES
  )
  return gspread.authorize(creds)


def get_worksheet():
  client = get_gsheet_client()
  spreadsheet_name = st.secrets["connections"]["gsheets"].get(
      "spreadsheet", "Absensi Siswa"
  )
  sh = client.open(spreadsheet_name)
  return sh.sheet1


def load_data():
  try:
    ws = get_worksheet()
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    if (
        df.empty
        or list(df.columns) != ["Tanggal", "Kelas", "Nama Siswa", "Status"]
    ):
      return pd.DataFrame(columns=["Tanggal", "Kelas", "Nama Siswa", "Status"])
    return df
  except Exception:
    return pd.DataFrame(columns=["Tanggal", "Kelas", "Nama Siswa", "Status"])


def save_data(df):
  ws = get_worksheet()
  ws.clear()
  # Update header dan isi data
  ws.update([df.columns.values.tolist()] + df.values.tolist())


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
# 1. HALAMAN WALI KELAS
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

  tgl_str = tgl_absensi.strftime("%d-%m-%Y")

  df_existing = pd.DataFrame()
  if not df_absensi.empty:
    df_existing = df_absensi[
        (df_absensi["Tanggal"] == tgl_str)
        & (df_absensi["Kelas"] == kelas_terpilih)
    ]

  data_template = []
  for siswa in daftar_siswa:
    status_awal = "Hadir"
    if not df_existing.empty:
      match = df_existing[df_existing["Nama Siswa"] == siswa]
      if not match.empty:
        status_awal = match.iloc[0]["Status"]

    data_template.append({
        "Tanggal": tgl_str,
        "Kelas": kelas_terpilih,
        "Nama Siswa": siswa,
        "Status": status_awal,
    })

  df_input = pd.DataFrame(data_template)

  edited_df = st.data_editor(
      df_input,
      column_config={
          "Tanggal": st.column_config.TextColumn("Tanggal", disabled=True),
          "Kelas": st.column_config.TextColumn("Kelas", disabled=True),
          "Nama Siswa": st.column_config.TextColumn("Nama Siswa", disabled=True),
          "Status": st.column_config.SelectboxColumn(
              "Status Kehadiran",
              options=["Hadir", "Sakit", "Izin", "Alpa"],
              required=True,
          ),
      },
      hide_index=True,
      use_container_width=True,
      key=f"editor_{kelas_terpilih}_{tgl_str}",
  )

  if st.button("💾 Simpan Absensi", type="primary"):
    with st.spinner("Menyimpan data ke Google Sheets..."):
      if not df_absensi.empty:
        df_absensi = df_absensi[
            ~(
                (df_absensi["Tanggal"] == tgl_str)
                & (df_absensi["Kelas"] == kelas_terpilih)
            )
        ]

      df_absensi = pd.concat([df_absensi, edited_df], ignore_index=True)
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
        st.warning(
            "Perhatian: Data yang dihapus dari Google Sheets tidak dapat"
            " dikembalikan."
        )

        daftar_tgl = df_absensi["Tanggal"].unique()
        tgl_hapus = st.selectbox("Pilih Tanggal:", daftar_tgl, key="hapus_tgl")
        kelas_hapus = st.selectbox(
            "Pilih Kelas:",
            ["Semua Kelas"] + list(DATA_MASTER_SISWA.keys()),
            key="hapus_kelas",
        )

        if st.button("🔴 Hapus Data Terpilih", type="primary"):
          with st.spinner("Menghapus data dari Google Sheets..."):
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