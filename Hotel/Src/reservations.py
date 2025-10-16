import streamlit as st
import matplotlib.pyplot as plt

def app(df):
    st.header("💰 Maliyet Raporu")

    # avg_price_per_room yoksa oluştur
    if "avg_price_per_room" not in df.columns:
        df["avg_price_per_room"] = df.apply(
            lambda x: x["Price"] / x["RoomNights"] if x["RoomNights"] > 0 else 0,
            axis=1
        )

    # Veriyi al ve sıralı hale getir
    price_counts = df["avg_price_per_room"].value_counts().sort_index()

    # Sekmeler ile farklı aralıkları göster
    tab1, tab2, tab3 = st.tabs(["Tüm Aralık", "0-100", "100-200"])

    # 1️⃣ Tüm Aralık
    with tab1:
        fig, ax = plt.subplots(figsize=(10, 5))
        price_counts.plot(ax=ax, color="#2E7D32")
        ax.set_title("Ortalama Oda Fiyatı Dağılımı (Tüm Aralık)")
        ax.set_xlabel("Fiyat Aralığı")
        ax.set_ylabel("Frekans")
        ax.set_ylim(0, 300)
        st.pyplot(fig)

    # 2️⃣ 0-100
    with tab2:
        fig, ax = plt.subplots(figsize=(10, 5))
        price_counts.plot(ax=ax, color="#C3EBE3")
        ax.set_xlim(0, 100)
        ax.set_title("Oda Fiyatı Dağılımı (0-100)")
        ax.set_xlabel("Fiyat Aralığı")
        ax.set_ylabel("Frekans")
        ax.set_ylim(0, 300)
        st.pyplot(fig)

    # 3️⃣ 100-200
    with tab3:
        fig, ax = plt.subplots(figsize=(10, 5))
        price_counts.plot(ax=ax, color="#FFA726")
        ax.set_xlim(100, 200)
        ax.set_title("Oda Fiyatı Dağılımı (100-200)")
        ax.set_xlabel("Fiyat Aralığı")
        ax.set_ylabel("Frekans")
        ax.set_ylim(0, 300)
        st.pyplot(fig)



