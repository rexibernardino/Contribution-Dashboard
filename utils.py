import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

def clean_volume(val):
    if pd.isna(val) or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    # Menangani format 1.280,00 -> 1280.00
    res = str(val).replace('.', '').replace(',', '.')
    try:
        return float(res)
    except:
        return 0.0

def parse_broker_csv(file, date_selected):
    # Baca mentah dengan separator semicolon sesuai file contoh
    df_raw = pd.read_csv(file, sep=';', header=None)
    
    all_data = []
    # Mapping kolom: [StartRow, [Col_Name, Col_Vol], CategoryName]
    configs = [
        [3, [0, 1], 'Fixed Income'],
        [3, [4, 5], 'Money Market'],
        [3, [8, 9], 'Forex Swap']
    ]
    
    for start_row, cols, cat_name in configs:
        # Mengambil kolom nama broker dan volume
        temp = df_raw.iloc[start_row:, cols].dropna()
        temp.columns = ['Broker_Name', 'Volume']
        # Buang baris "Grand Total"
        temp = temp[~temp['Broker_Name'].str.contains('Total', case=False, na=False)]
        temp['Category'] = cat_name
        all_data.append(temp)
    
    final_df = pd.concat(all_data, ignore_index=True)
    final_df['Volume'] = final_df['Volume'].apply(clean_volume)
    final_df['Date'] = pd.to_datetime(date_selected).date() # Tambahkan .date() di sini
    
    return final_df

def calculate_ranking(df, category):
    if df.empty:
        return pd.DataFrame(columns=['Rank', 'Broker_Name', 'Volume', 'Percentage (%)'])
    
    filtered_df = df[df['Category'] == category].copy()
    ranked = filtered_df.groupby('Broker_Name')['Volume'].sum().reset_index()
    ranked = ranked.sort_values(by='Volume', ascending=False).reset_index(drop=True)
    
    total_volume = ranked['Volume'].sum()
    ranked['Percentage (%)'] = (ranked['Volume'] / total_volume * 100).round(2) if total_volume > 0 else 0
    ranked.index += 1
    ranked.index.name = 'Rank'
    return ranked.reset_index()

def load_data_from_gdrive(spreadsheet_url):
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_url(spreadsheet_url)
        spreadsheet_title = sheet.title
        
        # MENGAMBIL DATA DARI SEMUA SHEET (Bulan)
        # Karena Anda membagi per bulan, kita akan menggabungkan semuanya
        all_month_data = []
        
        for worksheet in sheet.worksheets():
            # Ambil semua nilai dalam satu sheet
            data_raw = worksheet.get_all_values()
            if not data_raw: continue
            
            df_raw = pd.DataFrame(data_raw)
            
            # Gunakan logika mapping yang sama dengan parse_broker_csv
            # [BarisMulai, [KolomNama, KolomVol], NamaKategori]
            configs = [
                [2, [0, 1], 'Fixed Income'], # Kolom A-B
                [2, [3, 4], 'Money Market'], # Kolom D-E
                [2, [6, 7], 'Forex Swap']    # Kolom G-H
            ]
            
            for start_row, cols, cat_name in configs:
                try:
                    # Ambil kolom spesifik
                    temp = df_raw.iloc[start_row:, cols].copy()
                    temp.columns = ['Broker_Name', 'Volume']
                    
                    # Bersihkan data: hapus baris kosong atau "Grand Total"
                    temp = temp[temp['Broker_Name'] != ""]
                    temp = temp[~temp['Broker_Name'].str.contains('Total|Name', case=False, na=False)]
                    
                    temp['Category'] = cat_name
                    # Ambil nama sheet sebagai tanggal (asumsi nama sheet: "Maret 2026")
                    # Kita set default ke tanggal 1 bulan tersebut
                    temp['Date'] = worksheet.title 
                    
                    all_month_data.append(temp)
                except:
                    continue

        if not all_month_data:
            return pd.DataFrame()

        final_df = pd.concat(all_month_data, ignore_index=True)
        
        # Konversi Volume & Date
        final_df['Volume'] = final_df['Volume'].apply(clean_volume)
        
        # Fungsi pembantu untuk mengubah nama sheet "Maret 2026" menjadi objek date
        def parse_sheet_date(date_str):
            # Ini contoh sederhana, Anda bisa menyesuaikan sesuai format nama sheet Anda
            try:
                # Jika nama sheet "Maret 2026", kita ambil bulan/tahunnya
                return pd.to_datetime(date_str).date()
            except:
                return pd.Timestamp.now().date()

        final_df['Date'] = final_df['Date'].apply(parse_sheet_date)
        
        return final_df, spreadsheet_title
        
    except Exception as e:
        raise Exception(f"Gagal akses Google Drive: {str(e)}")
def get_dummy_data():
    # Sesuaikan agar menggunakan .date() agar seragam dengan data GDrive
    today = pd.Timestamp.now().date()
    last_month = (pd.Timestamp.now().replace(day=1) - pd.Timedelta(days=1)).date()
    
    data = {
        'Date': [last_month, last_month, today, today],
        'Broker_Name': ['Broker Dummy A', 'Broker Dummy B', 'Broker Dummy A', 'Broker Dummy C'],
        'Category': ['Forex Swap', 'Forex Swap', 'Forex Swap', 'Fixed Income'],
        'Volume': [100.0, 85.0, 120.0, 500.0]
    }
    return pd.DataFrame(data)