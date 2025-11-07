"""
RFM (Recency, Frequency, Monetary) Analysis
============================================
This module performs customer segmentation based on RFM metrics.

Author: [Your Name]
Date: November 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Tuple


class RFMAnalyzer:
    """
    A class to perform RFM (Recency, Frequency, Monetary) analysis on customer transaction data.

    Attributes:
        df (pd.DataFrame): The input transaction dataset
        rfm_df (pd.DataFrame): The calculated RFM metrics and scores
    """

    # RFM Score Configuration
    RECENCY_WEIGHT = 0.15
    FREQUENCY_WEIGHT = 0.28
    MONETARY_WEIGHT = 0.57
    SCORE_MULTIPLIER = 0.05

    # Customer Segment Thresholds
    SEGMENT_THRESHOLDS = {
        'Top Customers': 4.5,
        'High Value Customer': 4.0,
        'Medium Value Customer': 3.0,
        'Low Value Customers': 1.6
    }

    def __init__(self, filepath: str):
        """
        Initialize the RFM Analyzer with a dataset.

        Args:
            filepath (str): Path to the CSV file containing transaction data
        """
        self.df = self._load_data(filepath)
        self.rfm_df = None

    def _load_data(self, filepath: str) -> pd.DataFrame:
        """
        Load and preprocess the transaction data.

        Args:
            filepath (str): Path to the CSV file

        Returns:
            pd.DataFrame: Preprocessed transaction data
        """
        df = pd.read_csv(filepath)
        df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'])
        return df

    def calculate_recency(self) -> pd.DataFrame:
        """
        Calculate recency metric for each customer.

        Recency is defined as the number of days since the customer's last purchase.

        Returns:
            pd.DataFrame: DataFrame with CustomerID and Recency columns
        """
        recency_df = self.df.groupby('CustomerID', as_index=False)['PurchaseDate'].max()
        recency_df.columns = ['CustomerID', 'LastPurchaseDate']

        reference_date = recency_df['LastPurchaseDate'].max()
        recency_df['Recency'] = recency_df['LastPurchaseDate'].apply(
            lambda x: (reference_date - x).days
        )

        return recency_df[['CustomerID', 'Recency']]

    def calculate_frequency(self) -> pd.DataFrame:
        """
        Calculate frequency metric for each customer.

        Frequency is defined as the number of unique transactions per customer.

        Returns:
            pd.DataFrame: DataFrame with CustomerID and Frequency columns
        """
        frequency_df = (
            self.df.drop_duplicates()
            .groupby('CustomerID', as_index=False)['PurchaseDate']
            .count()
        )
        frequency_df.columns = ['CustomerID', 'Frequency']

        return frequency_df

    def calculate_monetary(self) -> pd.DataFrame:
        """
        Calculate monetary metric for each customer.

        Monetary value is the total amount spent by each customer.

        Returns:
            pd.DataFrame: DataFrame with CustomerID and Monetary columns
        """
        monetary_df = self.df.groupby('CustomerID', as_index=False)['TransactionAmount'].sum()
        monetary_df.columns = ['CustomerID', 'Monetary']

        return monetary_df

    def calculate_rfm_score(self) -> pd.DataFrame:
        """
        Calculate RFM scores and rankings for all customers.

        Returns:
            pd.DataFrame: Complete RFM analysis with scores and rankings
        """
        # Calculate individual metrics
        recency_df = self.calculate_recency()
        frequency_df = self.calculate_frequency()
        monetary_df = self.calculate_monetary()

        # Merge all metrics
        rfm_df = (
            recency_df
            .merge(frequency_df, on='CustomerID')
            .merge(monetary_df, on='CustomerID')
        )

        # Calculate rankings (lower recency is better, higher frequency/monetary is better)
        rfm_df['R_rank'] = rfm_df['Recency'].rank(ascending=True)
        rfm_df['F_rank'] = rfm_df['Frequency'].rank(ascending=False)
        rfm_df['M_rank'] = rfm_df['Monetary'].rank(ascending=False)

        # Normalize rankings to 0-100 scale
        for col in ['R_rank', 'F_rank', 'M_rank']:
            rfm_df[f'{col}_norm'] = (rfm_df[col] / rfm_df[col].max()) * 100

        # Calculate weighted RFM score
        rfm_df['RFM_Score'] = (
            self.RECENCY_WEIGHT * rfm_df['R_rank_norm'] +
            self.FREQUENCY_WEIGHT * rfm_df['F_rank_norm'] +
            self.MONETARY_WEIGHT * rfm_df['M_rank_norm']
        ) * self.SCORE_MULTIPLIER

        # Round for readability
        rfm_df = rfm_df.round(2)

        self.rfm_df = rfm_df
        return rfm_df

    def segment_customers(self) -> pd.DataFrame:
        """
        Segment customers based on their RFM scores.

        Returns:
            pd.DataFrame: RFM data with customer segments assigned
        """
        if self.rfm_df is None:
            self.calculate_rfm_score()

        conditions = [
            self.rfm_df['RFM_Score'] > self.SEGMENT_THRESHOLDS['Top Customers'],
            self.rfm_df['RFM_Score'] > self.SEGMENT_THRESHOLDS['High Value Customer'],
            self.rfm_df['RFM_Score'] > self.SEGMENT_THRESHOLDS['Medium Value Customer'],
            self.rfm_df['RFM_Score'] > self.SEGMENT_THRESHOLDS['Low Value Customers']
        ]

        segments = [
            'Top Customers',
            'High Value Customer',
            'Medium Value Customer',
            'Low Value Customers',
            'Lost Customers'
        ]

        self.rfm_df['Customer_Segment'] = np.select(conditions, segments[:-1], default=segments[-1])

        return self.rfm_df

    def get_summary(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get a summary of top customers by RFM score.

        Args:
            top_n (int): Number of top customers to display

        Returns:
            pd.DataFrame: Summary of top customers
        """
        if self.rfm_df is None or 'Customer_Segment' not in self.rfm_df.columns:
            self.segment_customers()

        return self.rfm_df[['CustomerID', 'RFM_Score', 'Customer_Segment']].head(top_n)

    def plot_segment_distribution(self, figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        Create a pie chart showing the distribution of customer segments.

        Args:
            figsize (tuple): Figure size as (width, height)
        """
        if self.rfm_df is None or 'Customer_Segment' not in self.rfm_df.columns:
            self.segment_customers()

        segment_counts = self.rfm_df['Customer_Segment'].value_counts()

        fig, ax = plt.subplots(figsize=figsize)

        # Create pie chart with adjusted parameters
        wedges, texts, autotexts = ax.pie(
            segment_counts,
            labels=segment_counts.index,
            autopct='%1.1f%%',
            startangle=105,  # Rotated 15 degrees (90 + 15)
            colors=plt.cm.Set3.colors,
            pctdistance=0.85,
            textprops={'fontsize': 10}
        )

        # Adjust label properties for better readability
        for text in texts:
            text.set_fontsize(11)
            text.set_weight('bold')

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')

        # Add title with padding
        plt.title('Customer Segmentation Distribution\n',
                 fontsize=14,
                 fontweight='bold',
                 pad=20)

        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def generate_report(self) -> None:
        """
        Generate a comprehensive RFM analysis report.
        """
        if self.rfm_df is None:
            self.segment_customers()

        print("="*60)
        print("RFM ANALYSIS REPORT")
        print("="*60)
        print(f"\nTotal Customers Analyzed: {len(self.rfm_df)}")
        print("\nCustomer Segment Distribution:")
        print("-"*60)
        print(self.rfm_df['Customer_Segment'].value_counts())
        print("\n" + "="*60)
        print("\nTop 20 Customers by RFM Score:")
        print("-"*60)
        print(self.get_summary(20))
        print("\n" + "="*60)


def main():
    """
    Main execution function for RFM analysis.
    """
    # Initialize analyzer
    analyzer = RFMAnalyzer('dataset.csv')

    # Perform analysis
    analyzer.segment_customers()

    # Generate report
    analyzer.generate_report()

    # Visualize results
    analyzer.plot_segment_distribution()


if __name__ == "__main__":
    main()