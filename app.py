from datetime import date
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
from gspread_formatting import format_cell_range, CellFormat

# ---------------------------------------------------------
# KONFIGURASI APLIKASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="Absensi Siswa MI Sukadana",
    page_icon="🏫",
    layout="centered",
)

KOLOM = ["Tanggal", "Kelas", "Nama Siswa", "Status"]
STATUS_ABSENSI = ["Hadir", "Sakit", "Izin", "Alpa"]
PASSWORD_ADMIN = st.secrets.get("admin", {}).get("password", "admin123")


def get_connection():
    """Buat koneksi GSheets. Tanpa cache manual agar secrets selalu dibaca ulang."""
    return st.connection("gsheets", type=GSheetsConnection)


def cek_private_key():
    """Diagnostik ringan: pastikan private_key di secrets.toml berformat PEM."""
    try:
        pk = st.secrets["connections"]["gsheets"]["private_key"]
    except Exception:
        return False, "Bagian [connections.gsheets] tidak ditemukan di secrets.toml."
    if not pk:
        return False, "private_key kosong."
    if "-----BEGIN PRIVATE KEY-----" not in pk or "-----END PRIVATE KEY-----" not in pk:
        return False, "private_key tidak memiliki header/footer PEM yang benar."
    if "\\n" not in pk and "\n" not in pk:
        return False, "private_key tidak memiliki newline; format salah."
    return True, f"private_key OK ({len(pk)} karakter)."


def kosongkan_data():
    return pd.DataFrame(columns=KOLOM)


def rapikan_data(data):
    """Menormalkan data agar header/kolom dari Google Sheets konsisten."""
    if data is None or data.empty:
        return kosongkan_data()

    data = data.copy()
    data.columns = [str(kolom).strip() for kolom in data.columns]

    if set(KOLOM).issubset(set(data.columns)):
        data = data[KOLOM]
    else:
        return kosongkan_data()

    data = data.dropna(how="all")
    for kolom in KOLOM:
        data[kolom] = data[kolom].fillna("").astype(str).str.strip()
    return data.reset_index(drop=True)


def load_data():
    """Baca data. Tandai status koneksi di session_state."""
    try:
        conn = get_connection()
        data = conn.read(worksheet="Sheet1", ttl=0)
        st.session_state["gsheets_ok"] = True
        return rapikan_data(data)
    except Exception as exc:
        st.session_state["gsheets_ok"] = False
        st.error(
            "Gagal membaca Google Sheets. Periksa .streamlit/secrets.toml, "
            "akses service account, nama worksheet 'Sheet1', dan koneksi internet."
        )
        with st.expander("Detail kesalahan"):
            st.code(str(exc))
        return kosongkan_data()


def save_data(data):
    """Simpan data dengan urutan kolom tetap, lalu atur format rata kiri."""
    data = rapikan_data(data)
    conn = get_connection()
    conn.update(worksheet="Sheet1", data=data[KOLOM])
    st.session_state["gsheets_ok"] = True
    
    # --- MENGATUR FORMAT RATA KIRI OTOMATIS SETELAH SIMPAN ---
    try:
        gc = gspread.service_account_from_dict(st.secrets["connections"]["gsheets"])
        sh = gc.open("Data Absensi MI Sukadana")
        ws = sh.worksheet("Sheet1")
        
        # Format rata kiri untuk kolom Tanggal, Kelas, dan Nama Siswa (Kolom A, B, C)
        format_cell_range(ws, 'A2:C10000', CellFormat(horizontalAlignment='LEFT'))
        
        # Format rata tengah untuk kolom Status (Kolom D) agar lebih rapi
        format_cell_range(ws, 'D2:D10000', CellFormat(horizontalAlignment='CENTER'))
        
    except Exception as e:
        # Jika gagal format, data tetap tersimpan dan error tidak ditampilkan ke user
        print(f"Peringatan: Gagal mengatur format sel: {e}")
    # ---------------------------------------------------------


