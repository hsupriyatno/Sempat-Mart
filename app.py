import streamlit as st
import pandas as pd
import os
from PIL import Image
import datetime
import urllib.parse
from geopy.distance import geodesic

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="SEMPAT MART - Alumni SMPN-4 Cirebon",
    page_icon="🛍️",
    layout="wide"
)

# --- DATABASE HIERARKI KECAMATAN & DESA/KELURAHAN ---
# Format: "Nama Kecamatan": {"Nama Desa/Kelurahan": (Latitude, Longitude)}
DATA_WILAYAH = {
    # --- KOTA CIREBON ---
    "Kota Cirebon - Kec. Kejaksan": {
        "Kel. Kejaksan": (-6.7088, 108.5562),
        "Kel. Kesenden": (-6.7012, 108.5583),
        "Kel. Sukapura": (-6.7035, 108.5461),
        "Kel. Kebonbaru": (-6.7130, 108.5590)
    },
    "Kota Cirebon - Kec. Lemahwungkuk": {
        "Kel. Lemahwungkuk": (-6.7235, 108.5671),
        "Kel. Panjunan": (-6.7168, 108.5662),
        "Kel. Pegambiran": (-6.7380, 108.5721),
        "Kel. Kesepuhan": (-6.7265, 108.5620)
    },
    "Kota Cirebon - Kec. Pekalipan": {
        "Kel. Pekalipan": (-6.7221, 108.5589),
        "Kel. Pulasaren": (-6.7238, 108.5550),
        "Kel. Jagasatru": (-6.7285, 108.5571)
    },
    "Kota Cirebon - Kec. Kesambi": {
        "Kel. Kesambi": (-6.7305, 108.5482),
        "Kel. Sunyaragi": (-6.7362, 108.5398),
        "Kel. Karyamulya": (-6.7410, 108.5285),
        "Kel. Drajat": (-6.7328, 108.5521),
        "Kel. Pekiringan": (-6.7188, 108.5501)
    },
    "Kota Cirebon - Kec. Harjamukti": {
        "Kel. Harjamukti": (-6.7580, 108.5412),
        "Kel. Kalijaga": (-6.7485, 108.5610),
        "Kel. Argasunya": (-6.7820, 108.5505),
        "Kel. Larangan": (-6.7395, 108.5580),
        "Kel. Kebonmanis": (-6.7450, 108.5490)
    },

    # --- KABUPATEN CIREBON ---
    "Kab. Cirebon - Kec. Kedawung": {
        "Desa Kedawung": (-6.7095, 108.5350),
        "Desa Kertawinangun (Tuparev)": (-6.7110, 108.5380),
        "Desa Sutawinangun": (-6.7125, 108.5320),
        "Desa Kalitoa": (-6.7080, 108.5280)
    },
    "Kab. Cirebon - Kec. Weru": {
        "Desa Megu Gede": (-6.7180, 108.5080),
        "Desa Megu Cilik": (-6.7150, 108.5020),
        "Desa Tegalwangi": (-6.7120, 108.4980),
        "Desa Weru Lor": (-6.7050, 108.5050),
        "Desa Weru Kidul": (-6.7080, 108.5010)
    },
    "Kab. Cirebon - Kec. Plumbon": {
        "Desa Plumbon": (-6.7100, 108.4680),
        "Desa Gombang": (-6.7150, 108.4550),
        "Desa Marikangen": (-6.7200, 108.4600),
        "Desa Padasuka": (-6.7080, 108.4500)
    },
    "Kab. Cirebon - Kec. Sumber": {
        "Kel. Sumber (Pusat Pemkab)": (-6.7610, 108.4810),
        "Kel. Babakan": (-6.7550, 108.4850),
        "Kel. Watubelah": (-6.7420, 108.4920),
        "Kel. Sendang": (-6.7500, 108.4780)
    },
    "Kab. Cirebon - Kec. Mundu": {
        "Desa Mundu Pesisir": (-6.7520, 108.6010),
        "Desa Bandengan": (-6.7580, 108.6100),
        "Desa Luwung": (-6.7650, 108.5880)
    },
    "Kab. Cirebon - Kec. Astanajapura": {
        "Desa Japura Bakti": (-6.8120, 108.6350),
        "Desa Mertapada": (-6.8050, 108.6280),
        "Desa Kanci": (-6.7890, 108.6200)
    },

    # --- WILAYAH SEKITAR (CIAYUMAJAKUNING) ---
    "Kab. Kuningan": {
        "Kec. Cilimus": (-6.8520, 108.5050),
        "Kec. Jalaksana": (-6.8900, 108.5010),
        "Kec. Kuningan Kota": (-6.9760, 108.4830)
    },
    "Kab. Majalengka": {
        "Kec. Rajagaluh": (-6.8280, 108.3420),
        "Kec. Jatiwangi": (-6.7320, 108.2610),
        "Kec. Majalengka Kota": (-6.8360, 108.2280)
    },
    "Kab. Indramayu": {
        "Kec. Jatibarang": (-6.4710, 108.3090),
        "Kec. Karangampel": (-6.4620, 108.4520),
        "Kec. Indramayu Kota": (-6.3260, 108.3200)
    }
}

