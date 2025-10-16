import streamlit as st
import dashboard
import reservations
import reports
from css import CUSTOM_CSS

# Page configuration
st.set_page_config(page_title="Hotel Dashboard", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def load_tabs(data):
    st.title("📊 Hotel Dashboard")

    # --- Sidebar Filters ---
    st.sidebar.title("🔧 Filters")

    # Multi-year selection
    years = st.sidebar.multiselect(
        "Select Year",
        options=sorted(data["Year"].unique()),
        default=sorted(data["Year"].unique())
    )
    # If user selects no year
    if not years:
        st.warning("⚠️ Please select at least one year.")
        st.stop()  # Prevents further execution

    meal_plan = st.sidebar.selectbox("Meal Plan", sorted(data["MealPlan"].unique()))

    booking_channels = st.sidebar.multiselect(
        "Booking Channel",
        options=sorted(data["BookingChannel"].unique()),
        default=sorted(data["BookingChannel"].unique())
    )

    # Apply filters
    filtered_data = data[
        (data["Year"].isin(years)) &
        (data["MealPlan"] == meal_plan) &
        (data["BookingChannel"].isin(booking_channels))
    ].reset_index(drop=True)

    # If filtered data is empty
    if filtered_data.empty:
        st.warning("⚠️ No records match these filters. Please try different filter selections.")
        st.stop()

    # --- KPI Metrics ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"₺ {filtered_data['Price'].sum():,.0f}")
    with col2:
        st.metric("Total Reservations", len(filtered_data))
    with col3:
        st.metric("Cancelled", len(filtered_data[filtered_data["Status"] == "Canceled"]))

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["📈 Sales Report", "💰 Cost Report", "💹 Profit Analysis"])

    with tab1:
        dashboard.app(filtered_data)
    with tab2:
        reservations.app(filtered_data)
    with tab3:
        reports.app(filtered_data)
