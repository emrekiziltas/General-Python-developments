import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging


class ReportGenerator:
    """Generates statistical reports and visualizations."""

    def __init__(self, df, df_map, config):
        self.df = df
        self.df_map = df_map
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Set visualization style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)

        # Store pivot tables
        self.pivots = {}

    def analyze_crime_types(self):
        """Analyze crimes by type."""
        self.logger.info("Analyzing crime types...")

        pivot = self.df.groupby('Crime type').size().reset_index(name='Count')
        pivot = pivot.sort_values('Count', ascending=False)
        pivot['Percentage'] = (pivot['Count'] / pivot['Count'].sum() * 100).round(2)

        self.pivots['crime_types'] = pivot

        # Generate chart
        self._create_crime_types_chart(pivot)

        return pivot

    def _create_crime_types_chart(self, pivot):
        """Create bar chart for crime types."""
        plt.figure(figsize=(12, 8))
        top10 = pivot.head(10)

        plt.barh(top10['Crime type'], top10['Count'], color='steelblue')
        plt.xlabel('Number of Crimes')
        plt.title('Top 10 Crime Types in Cambridge (12 Months)',
                  fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()

        for i, v in enumerate(top10['Count']):
            plt.text(v + 50, i, f'{v:,}', va='center')

        plt.tight_layout()
        output_path = self.config.get_output_path('charts', 'chart1_crime_types.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def analyze_monthly_trends(self):
        """Analyze monthly crime trends."""
        self.logger.info("Analyzing monthly trends...")

        # Get top 5 crime types
        top5_crimes = self.pivots['crime_types'].head(5)['Crime type'].tolist()

        # Create pivot table
        pivot = self.df[self.df['Crime type'].isin(top5_crimes)].groupby(
            [self.df['Month'].dt.to_period('M'), 'Crime type']
        ).size().unstack(fill_value=0)

        self.pivots['monthly_trends'] = pivot

        # Generate chart
        self._create_monthly_trends_chart(pivot)

        return pivot

    def _create_monthly_trends_chart(self, pivot):
        """Create line chart for monthly trends."""
        pivot.plot(kind='line', marker='o', linewidth=2, figsize=(14, 7))
        plt.title('Monthly Crime Trends - Top 5 Crime Types',
                  fontsize=14, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Number of Crimes')
        plt.legend(title='Crime Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        output_path = self.config.get_output_path('charts', 'chart2_monthly_trends.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def analyze_geographic_distribution(self):
        """Analyze crimes by geographic area."""
        self.logger.info("Analyzing geographic distribution...")

        pivot = self.df.groupby('LSOA name').size().reset_index(name='Count')
        pivot = pivot.sort_values('Count', ascending=False)
        pivot['Percentage'] = (pivot['Count'] / pivot['Count'].sum() * 100).round(2)

        self.pivots['geographic'] = pivot

        # Generate chart
        self._create_geographic_chart(pivot)

        return pivot

    def _create_geographic_chart(self, pivot):
        """Create bar chart for geographic distribution."""
        plt.figure(figsize=(12, 8))
        top15 = pivot.head(15)

        colors = plt.cm.Reds(top15['Count'] / top15['Count'].max())
        plt.barh(top15['LSOA name'], top15['Count'], color=colors)
        plt.xlabel('Number of Crimes')
        plt.title('Top 15 High-Crime Areas in Cambridge',
                  fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()

        for i, v in enumerate(top15['Count']):
            plt.text(v + 20, i, f'{v:,}', va='center', fontsize=9)

        plt.tight_layout()
        output_path = self.config.get_output_path('charts', 'chart3_areas.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def analyze_outcomes(self):
        """Analyze crime outcomes."""
        self.logger.info("Analyzing crime outcomes...")

        pivot = self.df.groupby('Last outcome category').size().reset_index(name='Count')
        pivot = pivot.sort_values('Count', ascending=False)
        pivot['Percentage'] = (pivot['Count'] / pivot['Count'].sum() * 100).round(2)

        self.pivots['outcomes'] = pivot

        # Generate chart
        self._create_outcomes_chart(pivot)

        return pivot

    def _create_outcomes_chart(self, pivot):
        """Create pie chart for outcomes."""
        plt.figure(figsize=(10, 10))
        colors = plt.cm.Set3(range(len(pivot)))

        plt.pie(pivot['Count'], labels=pivot['Last outcome category'],
                autopct='%1.1f%%', startangle=90, colors=colors)
        plt.title('Distribution of Crime Outcomes',
                  fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()

        output_path = self.config.get_output_path('charts', 'chart4_outcomes.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def generate_all_reports(self):
        """Generate all analysis reports."""
        self.analyze_crime_types()
        self.analyze_monthly_trends()
        self.analyze_geographic_distribution()
        self.analyze_outcomes()

        # Save summary statistics
        self._save_summary_report()

    def _save_summary_report(self):
        """Save summary statistics to file."""
        summary_path = self.config.get_output_path('reports', 'summary_statistics.txt')

        with open(summary_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("CAMBRIDGE CRIME ANALYSIS - SUMMARY REPORT\n")
            f.write("=" * 60 + "\n\n")

            # Overall statistics
            f.write(f"Total crimes analyzed: {len(self.df):,}\n")
            f.write(f"Date range: {self.df['Month'].min()} to {self.df['Month'].max()}\n\n")

            # Crime types
            top_crime = self.pivots['crime_types'].iloc[0]
            f.write(f"Most common crime: {top_crime['Crime type']}\n")
            f.write(f"  Count: {top_crime['Count']:,} ({top_crime['Percentage']:.1f}%)\n\n")

            # Geographic
            top_area = self.pivots['geographic'].iloc[0]
            f.write(f"Highest crime area: {top_area['LSOA name']}\n")
            f.write(f"  Count: {top_area['Count']:,} ({top_area['Percentage']:.1f}%)\n\n")

            safest_area = self.pivots['geographic'].iloc[-1]
            f.write(f"Safest area: {safest_area['LSOA name']}\n")
            f.write(f"  Count: {safest_area['Count']:,} ({safest_area['Percentage']:.1f}%)\n\n")

            # Outcomes
            top_outcome = self.pivots['outcomes'].iloc[0]
            f.write(f"Most common outcome: {top_outcome['Last outcome category']}\n")
            f.write(f"  Count: {top_outcome['Count']:,} ({top_outcome['Percentage']:.1f}%)\n\n")

        self.logger.info(f"Saved: {summary_path}")

    def get_pivots(self):
        """Return all pivot tables."""
        return self.pivots
