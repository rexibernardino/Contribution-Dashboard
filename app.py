import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils import calculate_ranking, parse_broker_csv, get_dummy_data, load_data_from_gdrive

# Konfigurasi Halaman
st.set_page_config(page_title="Broker Contribution Dashboard", page_icon="📋", layout="wide")

# Inisialisasi Session State
if 'main_df' not in st.session_state:
    if 'sheet_title' not in st.session_state:
        st.session_state.sheet_title = "Broker Contribution Dashboard" # Default

    try:
        if "spreadsheet_url" in st.secrets:
            df, title = load_data_from_gdrive(st.secrets["spreadsheet_url"])
            st.session_state.main_df = df
            st.session_state.sheet_title = title
        else:
            st.session_state.main_df = get_dummy_data()
    except:
        st.session_state.main_df = get_dummy_data()

# --- SIDEBAR NAVIGASI ---
st.sidebar.title(st.session_state.sheet_title)
# Google Drive Sync
st.sidebar.markdown("### ☁️ Google Drive Sync")
default_url = st.secrets.get("spreadsheet_url", "")
gdrive_url = st.sidebar.text_input("Google Sheet URL", value=default_url)

if st.sidebar.button("🔄 Sync & Refresh Data"):
    with st.spinner("Sedang menarik data dari Drive..."):
        try:
            updated_df, updated_title = load_data_from_gdrive(gdrive_url)
            st.session_state.main_df = updated_df
            st.session_state.sheet_title = updated_title
            st.sidebar.success("Berhasil Update!")
            st.rerun() # Refresh dashboard untuk menampilkan data baru
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

st.sidebar.divider()
st.sidebar.markdown("### 📊 Broker Ranking Dashboard Menu")
menu = st.sidebar.radio("Menu", [
    "Dashboard & Ranking Each Category",
    "Dashboard & Ranking All Categories", 
    "Import CSV: Monthly (Bulan Lalu)", 
    "Import CSV: Daily (Harian)",
    "Input Data Manual"
])

if menu == "Dashboard & Ranking All Categories":
    st.sidebar.divider()
    st.sidebar.markdown("### ✏️ Kustomisasi Judul")
    custom_title = st.sidebar.text_input("Edit Judul Halaman", value=st.session_state.sheet_title)
else:
    custom_title = "Broker Contribution Dashboard"
    
categories = ["Forex Swap", "Fixed Income", "Money Market"]

if menu == "Dashboard & Ranking Each Category":
    st.sidebar.divider()
    st.sidebar.markdown("### 🔍 Filter Kategori")
    selected_cat = st.sidebar.selectbox("Pilih Kategori Utama", categories)

def get_unit(cat):
    return "Mio USD" if cat == "Forex Swap" else "IDR Bn"