LIST_KECAMATAN = list(DATA_WILAYAH.keys())

# --- FUNGSI PARSING DARI STRING DATABASE ---
# Format simpanan di database: "Kecamatan | Desa"
def get_coords_from_str(lokasi_str):
    try:
        if " | " in str(lokasi_str):
            kec, desa = str(lokasi_str).split(" | ", 1)
            if kec in DATA_WILAYAH and desa in DATA_WILAYAH[kec]:
                return DATA_WILAYAH[kec][desa]
        # Default jika format lama / fallback ke Kesambi
        return (-6.7305, 108.5482)
    except Exception:
        return (-6.7305, 108.5482)

# --- FUNGSI HITUNG ONGKIR DARI HIERARKI ---
def hitung_ongkir_cascading(lokasi_asal_str, lokasi_tujuan_str, tarif_per_km=4000, min_ongkir=10000):
    try:
        coord1 = get_coords_from_str(lokasi_asal_str)
        coord2 = get_coords_from_str(lokasi_tujuan_str)
        
        # 1. Jarak Garis Lurus
        jarak_garis_lurus = geodesic(coord1, coord2).km
        
        # 2. Jarak Rute Jalan Raya (Pengali 1.2)
        jarak_rute = jarak_garis_lurus * 1.2
        
        # Jika asal & tujuan sama persis (sama kelurahan/desa)
        if jarak_rute < 0.5:
            jarak_rute = 0.5
            
        # 3. Hitung Total Ongkir
        total_ongkir = max(min_ongkir, jarak_rute * tarif_per_km)
        return round(jarak_rute, 1), int(total_ongkir)
    except Exception:
        return 1.0, min_ongkir

# --- KONFIGURASI PATH & DATABASE ---
if os.path.exists(r"D:\DATA\01. RELIABILITY PROJECT\DATABASE PROJECT\SEMPAT Mart"):
    BASE_DIR = r"D:\DATA\01. RELIABILITY PROJECT\DATABASE PROJECT\SEMPAT Mart"
else:
    BASE_DIR = os.getcwd()

DB_FILE = os.path.join(BASE_DIR, "sempat_mart_products.csv")
IMG_DIR = os.path.join(BASE_DIR, "product_images")
COUNTER_FILE = os.path.join(BASE_DIR, "visitor_counter.txt")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- FUNGSI PENGHITUNG KUNJUNGAN ---
def get_and_update_views():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("0")
    
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
        try:
            with open(COUNTER_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0

total_kunjungan = get_and_update_views()

# --- FUNGSI PEMBACAAN DATA ---
def load_data():
    default_loc = f"{LIST_KECAMATAN[0]} | {list(DATA_WILAYAH[LIST_KECAMATAN[0]].keys())[0]}"
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype=str)
            df = df.fillna("")
            
            kolom_wajib = ["Nama Penjual", "Angkatan", "Nama Produk", "Kategori", "Harga", "Lokasi Toko", "No WA (Format: 62xx)", "Deskripsi", "Daftar File Gambar"]
            for col in kolom_wajib:
                if col not in df.columns:
                    df[col] = default_loc if col == "Lokasi Toko" else ""
            return df
        except Exception as e:
            st.error(f"Gagal membaca file data utama: {e}")
            
    data = {
        "Nama Penjual": [], "Angkatan": [], "Nama Produk": [], "Kategori": [],
        "Harga": [], "Lokasi Toko": [], "No WA (Format: 62xx)": [], "Deskripsi": [], "Daftar File Gambar": []
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

st.sidebar.markdown("---")
st.sidebar.metric(label="👥 Total Pengunjung Situs", value=f"{total_kunjungan} Kali")

# UTILITY BACKUP & RESTORE
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Fitur Cadangan Database")

if not df_products.empty:
    csv_bytes = df_products.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Data CSV Terbaru",
        data=csv_bytes,
        file_name="sempat_mart_products_backup.csv",
        mime="text/csv",
        help="Simpan backup data lokal ini di komputer/HP Anda."
    )

