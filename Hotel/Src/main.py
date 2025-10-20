"""
Hotel Reservations Dashboard - Main Application
================================================
Main entry point for the Hotel Reservations Analytics Dashboard.
Orchestrates data loading, UI rendering, and tab navigation.

Author: [Your Name]
Date: October 2025
Version: 2.0.0
"""

import logging
from typing import Optional

import streamlit as st

from data_loading import load_data, inspect_data, visualize_missing
from tabs import load_tabs
from css import CUSTOM_CSS

# ========================
# Configuration
# ========================
PAGE_TITLE = "Hotel Reservations Dashboard"
PAGE_ICON = "🏨"
LAYOUT = "wide"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========================
# Application Setup
# ========================
def configure_page() -> None:
    """
    Configure Streamlit page settings and apply custom styling.

    Sets page title, icon, layout, and applies custom CSS.
    """
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS styling
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    logger.info("Page configuration completed")


# ========================
# Data Management
# ========================
def initialize_data() -> Optional[object]:
    """
    Load and validate hotel reservation data.

    Returns:
        DataFrame or None: Loaded data if successful, None otherwise.

    Raises:
        Exception: Propagates any data loading errors for handling.
    """
    try:
        logger.info("Initializing data loading process")
        data = load_data()

        if data is None or data.empty:
            st.error("❌ Failed to load data: Dataset is empty")
            logger.error("Data loading returned empty dataset")
            return None

        logger.info(f"Data loaded successfully: {len(data)} records")
        return data

    except FileNotFoundError as e:
        st.error(f"❌ Data file not found: {str(e)}")
        logger.error(f"File not found: {e}")
        return None

    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        logger.exception("Unexpected error during data loading")
        return None


# ========================
# UI Components
# ========================
def render_header() -> None:
    """
    Render the main dashboard header with title and description.
    """
    st.title("🏨 Hotel Reservations Analytics Dashboard")
    st.markdown(
        """
        <div style='margin-bottom: 2rem;'>
            <p style='font-size: 1.1rem; color: #666;'>
                Comprehensive analysis and insights for hotel reservation data.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")


def render_sidebar_info() -> None:
    """
    Render sidebar information and controls.
    """
    st.sidebar.title("ℹ️ Dashboard Info")
    st.sidebar.markdown(
        """
        **Version:** 2.0.0  
        **Last Updated:** October 2025

        ---

        ### 📊 Features
        - Data Overview & Statistics
        - Missing Data Analysis
        - Interactive Visualizations
        - Custom Filtering Options

        ---

        ### 🔧 Settings
        """
    )

    # Optional: Add settings controls
    show_data_inspection = st.sidebar.checkbox(
        "Show Data Inspection",
        value=False,
        help="Display detailed data inspection information"
    )

    show_missing_viz = st.sidebar.checkbox(
        "Show Missing Data Visualization",
        value=False,
        help="Display missing data analysis charts"
    )

    return show_data_inspection, show_missing_viz


def display_error_state(error_message: str) -> None:
    """
    Display a user-friendly error state when data loading fails.

    Args:
        error_message: The error message to display.
    """
    st.error(f"❌ {error_message}")

    st.markdown(
        """
        ### 🔍 Troubleshooting Steps:
        1. Verify that the data file exists in the correct directory
        2. Check file permissions and accessibility
        3. Ensure the CSV file format is correct
        4. Review the configuration in `config.py`

        ### 📝 Need Help?
        Check the application logs for more detailed error information.
        """
    )

    logger.error(f"Application in error state: {error_message}")


# ========================
# Main Application
# ========================
def main() -> None:
    """
    Main application entry point.

    Orchestrates the entire dashboard workflow:
    1. Configure page and styling
    2. Load and validate data
    3. Render UI components
    4. Display analytics tabs
    """
    # Configure page
    configure_page()

    # Render header
    render_header()

    # Render sidebar and get user preferences
    show_inspection, show_missing = render_sidebar_info()

    # Initialize data
    data = initialize_data()

    # Handle data loading failure
    if data is None:
        display_error_state("Unable to load hotel reservation data")
        return

    # Optional: Display data inspection
    if show_inspection:
        with st.expander("📋 Data Inspection", expanded=False):
            inspect_data(data, show_details=True)

    # Optional: Display missing data visualization
    if show_missing:
        with st.expander("🧱 Missing Data Analysis", expanded=False):
            visualize_missing(data)

    # Load main dashboard tabs
    try:
        logger.info("Loading dashboard tabs")
        load_tabs(data)
        logger.info("Dashboard rendered successfully")

    except Exception as e:
        st.error(f"❌ Error rendering dashboard: {str(e)}")
        logger.exception("Failed to render dashboard tabs")

        # Provide fallback information
        st.info("💡 Try refreshing the page or contact support if the issue persists.")


# ========================
# Application Entry Point
# ========================
if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("Starting Hotel Reservations Dashboard Application")
        logger.info("=" * 60)

        main()

        logger.info("Application execution completed")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")

    except Exception as e:
        logger.exception("Critical application error")
        st.error("❌ A critical error occurred. Please check the logs.")

    finally:
        logger.info("Application shutdown")