# --- MENU 1: DASHBOARD & RANKING ---
if menu == "Dashboard & Ranking Each Category":
    st.title(f"📈 {selected_cat} Ranking")
    
    today = datetime.now()
    first_day_curr = today.replace(day=1)
    last_month_date = first_day_curr - timedelta(days=1)
    
    df_master = st.session_state.main_df
    # df_last = df_master[df_master['Date'].dt.month == last_month_date.month]
    df_last = df_master[pd.to_datetime(df_master['Date']).dt.month == last_month_date.month]
    
    if not df_master.empty:
        latest_date = pd.to_datetime(df_master['Date']).max()
        df_now = df_master[pd.to_datetime(df_master['Date']) == latest_date]
        daily_label = f"Current Ranking (Data: {latest_date.date()})"
    else:
        df_now = pd.DataFrame()
        daily_label = "Current Ranking"
    
    unit_label = f"Volume ({get_unit(selected_cat)})"

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📅 Monthly ({last_month_date.strftime('%B %Y')})")
        rank_last = calculate_ranking(df_last, selected_cat)
        
        # 2. Rename kolom Volume sebelum ditampilkan di tabel Monthly
        display_rank_last = rank_last.rename(columns={'Volume': unit_label})
        st.dataframe(display_rank_last, use_container_width=True, hide_index=True)

    with col2:
        st.subheader(f"🚀 {daily_label}")
        rank_now = calculate_ranking(df_now, selected_cat)
        
        # 3. Rename kolom Volume sebelum ditampilkan di tabel Current
        display_rank_now = rank_now.rename(columns={'Volume': unit_label})
        st.dataframe(display_rank_now, use_container_width=True, hide_index=True)

    st.divider()
    v_col1, v_col2= st.columns(2)
    
    with v_col1:
        st.subheader(f"Monthly Volume ({last_month_date.strftime('%B')})")
        
        # Membuat Bar Chart menggunakan rank_last (Data Bulan Lalu)
        fig_monthly_bar = px.bar(rank_last, 
                                x='Broker_Name', 
                                y='Volume', 
                                color='Volume',
                                text='Volume', # Menampilkan angka volume di bar
                                color_continuous_scale='Greens', 
                                labels={'Volume': f'Volume ({get_unit(selected_cat)})'})
        
        # Mengatur posisi label angka dan format desimal
        fig_monthly_bar.update_traces(
            textposition='outside', 
            texttemplate='%{text:.2f}'
        )
        
        # Mengatur layout agar nama broker tidak saling tumpang tindih jika datanya banyak
        fig_monthly_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_monthly_bar, use_container_width=True)
    
    with v_col2:
        st.subheader(f"Current Top Broker ({get_unit(selected_cat)})")
        fig_bar = px.bar(rank_now.head(10), 
                        x='Broker_Name', 
                        y='Volume', 
                        color='Volume',
                        text='Volume', # Menampilkan angka volume
                        color_continuous_scale='Blues', # Warna berbeda agar tidak tertukar dengan Monthly
                        labels={'Volume': f'Volume ({get_unit(selected_cat)})'})

        
        # Mengatur posisi angka agar berada di luar/atas bar dan format angka
        fig_bar.update_traces(textposition='outside', texttemplate='%{text:.2f}')
        st.plotly_chart(fig_bar, use_container_width=True)

    # # Pie Chart untuk Monthly (Bulan Lalu)
    # with v_col1:
    #     st.subheader(f"Monthly Volume ({last_month_date.strftime('%B')})")
        
    #     # Membuat Pie Chart
    #     fig_pie = px.pie(rank_last, 
    #                     values='Volume', 
    #                     names='Broker Name', 
    #                     hole=0.4,
    #                     # Menambahkan data volume agar bisa dipanggil di template
    #                     custom_data=['Volume']) 
        
    #     # Mengatur agar menampilkan Label, Persentase, dan Nilai Volume di dalam chart
    #     fig_pie.update_traces(
    #         textposition='inside', 
    #         textinfo='percent+label+value',
    #         # %{value:.2f} menampilkan angka volume dengan 2 desimal
    #         # %{percent} menampilkan persentase otomatis dari Plotly
    #         texttemplate='%{label}<br>%{value:.2f}<br>(%{percent})'
    #     )
        
        # st.plotly_chart(fig_pie, use_container_width=True)

# --- MENU 2 & 3: IMPORT ---
elif menu in ["Import CSV: Monthly (Bulan Lalu)", "Import CSV: Daily (Harian)"]:
    is_monthly = "Monthly" in menu
    st.title(f"📥 {menu}")
    default_date = datetime.now()
    if is_monthly:
        default_date = (default_date.replace(day=1) - timedelta(days=1))

    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    date_input = st.date_input("Tanggal Data", default_date)
    
    if uploaded_file:
        try:
            temp_df = parse_broker_csv(uploaded_file, date_input)
            st.dataframe(temp_df.head())
            mode = st.radio("Mode", ["Merge", "Replace"])
            if st.button("Simpan"):
                if mode == "Merge":
                    st.session_state.main_df = pd.concat([st.session_state.main_df, temp_df], ignore_index=True)
                else:
                    st.session_state.main_df = temp_df
                st.success("Berhasil!")
        except Exception as e:
            st.error(f"Error: {e}")

# --- MENU 4: INPUT MANUAL ---
elif menu == "Input Data Manual":
    st.title("📝 Management")
    t1, t2 = st.tabs(["Tambah", "Edit/Hapus"])
    with t1:
        with st.form("f1"):
            c1, c2 = st.columns(2)
            d = c1.date_input("Tanggal")
            b = c2.text_input("Broker")
            cat = c1.selectbox("Kategori", categories)
            v = c2.number_input("Volume", min_value=0.0)
            if st.form_submit_button("Simpan"):
                new_row = pd.DataFrame({'Date': [d], 'Broker Name': [b], 'Category': [cat], 'Volume': [v]})
                st.session_state.main_df = pd.concat([st.session_state.main_df, new_row], ignore_index=True)
                st.success("Ok!")
    with t2:
        edited = st.data_editor(st.session_state.main_df, num_rows="dynamic", use_container_width=True)
        if st.button("Update"):
            st.session_state.main_df = edited
            st.success("Updated!")

