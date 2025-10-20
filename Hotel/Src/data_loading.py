"""
Hotel Reservations Data Analysis Module
========================================
This module provides data loading, inspection, and visualization functions
for hotel reservation datasets using Streamlit.

Author: [Your Name]
Date: October 2025
"""

import os
import io
from typing import Optional

import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import streamlit as st

from config import DATA_DIR

# ========================
# Constants
# ========================
EXPECTED_COLUMNS = [
    "BookingID", "Adults", "Children", "RoomNights", "Persons",
    "MealPlan", "Extras", "RoomType", "RoomID", "Year", "Month", "Day",
    "BookingChannel", "Other1", "Other2", "Other3", "Price",
    "NightFlag", "Status"
]

CSV_FILENAME = 'Hotel Reservations.csv'
DEFAULT_ENCODING = 'utf-8'


# ========================
# Data Loading
# ========================
@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load hotel reservation dataset from CSV file.

    Returns:
        pd.DataFrame: Loaded and preprocessed hotel reservation data.

    Raises:
        FileNotFoundError: If the CSV file cannot be found.
        Exception: For other data loading errors.
    """
    file_path = os.path.join(DATA_DIR, CSV_FILENAME)

    try:
        hotel_df = pd.read_csv(file_path, encoding=DEFAULT_ENCODING)

        # Validate and rename columns
        if len(hotel_df.columns) != len(EXPECTED_COLUMNS):
            st.warning(
                f"⚠️ Column count mismatch. Expected {len(EXPECTED_COLUMNS)}, "
                f"got {len(hotel_df.columns)}. Please verify CSV structure."
            )
        else:
            hotel_df.columns = EXPECTED_COLUMNS

        st.success(f"✅ Successfully loaded {len(hotel_df):,} records.")
        return hotel_df

    except FileNotFoundError as e:
        st.error(f"❌ File not found: {file_path}")
        raise

    except pd.errors.EmptyDataError:
        st.error("❌ The CSV file is empty.")
        raise

    except Exception as e:
        st.error(f"❌ Unexpected error loading data: {str(e)}")
        raise


# ========================
# Data Inspection
# ========================
def inspect_data(df: pd.DataFrame) -> None:
    """
    Display comprehensive dataset overview including shape, structure, and statistics.

    Args:
        df: DataFrame to inspect.
    """
    # Note: Visualization code commented out but retained for future use
    # Uncomment sections below as needed for detailed inspection

    # Dataset shape
    # st.subheader("📊 Data Overview")
    # st.write(f"**Shape:** {df.shape[0]:,} rows × {df.shape[1]} columns")

    # First few rows
    # st.write("**Sample Data:**")
    # st.dataframe(df.head())

    # DataFrame info
    # buffer = io.StringIO()
    # df.info(buf=buffer)
    # info_str = buffer.getvalue()
    # st.text("**DataFrame Info:**")
    # st.text(info_str)

    # Missing values summary
    # st.write("**Missing Values:**")
    # missing_df = pd.DataFrame({
    #     'Column': df.columns,
    #     'Missing Count': df.isnull().sum().values,
    #     'Missing %': (df.isnull().sum().values / len(df) * 100).round(2)
    # })
    # st.dataframe(missing_df[missing_df['Missing Count'] > 0])

    # Descriptive statistics
    # st.write("**Descriptive Statistics:**")
    # st.dataframe(df.describe(include='all'))

    pass


# ========================
# Missing Data Visualization
# ========================
def visualize_missing(df: pd.DataFrame, figsize: tuple = (10, 6)) -> None:
    """
    Generate and display missing data visualizations.

    Args:
        df: DataFrame to analyze for missing values.
        figsize: Figure size as (width, height) tuple. Default is (10, 6).
    """
    st.subheader("🧱 Missing Data Analysis")

    # Create missing data bar chart
    fig, ax = plt.subplots(figsize=figsize)
    msno.bar(df, ax=ax, color='steelblue', fontsize=10)
    plt.title("Missing Data Distribution", fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Missing values summary table
    st.write("**Missing Values Summary:**")
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0].sort_values(ascending=False)

    if len(missing_data) > 0:
        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing Count': missing_data.values,
            'Percentage': (missing_data.values / len(df) * 100).round(2)
        }).reset_index(drop=True)
        st.dataframe(missing_df, use_container_width=True)
    else:
        st.success("✨ No missing values detected in the dataset.")


# ========================
# Utility Functions
# ========================
def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Generate a comprehensive summary of the dataset.

    Args:
        df: DataFrame to summarize.

    Returns:
        dict: Summary statistics including shape, types, and missing values.
    """
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'total_missing': df.isnull().sum().sum(),
        'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 ** 2)
    }


if __name__ == "__main__":
    # Module testing
    st.title("Hotel Reservations Data Analysis")

    try:
        data = load_data()
        inspect_data(data)
        visualize_missing(data)

        # Display summary
        summary = get_data_summary(data)
        st.sidebar.json(summary)

    except Exception as e:
        st.error(f"Application error: {str(e)}")