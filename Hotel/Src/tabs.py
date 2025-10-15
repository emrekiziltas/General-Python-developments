import streamlit as st
import pandas as pd

# Alt sayfaları içe aktar
import dashboard
import reservations
import reports

from css import CUSTOM_CSS

# Sayfa yapılandırması (ilk satırda)
st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def load_tabs():
    st.title("📊 Çok Sekmeli Rapor Arayüzü")

    # Örnek veri
    df = pd.DataFrame({
        "Ay": ["Ocak", "Şubat", "Mart", "Nisan"],
        "Satış": [150, 200, 180, 220],
        "Maliyet": [100, 120, 90, 130]
    })

    # Sidebar filtreleri
    st.sidebar.title("🔧 Filtreler")
    year = st.sidebar.selectbox("Yıl", [2023, 2024, 2025])
    region = st.sidebar.multiselect("Bölge", ["Marmara", "Ege", "İç Anadolu"], default=["Marmara"])

    # KPI metrikleri
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Satış", "₺ 1.2M", "+5%")
    with col2:
        st.metric("Toplam Maliyet", "₺ 870K", "-3%")
    with col3:
        st.metric("Net Kar", "₺ 330K", "+8%")

    # Sekmeler
    tab1, tab2, tab3 = st.tabs(["📈 Satış Raporu", "💰 Maliyet Raporu", "💹 Kar Analizi"])

    with tab1:
        dashboard.app(df)
    with tab2:
        reservations.app(df)
    with tab3:
        reports.app(df)

if __name__ == "__main__":
    load_tabs()