def tampilkan_error(exc, tindakan="menyimpan data"):
    st.error(f"Gagal {tindakan}. Periksa koneksi dan konfigurasi Google Sheets.")
    with st.expander("Detail kesalahan"):
        st.code(str(exc))


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


st.title("🏫 Aplikasi Absensi Siswa MI Sukadana")
st.caption("Pencatatan kehadiran harian siswa")

with st.sidebar:
    st.header("📌 Pilih Menu")
    menu_pilihan = st.radio(
        "Masuk sebagai:",
        ["Wali Kelas (Input Absen)", "Admin (Rekap & Kelola)"],
    )
    st.markdown("---")
    with st.expander("🩺 Diagnostik koneksi"):
        ok, pesan = cek_private_key()
        if ok:
            st.success(pesan)
        else:
            st.error(pesan)
        st.caption("Status baca terakhir: "
                   + ("Berhasil" if st.session_state.get("gsheets_ok") else "Gagal/Belum"))

# Baca data pada setiap rerun agar perubahan terbaru terlihat.
df_absensi = load_data()

if menu_pilihan == "Wali Kelas (Input Absen)":
    st.subheader("📝 Form Input Absensi Harian")
    col_k1, col_k2 = st.columns(2)

    with col_k1:
        kelas_terpilih = st.selectbox(
            "Pilih Kelas Anda:", list(DATA_MASTER_SISWA.keys())
        )
    with col_k2:
        tgl_absensi = st.date_input("Tanggal Absensi:", value=date.today())

    tgl_str = tgl_absensi.strftime("%d-%m-%Y")
    daftar_siswa = DATA_MASTER_SISWA[kelas_terpilih]

    st.markdown("---")
    st.write(f"**Daftar Siswa {kelas_terpilih}** ({len(daftar_siswa)} siswa)")
    st.info("Pilih status kehadiran setiap siswa, lalu tekan Simpan Absensi.")

    df_existing = kosongkan_data()
    if not df_absensi.empty:
        df_existing = df_absensi[
            (df_absensi["Tanggal"] == tgl_str)
            & (df_absensi["Kelas"] == kelas_terpilih)
        ]

    status_input = {}
    with st.form(key=f"form_absen_{kelas_terpilih}_{tgl_absensi.isoformat()}"):
        for i, siswa in enumerate(daftar_siswa, start=1):
            status_awal_idx = 0
            match = df_existing[df_existing["Nama Siswa"] == siswa]
            if not match.empty:
                status_lama = str(match.iloc[0]["Status"]).strip()
                if status_lama in STATUS_ABSENSI:
                    status_awal_idx = STATUS_ABSENSI.index(status_lama)

            st.markdown(f"**{i}. {siswa}**")
            status_input[siswa] = st.radio(
                f"Status {siswa}",
                options=STATUS_ABSENSI,
                index=status_awal_idx,
                horizontal=True,
                key=f"radio_{kelas_terpilih}_{tgl_absensi.isoformat()}_{i}",
                label_visibility="collapsed",
            )
            st.divider()

        btn_simpan = st.form_submit_button("💾 Simpan Absensi", type="primary")

    if btn_simpan:
        if not st.session_state.get("gsheets_ok", False):
            st.error(
                "Tidak bisa menyimpan: koneksi Google Sheets belum berhasil dibaca. "
                "Perbaiki koneksi dulu agar data lama tidak terhapus."
            )
            st.stop()

        data_baru = pd.DataFrame(
            [
                {
                    "Tanggal": tgl_str,
                    "Kelas": kelas_terpilih,
                    "Nama Siswa": siswa,
                    "Status": status,
                }
                for siswa, status in status_input.items()
            ],
            columns=KOLOM,
        )
        if not df_absensi.empty:
            df_absensi = df_absensi[
                ~(
                    (df_absensi["Tanggal"] == tgl_str)
                    & (df_absensi["Kelas"] == kelas_terpilih)
                )
            ]
        hasil = pd.concat([df_absensi, data_baru], ignore_index=True)
        try:
            with st.spinner("Menyimpan data ke Google Sheets..."):
                save_data(hasil)
            st.success(f"Absensi {kelas_terpilih} tanggal {tgl_str} berhasil disimpan.")
            st.rerun()
        except Exception as exc:
            tampilkan_error(exc, "menyimpan absensi")

