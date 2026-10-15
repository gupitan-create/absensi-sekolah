from datetime import datetime
import pandas as pd
import streamlit as st

# 1. Konfigurasi Halaman (Mobile-Friendly)
st.set_page_config(
    page_title="Absensi Siswa SD",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Inisialisasi Database Penyimpanan di Session State
if "data_absensi" not in st.session_state:
    st.session_state["data_absensi"] = pd.DataFrame(
        columns=["Tanggal", "Kelas", "Nama Siswa", "Status", "Waktu Input"]
    )

# 3. Data Master Siswa per Kelas
DATA_MASTER_SISWA = {
    "Kelas 1": ["Ahmad Fauzi", "Budi Santoso", "Citra Dewi", "Deni Pratama"],
    "Kelas 2": ["Eka Putri", "Fajar Nugraha", "Gita Gutawa", "Hadi Wijaya"],
    "Kelas 3": ["Indah Sari", "Joko Susilo", "Kartika Putri", "Lestari Ayu"],
    "Kelas 4": ["Muhammad Ali", "Nanda Kurnia", "Oki Setiawan", "Putri Utami"],
    "Kelas 5": ["Qori Rizki", "Rian Hidayat", "Siti Rahma", "Tono Sudirjo"],
    "Kelas 6": ["Umar Faruq", "Vina Pandu", "Wahyu Hidayat", "Zahra Annisa"],
}

# 4. Header Aplikasi
st.title("📝 Absensi Harian Siswa")
st.caption("Aplikasi Input Kehadiran Siswa Kelas 1 - 6")

# 5. Tab Navigasi: Input Absensi vs Rekap Data
tab1, tab2 = st.tabs(["📌 Input Absensi", "📊 Rekap Data"])

with tab1:
    st.subheader("Form Input Kehadiran")

    # Pilih Tanggal dan Kelas
    col_tgl, col_kls = st.columns(2)
    with col_tgl:
        tanggal_input = st.date_input("Tanggal", datetime.today())
    with col_kls:
        kelas_pilihan = st.selectbox(
            "Pilih Kelas", list(DATA_MASTER_SISWA.keys())
        )

    daftar_siswa = DATA_MASTER_SISWA.get(kelas_pilihan, [])

    st.markdown("---")
    st.markdown(
        f"**Daftar Siswa {kelas_pilihan}** ({len(daftar_siswa)} Siswa)"
    )

    # Form Isian Absensi
    with st.form(key="form_input_absensi"):
        status_input = {}

        for nama in daftar_siswa:
            st.write(f"👤 **{nama}**")
            # Tombol Pilihan Status Kehadiran
            status_input[nama] = st.radio(
                label=f"Status untuk {nama}",
                options=["Hadir", "Sakit", "Izin", "Alpa"],
                index=0,
                horizontal=True,
                label_visibility="collapsed",
                key=f"radio_{kelas_pilihan}_{nama}",
            )
            st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

        tombol_simpan = st.form_submit_button(
            "💾 Simpan Absensi Hari Ini", use_container_width=True
        )

        if tombol_simpan:
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Format Data Baru
            data_baru = []
            for nama, status in status_input.items():
                data_baru.append(
                    {
                        "Tanggal": str(tanggal_input),
                        "Kelas": kelas_pilihan,
                        "Nama Siswa": nama,
                        "Status": status,
                        "Waktu Input": waktu_sekarang,
                    }
                )

            df_baru = pd.DataFrame(data_baru)

            # Hapus data lama jika tanggal & kelas yang sama sudah pernah diinput sebelumnya (mencegah duplikasi)
            df_existing = st.session_state["data_absensi"]
            df_filtered = df_existing[
                ~(
                    (df_existing["Tanggal"] == str(tanggal_input))
                    & (df_existing["Kelas"] == kelas_pilihan)
                )
            ]

            # Gabungkan dan Simpan
            st.session_state["data_absensi"] = pd.concat(
                [df_filtered, df_baru], ignore_index=True
            )

            st.success(
                f"✅ Absensi {kelas_pilihan} tanggal {tanggal_input} berhasil disimpan!"
            )
            st.balloons()

with tab2:
    st.subheader("📊 Rekapitulasi Absensi")

    df_rekap = st.session_state["data_absensi"]

    if df_rekap.empty:
        st.info(
            "Belum ada data absensi yang disimpan. Silakan isi absensi di menu **Input Absensi**."
        )
    else:
        # Filter Tampilan Rekap
        filter_kelas = st.selectbox(
            "Filter Berdasarkan Kelas",
            ["Semua Kelas"] + list(DATA_MASTER_SISWA.keys()),
        )

        if filter_kelas != "Semua Kelas":
            df_tampil = df_rekap[df_rekap["Kelas"] == filter_kelas]
        else:
            df_tampil = df_rekap

        st.dataframe(df_tampil, use_container_width=True, hide_index=True)

        # Download File Excel/CSV
        csv_data = df_tampil.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Data Absensi (CSV)",
            data=csv_data,
            file_name=f"rekap_absensi_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )