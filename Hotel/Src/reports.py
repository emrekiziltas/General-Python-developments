import streamlit as st
import plotly.express as px

def app(df):
        st.header("💹 Kar Analizi")
        df["Kar"] = df["Satış"] - df["Maliyet"]
        fig3 = px.area(df, x="Ay", y="Kar", title="Aylık Kar Grafiği")
        st.plotly_chart(fig3)
        st.dataframe(df)