"""
Customer Value Assessment Module with Streamlit Interface
==========================================================
This module performs customer evaluation based on purchasing behavior metrics.

Author: [Your Name]
Date: November 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Tuple
import streamlit as st


class CustomerValueAssessor:
    """
    A class to perform customer value assessment based on purchase behavior.

    Attributes:
        transaction_data (pd.DataFrame): The input transaction dataset
        evaluation_results (pd.DataFrame): The calculated metrics and scores
    """

    # Score Weighting Configuration
    TIME_WEIGHT = 0.15
    PURCHASE_COUNT_WEIGHT = 0.28
    REVENUE_WEIGHT = 0.57
    FINAL_MULTIPLIER = 0.05

    # Classification Boundaries
    TIER_BOUNDARIES = {
        'Premium Tier': 4.5,
        'Gold Tier': 4.0,
        'Silver Tier': 3.0,
        'Bronze Tier': 1.6
    }

    def __init__(self, data_path: str):
        """
        Initialize the Customer Value Assessor with a dataset.

        Args:
            data_path (str): Path to the CSV file containing transaction data
        """
        self.transaction_data = self._import_records(data_path)
        self.evaluation_results = None

    def _import_records(self, data_path: str) -> pd.DataFrame:
        """
        Load and preprocess the transaction data.

        Args:
            data_path (str): Path to the CSV file

        Returns:
            pd.DataFrame: Preprocessed transaction data
        """
        records = pd.read_csv(data_path)
        records['PurchaseDate'] = pd.to_datetime(records['PurchaseDate'])
        return records

    def compute_time_metric(self) -> pd.DataFrame:
        """
        Calculate time-based metric for each customer.

        Time metric is defined as days since the customer's most recent purchase.

        Returns:
            pd.DataFrame: DataFrame with CustomerID and time metric columns
        """
        time_analysis = self.transaction_data.groupby('CustomerID', as_index=False)['PurchaseDate'].max()
        time_analysis.columns = ['CustomerID', 'MostRecentDate']

        benchmark_date = time_analysis['MostRecentDate'].max()
        time_analysis['DaysSinceLastPurchase'] = time_analysis['MostRecentDate'].apply(
            lambda date: (benchmark_date - date).days
        )

        return time_analysis[['CustomerID', 'DaysSinceLastPurchase']]

    def compute_transaction_count(self) -> pd.DataFrame:
        """
        Calculate transaction count metric for each customer.

        Count is defined as the number of unique transactions per customer.

        Returns:
            pd.DataFrame: DataFrame with CustomerID and transaction count columns
        """
        count_analysis = (
            self.transaction_data.drop_duplicates()
            .groupby('CustomerID', as_index=False)['PurchaseDate']
            .count()
        )
        count_analysis.columns = ['CustomerID', 'TransactionCount']

        return count_analysis

    def compute_revenue_metric(self) -> pd.DataFrame:
        """
        Calculate revenue metric for each customer.

        Revenue value is the total amount spent by each customer.

        Returns:
            pd.DataFrame: DataFrame with CustomerID and revenue columns
        """
        revenue_analysis = self.transaction_data.groupby('CustomerID', as_index=False)['TransactionAmount'].sum()
        revenue_analysis.columns = ['CustomerID', 'TotalRevenue']

        return revenue_analysis

    def compute_overall_score(self, time_weight=None, count_weight=None, revenue_weight=None) -> pd.DataFrame:
        """
        Calculate overall value scores and rankings for all customers.

        Args:
            time_weight (float): Weight for recency (optional, uses default if None)
            count_weight (float): Weight for frequency (optional, uses default if None)
            revenue_weight (float): Weight for monetary (optional, uses default if None)

        Returns:
            pd.DataFrame: Complete analysis with scores and rankings
        """
        # Use custom weights or defaults
        tw = time_weight if time_weight is not None else self.TIME_WEIGHT
        cw = count_weight if count_weight is not None else self.PURCHASE_COUNT_WEIGHT
        rw = revenue_weight if revenue_weight is not None else self.REVENUE_WEIGHT

        # Calculate individual metrics
        time_metrics = self.compute_time_metric()
        count_metrics = self.compute_transaction_count()
        revenue_metrics = self.compute_revenue_metric()

        # Merge all metrics
        combined_data = (
            time_metrics
            .merge(count_metrics, on='CustomerID')
            .merge(revenue_metrics, on='CustomerID')
        )

        # Calculate rankings (lower time is better, higher count/revenue is better)
        combined_data['TimeRanking'] = combined_data['DaysSinceLastPurchase'].rank(ascending=True)
        combined_data['CountRanking'] = combined_data['TransactionCount'].rank(ascending=False)
        combined_data['RevenueRanking'] = combined_data['TotalRevenue'].rank(ascending=False)

        # Normalize rankings to 0-100 scale
        for metric in ['TimeRanking', 'CountRanking', 'RevenueRanking']:
            combined_data[f'{metric}_Normalized'] = (combined_data[metric] / combined_data[metric].max()) * 100

        # Calculate weighted overall score with custom or default weights
        combined_data['OverallScore'] = (
                                                tw * combined_data['TimeRanking_Normalized'] +
                                                cw * combined_data['CountRanking_Normalized'] +
                                                rw * combined_data['RevenueRanking_Normalized']
                                        ) * self.FINAL_MULTIPLIER

        # Round for readability
        combined_data = combined_data.round(2)

        self.evaluation_results = combined_data
        return combined_data

    def classify_customers(self, time_weight=None, count_weight=None, revenue_weight=None) -> pd.DataFrame:
        """
        Classify customers based on their overall scores.

        Args:
            time_weight (float): Weight for recency (optional)
            count_weight (float): Weight for frequency (optional)
            revenue_weight (float): Weight for monetary (optional)

        Returns:
            pd.DataFrame: Data with customer classifications assigned
        """
        if self.evaluation_results is None:
            self.compute_overall_score(time_weight, count_weight, revenue_weight)
        elif time_weight is not None or count_weight is not None or revenue_weight is not None:
            # Recalculate if weights are provided
            self.compute_overall_score(time_weight, count_weight, revenue_weight)

        criteria = [
            self.evaluation_results['OverallScore'] > self.TIER_BOUNDARIES['Premium Tier'],
            self.evaluation_results['OverallScore'] > self.TIER_BOUNDARIES['Gold Tier'],
            self.evaluation_results['OverallScore'] > self.TIER_BOUNDARIES['Silver Tier'],
            self.evaluation_results['OverallScore'] > self.TIER_BOUNDARIES['Bronze Tier']
        ]

        tier_labels = [
            'Premium Tier',
            'Gold Tier',
            'Silver Tier',
            'Bronze Tier',
            'Low Activity Tier'
        ]

        self.evaluation_results['CustomerTier'] = np.select(criteria, tier_labels[:-1], default=tier_labels[-1])

        return self.evaluation_results

    def get_top_performers(self, limit: int = 20) -> pd.DataFrame:
        """
        Get a summary of top-performing customers by overall score.

        Args:
            limit (int): Number of top customers to display

        Returns:
            pd.DataFrame: Summary of top customers
        """
        if self.evaluation_results is None or 'CustomerTier' not in self.evaluation_results.columns:
            self.classify_customers()

        return self.evaluation_results[['CustomerID', 'OverallScore', 'CustomerTier']].head(limit)

    def get_filtered_data(self, tier_filter=None, min_score=None, max_score=None):
        """
        Get filtered customer data based on parameters.

        Args:
            tier_filter (list): List of tiers to include
            min_score (float): Minimum overall score
            max_score (float): Maximum overall score

        Returns:
            pd.DataFrame: Filtered customer data
        """
        if self.evaluation_results is None or 'CustomerTier' not in self.evaluation_results.columns:
            self.classify_customers()

        filtered_data = self.evaluation_results.copy()

        if tier_filter:
            filtered_data = filtered_data[filtered_data['CustomerTier'].isin(tier_filter)]

        if min_score is not None:
            filtered_data = filtered_data[filtered_data['OverallScore'] >= min_score]

        if max_score is not None:
            filtered_data = filtered_data[filtered_data['OverallScore'] <= max_score]

        return filtered_data

    def visualize_tier_breakdown(self, chart_size: Tuple[int, int] = (12, 8), filtered_data=None):
        """
        Create a pie chart showing the distribution of customer tiers.

        Args:
            chart_size (tuple): Figure size as (width, height)
            filtered_data (pd.DataFrame): Optional filtered data to visualize
        """
        if self.evaluation_results is None or 'CustomerTier' not in self.evaluation_results.columns:
            self.classify_customers()

        data_to_plot = filtered_data if filtered_data is not None else self.evaluation_results
        tier_distribution = data_to_plot['CustomerTier'].value_counts()

        figure, axis = plt.subplots(figsize=chart_size)

        # Create pie chart with adjusted parameters
        slices, tier_labels, percentages = axis.pie(
            tier_distribution,
            labels=tier_distribution.index,
            autopct='%1.1f%%',
            startangle=105,
            colors=plt.cm.Set3.colors,
            pctdistance=0.85,
            textprops={'fontsize': 10}
        )

        # Adjust label properties for better readability
        for label in tier_labels:
            label.set_fontsize(11)
            label.set_weight('bold')

        for percentage in percentages:
            percentage.set_color('white')
            percentage.set_fontsize(10)
            percentage.set_weight('bold')

        plt.title('Customer Tier Distribution\n',
                  fontsize=14,
                  fontweight='bold',
                  pad=20)

        plt.axis('equal')
        plt.tight_layout()

        return figure

    def visualize_score_histogram(self, chart_size: Tuple[int, int] = (12, 6), bar_count: int = 30, filtered_data=None):
        """
        Create a histogram showing the distribution of overall scores.

        Args:
            chart_size (tuple): Figure size as (width, height)
            bar_count (int): Number of bars for the histogram
            filtered_data (pd.DataFrame): Optional filtered data to visualize
        """
        if self.evaluation_results is None or 'CustomerTier' not in self.evaluation_results.columns:
            self.classify_customers()

        data_to_plot = filtered_data if filtered_data is not None else self.evaluation_results

        figure, axis = plt.subplots(figsize=chart_size)

        # Create histogram
        frequencies, bar_edges, rectangles = axis.hist(
            data_to_plot['OverallScore'],
            bins=bar_count,
            color='skyblue',
            edgecolor='black',
            alpha=0.7
        )

        # Color bars by tier boundaries
        for index, rectangle in enumerate(rectangles):
            bar_left = bar_edges[index]
            bar_right = bar_edges[index + 1]
            bar_midpoint = (bar_left + bar_right) / 2

            if bar_midpoint > self.TIER_BOUNDARIES['Premium Tier']:
                rectangle.set_facecolor('#2ecc71')
            elif bar_midpoint > self.TIER_BOUNDARIES['Gold Tier']:
                rectangle.set_facecolor('#3498db')
            elif bar_midpoint > self.TIER_BOUNDARIES['Silver Tier']:
                rectangle.set_facecolor('#f39c12')
            elif bar_midpoint > self.TIER_BOUNDARIES['Bronze Tier']:
                rectangle.set_facecolor('#e74c3c')
            else:
                rectangle.set_facecolor('#95a5a6')

            for boundary in self.TIER_BOUNDARIES.values():
                if bar_left <= boundary < bar_right:
                    rectangle.set_edgecolor('black')
                    rectangle.set_linewidth(2)
                    rectangle.set_hatch('//')

        average_score = data_to_plot['OverallScore'].mean()
        middle_score = data_to_plot['OverallScore'].median()

        axis.axvline(average_score, color='purple', linestyle='-', linewidth=2,
                     label=f'Mean: {average_score:.2f}')
        axis.axvline(middle_score, color='pink', linestyle='-', linewidth=2,
                     label=f'Median: {middle_score:.2f}')

        for tier_name, boundary_value in self.TIER_BOUNDARIES.items():
            y_value = np.interp(boundary_value, bar_edges[:-1], frequencies)
            axis.scatter(boundary_value, y_value, color='black', s=80, marker='o', zorder=5)
            axis.text(
                boundary_value,
                y_value + max(frequencies) * 0.05,
                tier_name,
                ha='center',
                va='bottom',
                fontsize=9,
                color='black',
                fontweight='bold',
                rotation=30,
                rotation_mode='anchor',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7)
            )

        axis.set_xlabel('Overall Score', fontsize=12, fontweight='bold')
        axis.set_ylabel('Number of Customers', fontsize=12, fontweight='bold')
        axis.set_title('Overall Score Distribution\n', fontsize=14, fontweight='bold', pad=15)
        axis.grid(axis='y', alpha=0.3, linestyle='--')
        axis.legend(loc='upper right', fontsize=9)

        statistics_summary = f'Total Customers: {len(data_to_plot)}\n'
        statistics_summary += f'Mean Score: {average_score:.2f}\n'
        statistics_summary += f'Median Score: {middle_score:.2f}\n'
        statistics_summary += f'Std Dev: {data_to_plot["OverallScore"].std():.2f}'

        axis.text(
            0.02, 0.98, statistics_summary,
            transform=axis.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        plt.tight_layout()

        return figure


def create_streamlit_app():
    """
    Create Streamlit dashboard with tabs for different reports.
    """
    st.set_page_config(
        page_title="Customer Value Assessment Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Customer Value Assessment Dashboard")
    st.markdown("---")

    # File uploader
    uploaded_file = st.file_uploader("Upload Customer Dataset (CSV)", type=['csv'])

    if uploaded_file is not None:
        # Save uploaded file temporarily
        with open("dataset.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Initialize assessor
        assessor = CustomerValueAssessor('dataset.csv')
        assessor.classify_customers()

        # Sidebar filters (for future use)
        st.sidebar.header("🔍 Filters")
        st.sidebar.markdown("*Apply filters to all reports*")

        # Tier filter
        all_tiers = ['Premium Tier', 'Gold Tier', 'Silver Tier', 'Bronze Tier', 'Low Activity Tier']
        tier_filter = st.sidebar.multiselect(
            "Select Customer Tiers",
            options=all_tiers,
            default=all_tiers
        )

        # Score range filter
        min_score = st.sidebar.number_input(
            "Minimum Overall Score",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.1
        )

        max_score = st.sidebar.number_input(
            "Maximum Overall Score",
            min_value=0.0,
            max_value=10.0,
            value=10.0,
            step=0.1
        )

        # Get filtered data
        filtered_data = assessor.get_filtered_data(
            tier_filter=tier_filter if tier_filter else None,
            min_score=min_score,
            max_score=max_score
        )

        # Display filter summary
        st.sidebar.markdown("---")
        st.sidebar.metric("Total Customers", len(assessor.evaluation_results))
        st.sidebar.metric("Filtered Customers", len(filtered_data))

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Summary Report",
            "🏆 Top Performers",
            "📊 Tier Distribution",
            "📈 Score Distribution"
        ])

        # Tab 1: Summary Report
        with tab1:
            st.header("Summary Report")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Customers", len(filtered_data))

            with col2:
                st.metric("Avg Overall Score", f"{filtered_data['OverallScore'].mean():.2f}")

            with col3:
                st.metric("Total Revenue", f"${filtered_data['TotalRevenue'].sum():,.2f}")

            with col4:
                st.metric("Avg Transactions", f"{filtered_data['TransactionCount'].mean():.1f}")

            st.markdown("---")

            st.subheader("Customer Tier Breakdown")
            tier_counts = filtered_data['CustomerTier'].value_counts().reset_index()
            tier_counts.columns = ['Tier', 'Count']
            tier_counts['Percentage'] = (tier_counts['Count'] / len(filtered_data) * 100).round(1)
            st.dataframe(tier_counts, use_container_width=True, hide_index=True)

            st.markdown("---")

            st.subheader("Customer Details")
            st.dataframe(
                filtered_data[['CustomerID', 'OverallScore', 'CustomerTier',
                               'TotalRevenue', 'TransactionCount', 'DaysSinceLastPurchase']]
                .sort_values('OverallScore', ascending=False)
                .reset_index(drop=True),
                use_container_width=True
            )

        # Tab 2: Top Performers
        with tab2:
            st.header("Top Performing Customers")

            top_n = st.slider("Number of top customers to display", 10, 50, 20)

            top_customers = filtered_data.nlargest(top_n, 'OverallScore')

            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"Top {top_n} Customers")
                st.dataframe(
                    top_customers[['CustomerID', 'OverallScore', 'CustomerTier',
                                   'TotalRevenue', 'TransactionCount']]
                    .reset_index(drop=True),
                    use_container_width=True
                )

            with col2:
                st.subheader("Key Metrics")
                st.metric("Average Score (Top Performers)", f"{top_customers['OverallScore'].mean():.2f}")
                st.metric("Total Revenue (Top Performers)", f"${top_customers['TotalRevenue'].sum():,.2f}")
                st.metric("Avg Transactions (Top Performers)", f"{top_customers['TransactionCount'].mean():.1f}")

                # Tier distribution of top performers
                st.markdown("**Tier Distribution (Top Performers)**")
                top_tier_dist = top_customers['CustomerTier'].value_counts()
                st.bar_chart(top_tier_dist)

        # Tab 3: Tier Distribution
        with tab3:
            st.header("Customer Tier Distribution")

            fig_pie = assessor.visualize_tier_breakdown(chart_size=(10, 6), filtered_data=filtered_data)
            st.pyplot(fig_pie)
            plt.close()

            st.markdown("---")

            # Show tier statistics
            st.subheader("Tier Statistics")
            for tier in all_tiers:
                tier_data = filtered_data[filtered_data['CustomerTier'] == tier]
                if len(tier_data) > 0:
                    with st.expander(f"{tier} ({len(tier_data)} customers)"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Avg Score", f"{tier_data['OverallScore'].mean():.2f}")
                        with col2:
                            st.metric("Avg Revenue", f"${tier_data['TotalRevenue'].mean():,.2f}")
                        with col3:
                            st.metric("Avg Transactions", f"{tier_data['TransactionCount'].mean():.1f}")

        # Tab 4: Score Distribution
        with tab4:
            st.header("Overall Score Distribution")

            bins = st.slider("Number of bins", 10, 50, 30)

            fig_hist = assessor.visualize_score_histogram(chart_size=(12, 6), bar_count=bins,
                                                          filtered_data=filtered_data)
            st.pyplot(fig_hist)
            plt.close()

            st.markdown("---")

            st.subheader("Score Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Mean Score", f"{filtered_data['OverallScore'].mean():.2f}")
            with col2:
                st.metric("Median Score", f"{filtered_data['OverallScore'].median():.2f}")
            with col3:
                st.metric("Std Deviation", f"{filtered_data['OverallScore'].std():.2f}")
            with col4:
                st.metric("Max Score", f"{filtered_data['OverallScore'].max():.2f}")

    else:
        st.info("👆 Please upload a CSV file to begin the analysis")
        st.markdown("""
        ### Expected CSV Format:
        - `CustomerID`: Unique customer identifier
        - `PurchaseDate`: Date of purchase
        - `TransactionAmount`: Amount spent in transaction
        """)


if __name__ == "__main__":
    create_streamlit_app()