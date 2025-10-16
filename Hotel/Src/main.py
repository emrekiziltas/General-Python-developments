from data_loading import load_data, inspect_data, visualize_missing
from tabs import load_tabs
from css import CUSTOM_CSS
import streamlit as st

def main():
    # Sayfa yapılandırması
    st.set_page_config(page_title="Hotel Dashboard", layout="wide")

    # CSS uygula
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Veri yükle
    data = load_data()

    # Veri incele
    inspect_data(data)

    # Eksik verileri görselleştir (isteğe bağlı)
    # visualize_missing(data)

    # Dashboard sekmelerini yükle
    load_tabs(data)

if __name__ == "__main__":
    main()
