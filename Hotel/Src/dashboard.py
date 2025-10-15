import streamlit as st
import plotly.express as px

def app(df):
    st.header("📈 Satış Raporu")
    fig1 = px.bar(df, x="Ay", y="Satış", title="Aylık Satışlar")
    st.plotly_chart(fig1)