import streamlit as st
import plotly.graph_objects as go

def app(df):
    st.subheader("📊 Analysis Reports")

    selected_feature = st.selectbox(
        "Select a variable:",
        options=df.columns[1:],
        index=0
    )

    make_bar_graph(selected_feature, df)


def make_bar_graph(feature, df):
    primary_color = st.get_option("theme.primaryColor") or "#e35f62"

    value_counts = df[feature].value_counts()

    # Sort index numerically or alphabetically
    if value_counts.index.dtype == 'O':  # categorical
        sorted_data = value_counts.sort_index()
    else:
        sorted_data = value_counts.sort_index()

    x = sorted_data.index.astype(str)
    y = sorted_data.values

    fig = go.Figure([
        go.Bar(
            x=x,
            y=y,
            marker_color=primary_color,
            text=y,
            textposition='outside',
            hovertemplate=f"{feature}: %{x}<br>Count: %{y}<extra></extra>"
        )
    ])

    fig.update_layout(
        title=dict(text=f"{feature} Distribution", x=0.5, xanchor='center'),
        xaxis=dict(title=feature, tickangle=45),
        yaxis=dict(title="Count"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=500,
        margin=dict(t=80, b=80)
    )

    st.plotly_chart(fig, use_container_width=True)