uploaded_backup = st.sidebar.file_uploader(
    "Upload file backup untuk memulihkan data:", 
    type=["csv"], 
    key="backup_uploader"
)

if uploaded_backup is not None:
    if st.sidebar.button("🔄 Jalankan Restore Data", type="primary"):
        try:
            df_restored = pd.read_csv(uploaded_backup, dtype=str).fillna("")
            save_data(df_restored)
            st.sidebar.success("✅ Data merchant berhasil dipulihkan!")
            st.rerun()
        except Exception as ex:
            st.sidebar.error(f"Gagal memulihkan data: {ex}")


# --- HALAMAN 1: KATALOG ---
if menu == "🛍️ Katalog Produk":
    st.title("🛍️ Katalog Pasar Digital SEMPAT MART")
    st.subheader("Dukung usaha sesama alumni SMPN-4 Cirebon!")
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

                    lokasi_penjual_str = str(row.get('Lokasi Toko', ''))

                    st.markdown(f"### **{row['Nama Produk']}**")
                    st.markdown(f"**💰 Harga:** {harga_display}")
                    st.markdown(f"**👤 Penjual:** {row['Nama Penjual']} (Angkatan {row['Angkatan']})")
                    st.markdown(f"**📍 Lokasi Toko:** {lokasi_penjual_str}")
                    st.write(f"📝 {row['Deskripsi']}")
                    
                    # --- KALKULATOR ONGKIR CASCADING ---
                    with st.expander("🚚 Cek Estimasi Ongkir (Pilih Wilayah Anda)"):
                        col_kec, col_desa = st.columns(2)
                        with col_kec:
                            kec_pembeli = st.selectbox(
                                "Kecamatan/Kabupaten:", 
                                options=LIST_KECAMATAN,
                                key=f"kec_buyer_{index}"
                            )
                        with col_desa:
                            list_desa = list(DATA_WILAYAH[kec_pembeli].keys())
                            desa_pembeli = st.selectbox(
                                "Desa/Kelurahan:", 
                                options=list_desa,
                                key=f"desa_buyer_{index}"
                            )
                        
                        lokasi_pembeli_str = f"{kec_pembeli} | {desa_pembeli}"
                        
                        # Hitung Ongkir
                        jarak_km, total_ongkir = hitung_ongkir_cascading(
                            lokasi_penjual_str, 
                            lokasi_pembeli_str,
                            tarif_per_km=4000,  # <-- Silakan ubah tarif per km jika perlu
                            min_ongkir=10000     # <-- Silakan ubah tarif min ongkir jika perlu
                        )
                        
                        st.success(f"📏 Est. Jarak Rute (x1.2): **{jarak_km} km**")
                        st.info(f"💵 Est. Ongkir: **Rp {total_ongkir:,}**")

                    # --- HUBUNGI WA DI HP ---
                    no_wa_aktif = str(row['No WA (Format: 62xx)']).strip()
                    wa_message = f"Halo, saya tertarik dengan produk '{row['Nama Produk']}' di SEMPAT MART."
                    encoded_message = urllib.parse.quote(wa_message)
                    
                    wa_link = f"https://api.whatsapp.com/send?phone={no_wa_aktif}&text={encoded_message}"
                    
                    tombol_wa_html = f"""
                        <a href="{wa_link}" target="_blank" style="
                            display: inline-block;
                            width: 100%;
                            padding: 10px 0px;
                            background-color: #25D366;
                            color: white;
                            text-align: center;
                            text-decoration: none;
                            font-size: 15px;
                            font-weight: bold;
                            border-radius: 8px;
                            margin-top: 10px;
                            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
                        ">
                            💬 Hubungi Penjual via WA
                        </a>
                    """
                    st.markdown(tombol_wa_html, unsafe_allow_html=True)

