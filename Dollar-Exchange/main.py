import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import warnings
import os

warnings.filterwarnings("ignore")

# Set pandas display options
pd.set_option('display.max_columns', None)

# File path
file_path = './Data/Dollar-Exchange.csv'

try:
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    # Try reading the CSV
    df = pd.read_csv(file_path)

    # Check if DataFrame is empty
    if df.empty:
        raise ValueError("⚠️ The CSV file is empty. Please check your data source.")

    # Display info
    # print("✅ Data loaded successfully!")
    # print(f"Shape: {df.shape}")
    # print(f"Columns: {list(df.columns)}\n")
    # print(df.head())
    print(df.describe(include='all'))
    df.info()
    df_CNY = df[['Date', 'CNY=X']]
    df_CNY.dropna(inplace=True)
    df_CNY.reset_index()

    df_CNY = df[['Date', 'CNY=X']]
    df_CNY.dropna(inplace=True)
    df_CNY.reset_index()
    plt.figure(figsize=(12, 10), dpi=200)
    plot = px.line(x=df_CNY['Date'], y=df_CNY['CNY=X'])
    plot.update_traces(line_color='#0000ff', line_width=2)
    plot.update_layout(
        plot_bgcolor='white',
        title="Dollar vs CNY",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Dollar/CNY",
        font_family="Courier New",
        font_color="blue",
        title_font_family="Times New Roman",
        title_font_color="red",
    )
    plot.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    plot.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    plot.add_shape(
        type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
        x0=0.52, x1=1, xref="paper", y0=6.03, y1=6.31, yref="y"
    )
    plot.add_shape(
        type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
        x0=0.52, x1=1, xref="paper", y0=7, y1=7.3, yref="y"
    )

    plt.tight_layout()
    plot.show()

    df_IRR = df[['Date', 'IRR=X']]
    df_IRR.dropna(inplace=True)
    df_IRR.reset_index()
   7
    noise2 = df_IRR[df_IRR["IRR=X"] > 50000]
    df_IRR.drop(index=noise1.index.union(noise2.index), inplace=True)

    plt.figure(figsize=(12, 10), dpi=200)
    plot = px.line(x=df_IRR['Date'], y=df_IRR['IRR=X'])
    plot.update_traces(line_color='#0000ff', line_width=2)
    plot.update_layout(
        plot_bgcolor='white',
        title="Dollar vs IRR",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Dollar/IRR",
        font_family="Courier New",
        font_color="blue",
        title_font_family="Times New Roman",
        title_font_color="red",
    )
    plot.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    plot.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    plt.tight_layout()
    plot.show();

except FileNotFoundError as e:
    print(e)

except pd.errors.ParserError as e:
    print("❌ Error parsing CSV file. Please check the file format.")
    print(e)

except ValueError as e:
    print(e)

except Exception as e:
    print("❌ An unexpected error occurred:")
    print(e)
