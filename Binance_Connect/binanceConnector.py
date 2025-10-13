# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 16:25:44 2025

@author: ek675
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 16:12:34 2025

@author: ek675
"""

import os
import requests
import pandas as pd
import time
import datetime


def fetch_and_save(symbol, interval='1m', limit=1000, total_minutes=1440):
    """
    symbol: Binance sembolü (ör: 'BTCUSDT')
    interval: veri aralığı ('1m' = 1 dakika)
    limit: API'den tek seferde çekilen maksimum veri
    total_minutes: çekilecek toplam dakika sayısı (ör: 1440 = 24 saat)
    """

    # Klasör adı olarak sembolü kullan (ör: 'btcusdt_data')
    directory = symbol.lower() + '_data'
    if not os.path.exists(directory):
        os.makedirs(directory)

    all_data = []

    now = int(time.time() * 1000)  # Şu an milisaniye cinsinden
    start_time = now - total_minutes * 60 * 1000  # Başlangıç zamanı (şu an - total_minutes)

    while start_time < now:
        url = f'https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}&startTime={start_time}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        all_data.extend(data)

        last_open_time = data[-1][0]
        start_time = last_open_time + 60 * 1000  # 1 dakika ileri

        time.sleep(0.1)  # API hız limiti için ufak bekleme

    # DataFrame oluşturma
    df = pd.DataFrame(all_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

    base_directory = r"C:\Users\ek675\rickandmorty"

    # Create subdirectory based on symbol (e.g., btcusdt_data)
    symbol_folder = f"{symbol.lower()}_data"
    directory = os.path.join(base_directory, symbol_folder)

    # Create the folder if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Create the timestamped file path
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    file_path = os.path.join(directory, f"{symbol.lower()}_1m_data_{now_str}.csv")

    # CSV olarak kaydet
    df.to_csv(file_path, index=False)
    print(f"{symbol} verisi '{file_path}' dosyasına kaydedildi.")


# BTCUSDT ve ETHUSDT için veri çek ve kaydet
fetch_and_save('BTCUSDT')
fetch_and_save('ETHUSDT')