# --- HALAMAN 2: FORM VENDOR ---
elif menu == "➕ Daftarkan Jualan Anda":
    st.title("➕ Daftarkan Jualan Anda")
    st.write("Silakan isi formulir dan unggah foto produk Anda (Maksimal 5 Foto).")
    
    with st.form("form_tambah_produk", clear_on_submit=False):
        nama_penjual = st.text_input("Nama Lengkap:")
        angkatan = st.selectbox("Angkatan SMPN-4 Cirebon:", ["86", "Lainnya"])
        nama_produk = st.text_input("Nama Produk/Jasa:")
        
        # CASCADING DROPDOWN UNTUK LOKASI TOKO
        st.markdown("**📍 Lokasi Toko / Penjual:**")
        col_kec_v, col_desa_v = st.columns(2)
        with col_kec_v:
            kec_vendor = st.selectbox("Pilih Kecamatan/Kabupaten:", options=LIST_KECAMATAN, key="vendor_kec_add")
        with col_desa_v:
            desa_vendor = st.selectbox("Pilih Desa/Kelurahan:", options=list(DATA_WILAYAH[kec_vendor].keys()), key="vendor_desa_add")
            
        lokasi_toko_final = f"{kec_vendor} | {desa_vendor}"
        
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
            if nama_penjual and nama_produk and no_wa and uploaded_images and lokasi_toko_final:
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
                        "Lokasi Toko": lokasi_toko_final,
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
                st.error("Mohon lengkapi data penting: Nama, Nama Produk, Lokasi Toko, WhatsApp, dan minimal 1 Foto Produk.")

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
                
                # --- AMBIL DATA LOKASI LAMA ---
                lokasi_lama_str = str(row_data.get("Lokasi Toko", ""))
                def_kec_idx = 0
                def_desa_idx = 0
                if " | " in lokasi_lama_str:
                    old_k, old_d = lokasi_lama_str.split(" | ", 1)
                    if old_k in LIST_KECAMATAN:
                        def_kec_idx = LIST_KECAMATAN.index(old_k)
                        old_desas = list(DATA_WILAYAH[old_k].keys())
                        if old_d in old_desas:
                            def_desa_idx = old_desas.index(old_d)

                # --- DROPDOWN LOKASI DITARUH DI LUAR FORM AGAR INTERAKTIF/CASCADING RE-RENDER ---
                st.markdown("**📍 Lokasi Toko / Penjual:**")
                col_kec_e, col_desa_e = st.columns(2)
                
                with col_kec_e:
                    edit_kec_vendor = st.selectbox(
                        "Pilih Kecamatan/Kabupaten:", 
                        options=LIST_KECAMATAN, 
                        index=def_kec_idx, 
                        key=f"vendor_kec_edit_{target_idx}"
                    )
                
                # List desa dinamis menyesuaikan kecamatan yang sedang dipilih
                edit_desa_list = list(DATA_WILAYAH[edit_kec_vendor].keys())
                
                # Tentukan default index desa
                if edit_kec_vendor == LIST_KECAMATAN[def_kec_idx]:
                    current_desa_idx = def_desa_idx if def_desa_idx < len(edit_desa_list) else 0
                else:
                    current_desa_idx = 0

                with col_desa_e:
                    edit_desa_vendor = st.selectbox(
                        "Pilih Desa/Kelurahan:", 
                        options=edit_desa_list, 
                        index=current_desa_idx, 
                        key=f"vendor_desa_edit_{target_idx}_{edit_kec_vendor}"
                    )
                
                edit_lokasi_toko_final = f"{edit_kec_vendor} | {edit_desa_vendor}"

                # --- FORM UNTUK FIELD LAINNYA ---
                with st.form(f"form_edit_produk_{target_idx}"):
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
                    
                    submit_edit = st.form_submit_button("Simpan Perubahan")
                    
                    if submit_edit:
                        df_products.at[target_idx, "Nama Penjual"] = edit_nama_penjual
                        df_products.at[target_idx, "Angkatan"] = edit_angkatan
                        df_products.at[target_idx, "Nama Produk"] = edit_nama_produk
                        df_products.at[target_idx, "Lokasi Toko"] = edit_lokasi_toko_final
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