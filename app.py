import streamlit as st
import pandas as pd
import os
from PIL import Image
import datetime
import urllib.parse

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="SEMPAT MART - Alumni SMPN-4 Cirebon",
    page_icon="🛍️",
    layout="wide"
)

# --- KONFIGURASI PATH & DATABASE ---
BASE_DIR = r"D:\DATA\01. RELIABILITY PROJECT\DATABASE PROJECT\SEMPAT Mart"
DB_FILE = os.path.join(BASE_DIR, "sempat_mart_products.csv")
IMG_DIR = os.path.join(BASE_DIR, "product_images")
COUNTER_FILE = os.path.join(BASE_DIR, "visitor_counter.txt")  # File penyimpan hitungan kunjungan

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- FUNGSI PENGHITUNG KUNJUNGAN (FITUR BARU) ---
def get_and_update_views():
    # Jika file belum ada, buat baru dengan angka 0
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("0")
    
    # Jalankan penambahan angka hanya sekali per sesi halaman dimuat
    if "visited" not in st.session_state:
        st.session_state["visited"] = True
        try:
            with open(COUNTER_FILE, "r") as f:
                current_views = int(f.read().strip())
        except Exception:
            current_views = 0
            
        new_views = current_views + 1
        
        try:
            with open(COUNTER_FILE, "w") as f:
                f.write(str(new_views))
        except Exception:
            pass
        return new_views
    else:
        # Jika hanya ganti-ganti menu halaman, baca angka saat ini saja (tidak menambah hitungan)
        try:
            with open(COUNTER_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0

# Panggil fungsi hitung saat aplikasi pertama kali dimuat di browser pengguna
total_kunjungan = get_and_update_views()

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE, dtype={"Harga": str, "No WA (Format: 62xx)": str}).fillna("")
        except Exception:
            pass
            
    data = {
        "Nama Penjual": [],
        "Angkatan": [],
        "Nama Produk": [],
        "Kategori": [],
        "Harga": [],
        "No WA (Format: 62xx)": [],
        "Deskripsi": [],
        "Daftar File Gambar": []
    }
    df = pd.DataFrame(data)
    df.to_csv(DB_FILE, index=False)
    return df

def save_data(df):
    df.to_csv(DB_FILE, index=False)

df_products = load_data()

# --- SIDEBAR ---
st.sidebar.title("SEMPAT MART 🛒")
st.sidebar.write("Dari Kita, Oleh Kita, Untuk Alumni SMPN-4 Cirebon")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigasi Halaman:", 
    ["🛍️ Katalog Produk", "➕ Daftarkan Jualan Anda", "⚙️ Kelola Jualan Anda"]
)

# TAMPILKAN TOTAL KUNJUNGAN DI BAWAH SIDEBAR (FITUR BARU)
st.sidebar.markdown("---")
st.sidebar.metric(label="👥 Total Pengunjung Situs", value=f"{total_kunjungan} Kali")

# --- HALAMAN 1: KATALOG ---
if menu == "🛍️ Katalog Produk":
    st.title("🛍️ Katalog Pasar Digital SEMPAT MART")
    st.subheader("Dukung usaha sesama alumni SMPN-4 Cirebon")
    st.markdown("---")
    
    search_query = st.text_input("🔍 Cari produk atau nama penjual...")
    
    filtered_df = df_products.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Nama Produk"].str.contains(search_query, case=False, na=False) |
            filtered_df["Nama Penjual"].str.contains(search_query, case=False, na=False)
        ]
        
    if filtered_df.empty:
        st.info("Belum ada produk yang didaftarkan.")
    else:
        cols = st.columns(3)
        for index, row in filtered_df.reset_index().iterrows():
            col = cols[index % 3]
            with col:
                with st.container(border=True):
                    images_str = str(row['Daftar File Gambar'])
                    image_list = [img.strip() for img in images_str.split(",") if img.strip()]
                    
                    valid_images = []
                    for img_name in image_list:
                        full_path = os.path.join(IMG_DIR, img_name)
                        if os.path.exists(full_path):
                            valid_images.append(full_path)
                    
                    if valid_images:
                        if len(valid_images) == 1:
                            st.image(Image.open(valid_images[0]), use_container_width=True)
                        else:
                            tabs_labels = [f"📸 Gambar {i+1}" for i in range(len(valid_images))]
                            img_tabs = st.tabs(tabs_labels)
                            for t_idx, img_tab in enumerate(img_tabs):
                                with img_tab:
                                    st.image(Image.open(valid_images[t_idx]), use_container_width=True)
                    else:
                        st.warning("⚠️ Foto tidak tersedia")
                        
                    harga_raw = str(row['Harga'])
                    if harga_raw.isdigit():
                        harga_display = f"Rp {int(harga_raw):,}"
                    else:
                        harga_display = harga_raw

                    st.markdown(f"### **{row['Nama Produk']}**")
                    st.markdown(f"**💰 Harga:** {harga_display}")
                    st.markdown(f"**👤 Penjual:** {row['Nama Penjual']} (Angkatan {row['Angkatan']})")
                    st.write(f"📝 {row['Deskripsi']}")
                    
                    no_wa_aktif = str(row['No WA (Format: 62xx)']).strip()
                    wa_message = f"Halo, saya tertarik dengan produk '{row['Nama Produk']}' di SEMPAT MART."
                    encoded_message = urllib.parse.quote(wa_message)
                    
                    wa_link = f"https://wa.me/{no_wa_aktif}?text={encoded_message}"
                    st.markdown(f"[💬 Hubungi Penjual via WA]({wa_link})")

