import streamlit as st
import pandas as pd

# Sample data for demonstration purposes
data = {
    "Name": ["John", "Mary", "Jane", "Alice", "Bob"],
    "Age": [25, 32, 43, 28, 38],
    "Income ($):": [50000, 60000, 40000, 70000, 80000]
}
df = pd.DataFrame(data)

# Title
st.title("Advanced Dashboard")

# Inputs
income_input = st.number_input("Income ($):", min_value=20000, max_value=150000, value=50000, step=10000)
age_input = st.slider("Age:", min_value=18, max_value=100, value=25, step=5)

# Filter and display DataFrame
filtered_df = pd.DataFrame()  # Initialize empty df to avoid reference before assignment

if st.button("Update DataFrame"):
    filtered_df = df[(df["Income ($):"] > income_input) & (df["Age"] > age_input)]

    if not filtered_df.empty:
        st.write("Filtered DataFrame:")
        st.table(filtered_df)
    else:
        st.info("No matching records found.")

# Optional: Input validation (if needed beyond widget constraints)
# These are redundant with current widget settings but included for reference
if income_input < 0 or income_input > 150000:
    st.warning("Invalid income value!")
if age_input < 0 or age_input > 100:
    st.warning("Invalid age value!")