else:
    st.subheader("🔐 Login Admin")
    input_password = st.text_input(
        "Masukkan Password Admin:", type="password", key="admin_pass_input"
    )

    if input_password and input_password == PASSWORD_ADMIN:
        st.success("Password benar. Selamat datang, Admin!")
        st.markdown("---")
        st.subheader("📊 Rekap Data & Kelola")

        if df_absensi.empty:
            st.info("Belum ada data absensi di Google Sheets.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                pilihan_kelas = st.selectbox(
                    "Filter Kelas:",
                    ["Semua Kelas"] + list(DATA_MASTER_SISWA.keys()),
                )
            with col2:
                daftar_tanggal = sorted(
                    df_absensi["Tanggal"].dropna().astype(str).unique().tolist()
                )
                pilihan_tanggal = st.selectbox(
                    "Filter Tanggal:", ["Semua Tanggal"] + daftar_tanggal
                )

            df_tampil = df_absensi.copy()
            if pilihan_kelas != "Semua Kelas":
                df_tampil = df_tampil[df_tampil["Kelas"] == pilihan_kelas]
            if pilihan_tanggal != "Semua Tanggal":
                df_tampil = df_tampil[df_tampil["Tanggal"] == pilihan_tanggal]

            st.dataframe(df_tampil, use_container_width=True, hide_index=True)
            csv_data = df_tampil.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Download Data Absensi (CSV)",
                data=csv_data,
                file_name=(
                    f"rekap_absensi_{pilihan_kelas.lower().replace(' ', '_')}_"
                    f"{pilihan_tanggal.lower().replace(' ', '_')}.csv"
                ),
                mime="text/csv",
            )

            st.markdown("---")
            st.subheader("🗑️ Hapus Data Absensi")
            with st.expander("Klik di sini untuk menghapus data"):
                st.warning("Perhatian: data yang dihapus tidak dapat dikembalikan.")
                tanggal_hapus = st.selectbox(
                    "Pilih Tanggal:",
                    sorted(df_absensi["Tanggal"].dropna().astype(str).unique().tolist()),
                    key="hapus_tgl",
                )
                kelas_hapus = st.selectbox(
                    "Pilih Kelas:",
                    ["Semua Kelas"] + list(DATA_MASTER_SISWA.keys()),
                    key="hapus_kelas",
                )
                konfirmasi = st.checkbox(
                    "Saya yakin ingin menghapus data yang dipilih.",
                    key="konfirmasi_hapus",
                )
                if st.button(
                    "🔴 Hapus Data Terpilih",
                    type="primary",
                    disabled=not konfirmasi,
                ):
                    if not st.session_state.get("gsheets_ok", False):
                        st.error(
                            "Tidak bisa menghapus: koneksi Google Sheets belum berhasil dibaca."
                        )
                        st.stop()
                    if kelas_hapus == "Semua Kelas":
                        sisa = df_absensi[df_absensi["Tanggal"] != tanggal_hapus]
                    else:
                        sisa = df_absensi[
                            ~(
                                (df_absensi["Tanggal"] == tanggal_hapus)
                                & (df_absensi["Kelas"] == kelas_hapus)
                            )
                        ]
                    try:
                        with st.spinner("Menghapus data..."):
                            save_data(sisa)
                        st.success(
                            f"Data tanggal {tanggal_hapus} ({kelas_hapus}) berhasil dihapus."
                        )
                        st.rerun()
                    except Exception as exc:
                        tampilkan_error(exc, "menghapus data")
    elif input_password == "":
        st.info("Silakan masukkan password admin di atas.")
    else:
        st.error("Password admin salah.")