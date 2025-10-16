import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd

def date_numb_graph(df, feature):
    years = df["Year"].unique()
    for year in sorted(years):
        fig, ax = plt.subplots(figsize=(15, 8))
        year_df = df[df["Year"] == year]

        for month in sorted(year_df["Month"].unique()):
            month_df = year_df[year_df["Month"] == month]
            counts = month_df[feature].value_counts().sort_index()
            counts.plot(kind="line", ax=ax, marker='o', label=f"Month {month}")

        ax.set_xlabel(feature)
        ax.set_ylabel(f"{feature} per month in {year}")
        ax.set_title(f"{feature} per month in {year} - Number of Reservations")
        ax.legend()
        st.pyplot(fig)

def app(df):
    st.header("📊 Monthly Analysis Report")

    selected_feature = st.selectbox(
        "Select a variable:",
        options=df.columns[1:],
        index=0
    )

    date_numb_graph(df, selected_feature)
