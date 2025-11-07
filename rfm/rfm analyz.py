"""
Customer Value Assessment Module
=================================
This module performs customer evaluation based on purchasing behavior metrics.

Author: [Your Name]
Date: November 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Tuple


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

    def compute_overall_score(self) -> pd.DataFrame:
        """
        Calculate overall value scores and rankings for all customers.

        Returns:
            pd.DataFrame: Complete analysis with scores and rankings
        """
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

        # Calculate weighted overall score
        combined_data['OverallScore'] = (
            self.TIME_WEIGHT * combined_data['TimeRanking_Normalized'] +
            self.PURCHASE_COUNT_WEIGHT * combined_data['CountRanking_Normalized'] +
            self.REVENUE_WEIGHT * combined_data['RevenueRanking_Normalized']
        ) * self.FINAL_MULTIPLIER

        # Round for readability
        combined_data = combined_data.round(2)

        self.evaluation_results = combined_data
        return combined_data

    def classify_customers(self) -> pd.DataFrame:
        """
        Classify customers based on their overall scores.

        Returns:
            pd.DataFrame: Data with customer classifications assigned
        """
        if self.evaluation_results is None:
            self.compute_overall_score()

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
            'Inactive Tier'
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

    def visualize_tier_breakdown(self, chart_size: Tuple[int, int] = (12, 8)) -> None:
        """
        Create a pie chart showing the distribution of customer tiers.

        Args:
            chart_size (tuple): Figure size as (width, height)
        """
        if self.evaluation_results is None or 'CustomerTier' not in self.evaluation_results.columns:
            self.classify_customers()

        tier_distribution = self.evaluation_results['CustomerTier'].value_counts()

        figure, axis = plt.subplots(figsize=chart_size)

        # Create pie chart with adjusted parameters
        slices, tier_labels, percentages = axis.pie(
            tier_distribution,
            labels=tier_distribution.index,
            autopct='%1.1f%%',
            startangle=105,  # Rotated 15 degrees (90 + 15)
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

        # Add title with padding
        plt.title('Customer Tier Distribution\n',
                 fontsize=14,
                 fontweight='bold',
                 pad=20)

        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def visualize_score_histogram(self, chart_size: Tuple[int, int] = (12, 6), bar_count: int = 30) -> None:
        """
        Create a histogram showing the distribution of overall scores across all customers.

        Args:
            chart_size (tuple): Figure size as (width, height)
            bar_count (int): Number of bars for the histogram
        """
        if self.evaluation_results is None or 'CustomerTier' not in self.evaluation_results.columns:
            self.classify_customers()

        figure, axis = plt.subplots(figsize=chart_size)

        # Create histogram
        frequencies, bar_edges, rectangles = axis.hist(
            self.evaluation_results['OverallScore'],
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

            # Default color based on tier boundaries
            if bar_midpoint > self.TIER_BOUNDARIES['Premium Tier']:
                rectangle.set_facecolor('#2ecc71')  # Green
            elif bar_midpoint > self.TIER_BOUNDARIES['Gold Tier']:
                rectangle.set_facecolor('#3498db')  # Blue
            elif bar_midpoint > self.TIER_BOUNDARIES['Silver Tier']:
                rectangle.set_facecolor('#f39c12')  # Orange
            elif bar_midpoint > self.TIER_BOUNDARIES['Bronze Tier']:
                rectangle.set_facecolor('#e74c3c')  # Red
            else:
                rectangle.set_facecolor('#95a5a6')  # Gray

            # ✅ Highlight intersection bars (those containing boundary values)
            for boundary in self.TIER_BOUNDARIES.values():
                if bar_left <= boundary < bar_right:
                    rectangle.set_edgecolor('black')
                    rectangle.set_linewidth(2)
                    rectangle.set_hatch('//')  # Optional: add pattern to highlight

            for tier_name, boundary_value in self.TIER_BOUNDARIES.items():
                y_value = np.interp(boundary_value, bar_edges[:-1], frequencies)
                axis.scatter(boundary_value, y_value, color='black', s=80, marker='o', zorder=5)


        # Add statistical information
        average_score = self.evaluation_results['OverallScore'].mean()
        middle_score = self.evaluation_results['OverallScore'].median()

        axis.axvline(average_score, color='purple', linestyle='-', linewidth=2,
                   label=f'Mean: {average_score:.2f}')
        axis.axvline(middle_score, color='pink', linestyle='-', linewidth=2,
                   label=f'Median: {middle_score:.2f}')

        for tier_name, boundary_value in self.TIER_BOUNDARIES.items():
            # Find approximate Y for intersection
            y_value = np.interp(boundary_value, bar_edges[:-1], frequencies)

            # Plot intersection marker
            axis.scatter(boundary_value, y_value, color='black', s=80, marker='o', zorder=5)

            # Add label with offset and rotation
            axis.text(
                boundary_value,
                y_value + max(frequencies) * 0.05,  # vertical offset (5% of height)
                tier_name,
                ha='center',
                va='bottom',
                fontsize=9,
                color='black',
                fontweight='bold',
                rotation=30,  # tilt text slightly
                rotation_mode='anchor',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7)  # background box for readability
            )

        # Formatting
       # axis.set_xlabel('Overall Score', fontsize=12, fontweight='bold')
       # axis.set_ylabel('Number of Customers', fontsize=12, fontweight='bold')
        axis.set_title('Overall Score Distribution\n', fontsize=14, fontweight='bold', pad=15)
        axis.grid(axis='y', alpha=0.3, linestyle='--')
        axis.legend(loc='upper right', fontsize=9)

        # Add text box with statistics
        statistics_summary = f'Total Customers: {len(self.evaluation_results)}\n'
        statistics_summary += f'Mean Score: {average_score:.2f}\n'
        statistics_summary += f'Median Score: {middle_score:.2f}\n'
        statistics_summary += f'Std Dev: {self.evaluation_results["OverallScore"].std():.2f}'

        axis.text(
            0.02, 0.98, statistics_summary,
            transform=axis.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        plt.tight_layout()
        plt.show()

    def produce_summary_report(self) -> None:
        """
        Generate a comprehensive customer value assessment report.
        """
        if self.evaluation_results is None:
            self.classify_customers()

        print("="*60)
        print("CUSTOMER VALUE ASSESSMENT REPORT")
        print("="*60)
        print(f"\nTotal Customers Analyzed: {len(self.evaluation_results)}")
        print("\nCustomer Tier Distribution:")
        print("-"*60)
        print(self.evaluation_results['CustomerTier'].value_counts())
        print("\n" + "="*60)
        print("\nTop 20 Customers by Overall Score:")
        print("-"*60)
        print(self.get_top_performers(20))
        print("\n" + "="*60)


def execute_analysis():
    """
    Main execution function for customer value assessment.
    """
    # Initialize assessor
    assessor = CustomerValueAssessor('dataset.csv')

    # Perform analysis
    assessor.classify_customers()

    # Generate report
    assessor.produce_summary_report()

    # Visualize results
    assessor.visualize_tier_breakdown()
    assessor.visualize_score_histogram()


if __name__ == "__main__":
    execute_analysis()