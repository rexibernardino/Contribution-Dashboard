import pandas as pd

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

def get_dummy_data():
    # Fungsi ini diperlukan agar aplikasi tidak error saat pertama kali dibuka
    today = pd.Timestamp.now().normalize()
    last_month = (today.replace(day=1) - pd.Timedelta(days=1)).replace(day=1)
    
    data = {
        'Date': [last_month, last_month, today, today],
        'Broker_Name': ['Broker Dummy A', 'Broker Dummy B', 'Broker Dummy A', 'Broker Dummy C'],
        'Category': ['Forex Swap', 'Forex Swap', 'Forex Swap', 'Fixed Income'],
        'Volume': [100.0, 85.0, 120.0, 500.0]
    }
    return pd.DataFrame(data)