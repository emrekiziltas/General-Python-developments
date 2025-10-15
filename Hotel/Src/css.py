import streamlit as st
# css.py

CUSTOM_CSS = """
<style>
/* Metric değerlerini renklendir */
div[data-testid="stMetricValue"] {
    color: #E6e6fa;
    font-weight: bold;
    font-size: 26px;
}

/* Sekme başlıklarını kalın yap */
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] p {
    font-weight: 600;
}

/* Sayfa genelinde daha ferah bir görünüm */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    padding-left: 3rem;
    padding-right: 3rem;
}
</style>
"""
