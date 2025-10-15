import streamlit as st
import plotly.express as px

def app(df):
    st.header("💰 Maliyet Raporu")
    fig2 = px.line(df, x="Ay", y="Maliyet", title="Aylık Maliyetler")
    st.plotly_chart(fig2)