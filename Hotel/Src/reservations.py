import streamlit as st
import matplotlib.pyplot as plt

def app(df):
    st.header("💰 Cost Report")

    # Create avg_price_per_room if missing
    if "avg_price_per_room" not in df.columns:
        df["avg_price_per_room"] = df.apply(
            lambda x: x["Price"] / x["RoomNights"] if x["RoomNights"] > 0 else 0,
            axis=1
        )

    price_counts = df["avg_price_per_room"].value_counts().sort_index()

    # Tabs for different ranges
    tab1, tab2, tab3 = st.tabs(["All Range", "0-100", "100-200"])

    with tab1:
        fig, ax = plt.subplots(figsize=(10,5))
        price_counts.plot(ax=ax, color="#2E7D32")
        ax.set_title("Average Room Price Distribution (All Range)")
        ax.set_xlabel("Price")
        ax.set_ylabel("Frequency")
        ax.set_ylim(0, 300)
        st.pyplot(fig)

    with tab2:
        fig, ax = plt.subplots(figsize=(10,5))
        price_counts_0_100 = price_counts[price_counts.index <= 100]
        price_counts_0_100.plot(ax=ax, color="#C3EBE3")
