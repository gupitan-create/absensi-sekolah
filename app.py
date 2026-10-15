import streamlit as st
import pandas as pd
from datetime import date
import os

# Set Konfigurasi Halaman Web
st.set_page_config(page_title="Absensi Siswa Sekolah", page_icon="🏫", layout="centered")

# File Penyimpanan Data Local
FILE_DATA = "data_absensi.csv"

# Data Master Siswa per Kelas
DATA_MASTER_SISWA = {
    "Kelas 1": [
        "Ahmad Fauzi",
        "Budi Santoso",
        "Citra Dewi",
        "Deni Pratama",
    ],
    "Kelas 2": [
        "Eka Putri",
        "Fajar Nugraha",
        "Gita Gutawa",
        "Hadi Wijaya",
    ],
    "Kelas 3": [
        "Indah Sari",
        "Joko Susilo",
        "Kartika Putri",
        "Lestari Ayu",
    ],
    "Kelas 4": [
        "Muhammad Ali",
        "Nanda Kurnia",
        "Oki Setiawan",
        "Putri Utami",
    ],
    "Kelas 5": [
        "Qori Rizki",
        "Rian Hidayat",
        "Siti Rahma",
        "Tono Sudirjo",
    ],
    "Kelas 6": [
        "Umar Faruq",
        "Vina Pandu",
        "Wahyu Hidayat",
        "Zahra Annisa",
    ],
}

# Fungsi Membaca Data
def load_data():
    if os.path.exists(FILE_DATA):
        return pd.read_csv(FILE_DATA)
    else:
        return pd.DataFrame(columns=["Tanggal", "Kelas", "Nama Siswa", "Status"])

# Fungsi Menyimpan Data
def save_data(df):
    df.to_csv(FILE_DATA, index=False)

# Inisialisasi Data
df_absensi = load_data()

# Header Utama
st.title("🏫 Aplikasi Absensi Siswa")

# --- SIDEBAR NAVIGASI UNTUK MEMBEDAKAN PERAN ---
st.sidebar.header("📌 Pilih Akses")
peran = st.sidebar.radio("Masuk Sebagai:", ["Wali Kelas (Input Absen)", "Admin (Rekap Data)"])

# =========================================================
# 1. HALAMAN WALI KELAS (HANYA INPUT DATA)
# =========================================================
if peran == "Wali Kelas (Input Absen)":
    st.subheader("📝 Form Input Absensi Harian")
    
    # Pilih Kelas
    kelas_terpilih = st.selectbox("Pilih Kelas Anda:", list(DATA_MASTER_SISWA.keys()))
    
    # Pilih Tanggal (Bisa Mundur untuk Tanggal Terlewat)
    tgl_absensi = st.date_input("Tanggal Absensi:", value=date.today())
    
    st.markdown("---")
    daftar_siswa = DATA_MASTER_SISWA[kelas_terpilih]
    st.write(f"**Daftar Siswa {kelas_terpilih}** ({len(daftar_siswa)} Siswa)")
    
    # Dictionary Temp untuk Menampung Pilihan Status Absen
    status_input = {}
    
    with st.form(key=f"form_absen_{kelas_terpilih}"):
        for siswa in daftar_siswa:
            # Pilihan Radio Button
            status_input[siswa] = st.radio(
                f"👤 {siswa}",
                ["Hadir", "Sakit", "Izin", "Alpa"],
                horizontal=True,
                key=f"{kelas_terpilih}_{siswa}"
            )
        
        btn_simpan = st.form_submit_button("💾 Simpan Absensi")
        
    if btn_simpan:
        data_baru = []
        tgl_str = tgl_absensi.strftime("%Y-%m-%d")
        
        for siswa, status in status_input.items():
            data_baru.append({
                "Tanggal": tgl_str,
                "Kelas": kelas_terpilih,
                "Nama Siswa": siswa,
                "Status": status
            })
        
        df_baru = pd.DataFrame(data_baru)
        
        # Hapus data lama jika tanggal & kelas sama (mencegah ganda)
        if not df_absensi.empty:
            df_absensi = df_absensi[~((df_absensi["Tanggal"] == tgl_str) & (df_absensi["Kelas"] == kelas_terpilih))]
        
        # Gabungkan data baru
        df_absensi = pd.concat([df_absensi, df_baru], ignore_index=False)
        save_data(df_absensi)
        
        st.success(f"✅ Absensi {kelas_terpilih} tanggal {tgl_str} berhasil disimpan!")

# =========================================================
# 2. HALAMAN ADMIN (REKAP DATA & HAPUS DATA)
# =========================================================
else:
    st.subheader("📊 Halaman Khusus Admin (Rekap Data)")
    
    if df_absensi.empty:
        st.info("Belum ada data absensi yang tersimpan.")
    else:
        # Filter Tampilan Rekap
        st.write("### Filter Data Rekap")
        pilihan_kelas = st.selectbox("Filter Kelas:", ["Semua Kelas"] + list(DATA_MASTER_SISWA.keys()))
        
        df_tampil = df_absensi.copy()
        if pilihan_kelas != "Semua Kelas":
            df_tampil = df_tampil[df_tampil["Kelas"] == pilihan_kelas]
            
        st.dataframe(df_tampil, use_container_width=True)
        
        # Tombol Download File CSV / Excel
        csv_data = df_tampil.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data Absensi (CSV/Excel)",
            data=csv_data,
            file_name=f"rekap_absensi_{pilihan_kelas.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        # Fitur Hapus Entri Salah (Khusus Admin)
        st.write("### 🗑️ Hapus Data Absensi")
        with st.expander("Klik di sini untuk menghapus data tanggal/kelas tertentu"):
            st.warning("Perhatian: Data yang dihapus tidak dapat dikembalikan.")
            
            daftar_tgl = df_absensi["Tanggal"].unique()
            tgl_hapus = st.selectbox("Pilih Tanggal yang Ingin Dihapus:", daftar_tgl)
            kelas_hapus = st.selectbox("Pilih Kelas yang Ingin Dihapus:", ["Semua Kelas"] + list(DATA_MASTER_SISWA.keys()))
            
            if st.button("🔴 Hapus Data Terpilih"):
                if kelas_hapus == "Semua Kelas":
                    df_absensi = df_absensi[df_absensi["Tanggal"] != tgl_hapus]
                else:
                    df_absensi = df_absensi[~((df_absensi["Tanggal"] == tgl_hapus) & (df_absensi["Kelas"] == kelas_hapus))]
                
                save_data(df_absensi)
                st.success(f"Data tanggal {tgl_hapus} ({kelas_hapus}) berhasil dihapus!")
                st.rerun()