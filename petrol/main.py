import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- YAPILANDIRMA (Configuration) ---

# yfinance Sembolleri:
# Not: yfinance doğrudan Brent Crude veya Henry Hub'ı sağlamaz.
# Alternatif olarak, onlara yakından ilişkili olan vadeli işlem kontratları veya ETF'ler kullanılır.

COMMODITY_SYMBOLS = {
    # 1. Brent Crude Petrol (İlişkili Vadeli İşlem Kontratı)
    # yfinance'da, Brent Crude genellikle 'BZO=F' (ICE Brent Futures) veya
    # 'BRENT' sembolüyle bulunur. BZO=F en yaygın kullanılanıdır.
    "Brent Crude": "BNO",

    # 2. Doğal Gaz (Henry Hub) (Vadeli İşlem Kontratı)
    # Henry Hub doğal gaz vadeli işlemleri için standart sembol.
    "Natural Gas (Henry Hub)": "NG=F"
}

# Veri Aralığı: Bugünün tarihinden 1 yıl öncesine kadar
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')


# --- FONKSİYONLAR (Functions) ---

def fetch_yfinance_data(symbol, start, end):
    """
    yfinance kütüphanesini kullanarak belirli bir sembol için tarihsel veriyi çeker.
    """
    try:
        # Veriyi çek
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end)

        # Sadece Kapanış fiyatını al (diğer sütunlar isteğe bağlı)
        if 'Close' in df.columns:
            return df[['Close']]
        else:
            print(f"  ⚠️ Uyarı: {symbol} için 'Close' sütunu bulunamadı.")
            return pd.DataFrame()

    except Exception as e:
        print(f"  ❌ Hata: {symbol} verisi çekilemedi. Hata: {e}")
        return pd.DataFrame()


# --- ANA ÇALIŞMA (Main Execution) ---

print(f"💰 yfinance'dan {start_date} - {end_date} arasındaki veriler çekiliyor...")

# Tüm verileri birleştirmek için bir DataFrame oluştur
all_data = pd.DataFrame()

for name, symbol in COMMODITY_SYMBOLS.items():
    print(f"\n-> {name} ({symbol}) verisi çekiliyor...")

    # 1. Veriyi çek
    commodity_df = fetch_yfinance_data(symbol, start_date, end_date)

    if not commodity_df.empty:
        # 2. Sütunu emtia adı ile yeniden adlandır
        commodity_df.columns = [f"{name.replace(' ', '_')}_Price"]

        # 3. Ana DataFrame'e birleştir
        if all_data.empty:
            all_data = commodity_df
        else:
            # Ortak tarihleri kullanarak birleştirme (İndeks tarih olduğundan)
            all_data = all_data.join(commodity_df, how='outer')

        print(f"  ✅ {name} için {len(commodity_df)} günlük veri çekildi.")
    else:
        print(f"  ❌ {name} için veri çekimi başarısız oldu.")

# --- SONUÇLARI GÖRÜNTÜLEME ve KAYDETME (Display & Save Results) ---

if not all_data.empty:
    # İndeks adını "Date" olarak belirle
    all_data.index.name = 'Date'

    # NaN değerlerini bir önceki geçerli değerle doldur (opsiyonel ama önerilir)
    #all_data.fillna(method='ffill', inplace=True)
    all_data.ffill(inplace=True)  # <<< YENİ VE ÖNERİLEN KULLANIM

    print("\n--- ÇEKİLEN VERİNİN İLK 5 SATIRI ---")
    print(all_data.head())

    print("\n--- ÇEKİLEN VERİNİN SON 5 SATIRI ---")
    print(all_data.tail())

    # Veriyi bir CSV dosyasına kaydetme
    file_name = f"yfinance_commodities_{datetime.now().strftime('%Y%m%d')}.csv"
    all_data.to_csv(file_name)
    print(f"\n✅ Veriler '{file_name}' dosyasına başarıyla kaydedildi.")

else:
    print("\n⚠️ Hata: Hiçbir emtia için veri çekilemedi.")