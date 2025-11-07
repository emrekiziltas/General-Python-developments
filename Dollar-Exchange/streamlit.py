import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)

st.set_page_config(
    page_title="💵 Dollar Exchange Rates Dashboard",
    page_icon="💵",
    layout="wide",       # <-- Burası tam ekran yapıyor
    initial_sidebar_state="expanded"
)


st.title("💵 Dollar Exchange Rates Dashboard")

# CSV yükleme
uploaded_file = st.file_uploader("CSV dosyasını yükleyin", type="csv")
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if df.empty:
            st.warning("⚠️ Yüklenen CSV boş.")
        else:
            st.write("📊 İlk birkaç satır:", df.head())

            # Döviz sütunlarını seç
            currency_columns = [col for col in df.columns if col != 'Date']

            # Her döviz için bir Tab oluştur
            tabs = st.tabs(currency_columns)

            for i, currency in enumerate(currency_columns):
                with tabs[i]:
                    df_curr = df[['Date', currency]].dropna().reset_index(drop=True)

                    # Basit outlier temizleme (%99 üst değerleri kaldır)
                    threshold = df_curr[currency].quantile(0.99)
                    df_curr = df_curr[df_curr[currency] <= threshold]

                    fig = px.line(df_curr, x='Date', y=currency, title=f"Dollar vs {currency}")
                    fig.update_traces(line_color='#0000ff', line_width=2)
                    fig.update_layout(
                        plot_bgcolor='white',
                        title_x=0.5,
                        xaxis_title="Date",
                        yaxis_title=f"Dollar/{currency}",
                        font_family="Courier New",
                        font_color="blue",
                        title_font_family="Times New Roman",
                        title_font_color="red",
                    )
                    st.plotly_chart(fig, use_container_width=True)

    except pd.errors.ParserError as e:
        st.error("❌ CSV dosyası okunamadı. Lütfen formatı kontrol edin.")
    except Exception as e:
        st.error(f"❌ Beklenmeyen bir hata oluştu: {e}")