# --- HALAMAN 2: FORM VENDOR ---
elif menu == "➕ Daftarkan Jualan Anda":
    st.title("➕ Daftarkan Jualan Anda")
    st.write("Silakan isi formulir dan unggah foto produk Anda (Maksimal 5 Foto).")
    
    with st.form("form_tambah_produk", clear_on_submit=False):
        nama_penjual = st.text_input("Nama Lengkap:")
        angkatan = st.selectbox("Angkatan Sempat:", ["86", "Lainnya"])
        nama_produk = st.text_input("Nama Produk/Jasa:")
        
        uploaded_images = st.file_uploader(
            "Unggah Foto Produk (Maksimal 5 foto)", 
            type=['jpg', 'jpeg', 'png'], 
            accept_multiple_files=True
        )
        
        kategori = st.selectbox("Kategori:", ["Kuliner", "Fashion & Atribut", "Jasa / Keahlian", "Umum"])
        
        st.markdown("**Pengaturan Harga:**")
        tipe_harga = st.radio(
            "Pilih tipe harga:",
            ["Harga Pasti (Nominal)", "Harga Bervariasi (Sesuai Katalog / Kontak Penjual)"],
            label_visibility="collapsed"
        )
        
        if tipe_harga == "Harga Pasti (Nominal)":
            harga_input = st.number_input("Masukkan Harga (Rp):", min_value=0, step=1000, value=0)
            harga_final = str(harga_input)
        else:
            harga_opsi_teks = st.selectbox("Keterangan Harga:", ["Sesuai Katalog", "Harga Bervariasi", "Mulai dari... (Tulis di deskripsi)"])
            harga_final = harga_opsi_teks

        no_wa = st.text_input("Nomor WhatsApp:", placeholder="628xxx")
        deskripsi = st.text_area("Deskripsi Singkat:")
        
        submitted = st.form_submit_button("Simpan & Tayangkan Produk")
        
        if submitted:
            if nama_penjual and nama_produk and no_wa and uploaded_images:
                files_to_process = uploaded_images[:5]
                saved_filenames_list = []
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_prod_name = "".join(x for x in nama_produk if x.isalnum())
                
                success_upload = True
                for idx, single_image in enumerate(files_to_process):
                    file_extension = os.path.splitext(single_image.name)[1]
                    saved_filename = f"{timestamp}_{clean_prod_name}_img{idx+1}{file_extension}"
                    full_image_path = os.path.join(IMG_DIR, saved_filename)
                    
                    try:
                        with open(full_image_path, "wb") as f:
                            f.write(single_image.getbuffer())
                        saved_filenames_list.append(saved_filename)
                    except Exception as e:
                        st.error(f"Gagal mengunggah gambar ke-{idx+1}: {e}")
                        success_upload = False
                        break
                
                if success_upload and saved_filenames_list:
                    csv_images_value = ",".join(saved_filenames_list)
                    clean_wa = "".join(filter(str.isdigit, no_wa))
                    
                    new_row = {
                        "Nama Penjual": nama_penjual,
                        "Angkatan": angkatan,
                        "Nama Produk": nama_produk,
                        "Kategori": kategori,
                        "Harga": harga_final,
                        "No WA (Format: 62xx)": clean_wa,
                        "Deskripsi": deskripsi,
                        "Daftar File Gambar": csv_images_value
                    }
                    
                    df_products = pd.concat([df_products, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df_products)
                    
                    st.success(f"🎉 Produk '{nama_produk}' berhasil ditayangkan!")
                    st.balloons()
                    st.rerun()
            else:
                st.error("Mohon lengkapi data penting: Nama, Nama Produk, WhatsApp, dan minimal 1 Foto Produk.")

# --- HALAMAN 3: EDIT & DELETE ---
elif menu == "⚙️ Kelola Jualan Anda":
    st.title("⚙️ Kelola Jualan Anda")
    st.write("Masukkan Nomor WhatsApp Anda untuk melihat dan mengedit/menghapus produk yang pernah didaftarkan.")
    
    verifikasi_wa = st.text_input("Masukkan Nomor WhatsApp Anda saat mendaftar:", placeholder="Contoh: 62812345...")
    
    if verifikasi_wa:
        clean_verif_wa = "".join(filter(str.isdigit, verifikasi_wa))
        user_products = df_products[df_products["No WA (Format: 62xx)"].astype(str) == clean_verif_wa]
        
        if user_products.empty:
            st.warning("Tidak ada produk yang terdaftar dengan nomor WhatsApp tersebut. Pastikan nomor sesuai (menggunakan format 62xxx).")
        else:
            st.success(f"Ditemukan {len(user_products)} produk Anda.")
            
            produk_pilihan = st.selectbox(
                "Pilih Produk yang Ingin Dikelola:", 
                user_products["Nama Produk"].tolist()
            )
            
            target_idx = df_products[
                (df_products["No WA (Format: 62xx)"].astype(str) == clean_verif_wa) & 
                (df_products["Nama Produk"] == produk_pilihan)
            ].index[0]
            
            row_data = df_products.loc[target_idx]
            
            st.markdown("---")
            action = st.radio("Pilih Tindakan:", ["📝 Edit Data Produk", "❌ Hapus Produk dari Toko"])
            
            if action == "📝 Edit Data Produk":
                st.subheader(f"Form Edit: {row_data['Nama Produk']}")
                
                with st.form("form_edit_produk"):
                    edit_nama_penjual = st.text_input("Nama Lengkap:", value=row_data["Nama Penjual"])
                    edit_angkatan = st.selectbox("Angkatan Sempat:", ["86", "Lainnya"], index=0 if row_data["Angkatan"] == "86" else 1)
                    edit_nama_produk = st.text_input("Nama Produk/Jasa:", value=row_data["Nama Produk"])
                    edit_kategori = st.selectbox(
                        "Kategori:", 
                        ["Kuliner", "Fashion & Atribut", "Jasa / Keahlian", "Umum"],
                        index=["Kuliner", "Fashion & Atribut", "Jasa / Keahlian", "Umum"].index(row_data["Kategori"]) if row_data["Kategori"] in ["Kuliner", "Fashion & Atribut", "Jasa / Keahlian", "Umum"] else 0
                    )
                    
                    harga_lama = str(row_data["Harga"])
                    is_harga_digit = harga_lama.isdigit()
                    
                    st.markdown("**Pengaturan Harga Baru:**")
                    edit_tipe_harga = st.radio(
                        "Pilih tipe harga:",
                        ["Harga Pasti (Nominal)", "Harga Bervariasi (Sesuai Katalog / Kontak Penjual)"],
                        index=0 if is_harga_digit else 1
                    )
                    
                    if edit_tipe_harga == "Harga Pasti (Nominal)":
                        harga_default_val = int(harga_lama) if is_harga_digit else 0
                        edit_harga_input = st.number_input("Masukkan Harga (Rp):", min_value=0, step=1000, value=harga_default_val)
                        edit_harga_final = str(edit_harga_input)
                    else:
                        opsi_list = ["Sesuai Katalog", "Harga Bervariasi", "Mulai dari... (Tulis di deskripsi)"]
                        default_opsi_idx = opsi_list.index(harga_lama) if harga_lama in opsi_list else 0
                        edit_harga_opsi = st.selectbox("Keterangan Harga:", opsi_list, index=default_opsi_idx)
                        edit_harga_final = edit_harga_opsi
                        
                    edit_deskripsi = st.text_area("Deskripsi Singkat:", value=row_data["Deskripsi"])
                    st.info("💡 Catatan: Untuk versi saat ini, jika ingin mengganti foto silakan hapus produk lalu daftarkan kembali dengan foto baru.")
                    
                    submit_edit = st.form_submit_button("Simpan Perubahan")
                    
                    if submit_edit:
                        df_products.at[target_idx, "Nama Penjual"] = edit_nama_penjual
                        df_products.at[target_idx, "Angkatan"] = edit_angkatan
                        df_products.at[target_idx, "Nama Produk"] = edit_nama_produk
                        df_products.at[target_idx, "Kategori"] = edit_kategori
                        df_products.at[target_idx, "Harga"] = edit_harga_final
                        df_products.at[target_idx, "Deskripsi"] = edit_deskripsi
                        
                        save_data(df_products)
                        st.success("🎉 Perubahan data produk berhasil disimpan!")
                        st.rerun()

            elif action == "❌ Hapus Produk dari Toko":
                st.subheader(f"Hapus Produk: {row_data['Nama Produk']}")
                st.warning("⚠️ Apakah Anda yakin ingin menghapus produk ini secara permanen dari SEMPAT MART?")
                
                konfirmasi_hapus = st.checkbox("Ya, saya setuju menghapus produk ini secara permanen.")
                tombol_hapus = st.button("Hapus Produk Sekarang", type="primary", disabled=not konfirmasi_hapus)
                
                if tombol_hapus:
                    images_str = str(row_data['Daftar File Gambar'])
                    image_list = [img.strip() for img in images_str.split(",") if img.strip()]
                    for img_name in image_list:
                        full_path = os.path.join(IMG_DIR, img_name)
                        if os.path.exists(full_path):
                            try:
                                os.remove(full_path)
                            except Exception:
                                pass
                                
                    df_products = df_products.drop(target_idx)
                    save_data(df_products)
                    st.success("❌ Produk telah berhasil dihapus dari sistem.")
                    st.rerun()