# --- MENU 5: DASHBOARD & RANKING ALL CATEGORIES ---
elif menu == "Dashboard & Ranking All Categories":
    st.title(custom_title)
    
    # --- FITUR SORTING DI TAMPILAN UTAMA ---
    s_col1, s_col2 = st.columns([1, 2]) 
    with s_col1:
        sort_choice = st.radio(
            "Urutkan Volume berdasarkan:", 
            ["Terbesar (Descending)", "Terkecil (Ascending)"],
            horizontal=True # Membuat pilihan berjejer ke samping
        )

    # Pengaturan Waktu
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    current_date_str = today.strftime('%d %B %Y')
    
    first_day_curr = today.replace(day=1)
    last_month_date = first_day_curr - timedelta(days=1)

    df_master = st.session_state.main_df
    df_master['Date'] = pd.to_datetime(df_master['Date'])

    # Filter Data Bulanan dan Terkini
    df_last_all = df_master[pd.to_datetime(df_master['Date']).dt.month == last_month_date.month]
    latest_date = pd.to_datetime(df_master['Date']).max() if not df_master.empty else today
    df_now_all = df_master[
        (df_master['Date'].dt.month == current_month) & 
        (df_master['Date'].dt.year == current_year)
    ]
    
    # Grid Layout: 3 Kolom (Satu kolom per Divisi)
    col_fi, col_mm, col_fx = st.columns(3)
    
    divisi_config = [
        {"name": "Fixed Income", "col": col_fi, "color_m": "Greens", "color_d": "Blues"},
        {"name": "Money Market", "col": col_mm, "color_m": "Greens", "color_d": "Blues"},
        {"name": "Forex Swap", "col": col_fx, "color_m": "Greens", "color_d": "Blues"}
    ]

    for div in divisi_config:
            with div["col"]:
                unit = get_unit(div["name"])
                st.markdown(f"#### {div['name']} ({unit})")
                
                # --- LOGIKA SORTING ---
                is_asc = True if sort_choice == "Terkecil (Ascending)" else False
                
                # 1. Monthly Chart
                rank_m = calculate_ranking(df_last_all, div["name"])
                # Terapkan sorting ke dataframe
                rank_m = rank_m.sort_values(by='Volume', ascending=is_asc)
                
                fig_m = px.bar(rank_m, x='Volume', y='Broker_Name', text='Volume', 
                            color_discrete_sequence=[px.colors.qualitative.Plotly[2]],
                            title=f"Monthly ({last_month_date.strftime('%B')})")
                
                fig_m.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                
                # MENGAKTIFKAN LABEL VOLUME DAN BROKER NAME
                fig_m.update_layout(
                    height=300, # Sedikit ditambah agar label axis tidak terpotong
                    margin=dict(l=10, r=10, t=30, b=40), 
                    showlegend=False, 
                    xaxis_title="Volume",      # Menampilkan tulisan "Volume" di bawah angka
                    yaxis_title="Broker Name"  # Menampilkan tulisan "Broker Name" di samping
                )
                st.plotly_chart(fig_m, use_container_width=True, config={'displayModeBar': True},key=f"chart_monthly_{div['name'].replace(' ', '_')}")
        
                # 2. Daily Chart
                rank_d = calculate_ranking(df_now_all, div["name"])
                # Terapkan sorting ke dataframe
                rank_d = rank_d.sort_values(by='Volume', ascending=is_asc)
                
                # Jika data bulan berjalan ditemukan di sheet, tampilkan tanggal hari ini
                if not rank_d.empty:
                    chart_title = f"On going ({current_date_str})"
                else:
                    chart_title = f"On going (No Data for {today.strftime('%B %Y')})"

                fig_d = px.bar(rank_d, x='Volume', y='Broker_Name', text='Volume',
                            color_discrete_sequence= [px.colors.qualitative.Plotly[0]],
                            title=chart_title)
                
                fig_d.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                
                # MENGAKTIFKAN LABEL VOLUME DAN BROKER NAME
                fig_d.update_layout(
                    height=300, 
                    margin=dict(l=10, r=10, t=30, b=40), 
                    showlegend=False, 
                    xaxis_title="Volume",      # Menampilkan tulisan "Volume" di bawah angka
                    yaxis_title="Broker Name"  # Menampilkan tulisan "Broker Name" di samping
                )
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': True}, key=f"chart_ongoing_{div['name'].replace(' ', '_')}")
                
# # Footer
# st.sidebar.divider()
# csv = st.session_state.main_df.to_csv(index=False).encode('utf-8')
# st.sidebar.markdown("### 📂 Export Data")
# st.sidebar.download_button("📥 Export CSV", csv, "data.csv", "text/csv")
