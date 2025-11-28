import logging
from pathlib import Path
from config import Config
from data_loader import DataLoader
from report_generator import ReportGenerator
from map_generator import MapGenerator


def setup_logging():
    """Configure logging for the entire application."""
    # Get script directory for log file
    script_dir = Path(__file__).parent
    log_file = script_dir.parent / 'crime_analysis.log'  # Save log in project root

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Log file: {log_file}")


def main():
    """Main execution function."""
    logger = logging.getLogger(__name__)

    print("=" * 60)
    print("CAMBRIDGE CRIME DATA ANALYSIS")
    print("=" * 60)
    print()

    # Initialize configuration
    logger.info("Initializing configuration...")
    config = Config()

    # Load data
    logger.info("Loading data...")
    loader = DataLoader(config)

    if not loader.load_data():
        logger.error("Failed to load data. Exiting.")
        return

    if not loader.clean_data():
        logger.error("Failed to clean data. Exiting.")
        return

    df, df_map = loader.get_data()

    # Print summary
    stats = loader.get_summary_stats()
    print(f"\nData Summary:")
    print(f"  Total records: {stats['total_records']:,}")
    print(f"  Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    print(f"  Unique crime types: {stats['unique_crime_types']}")
    print(f"  Unique areas: {stats['unique_areas']}")
    print(f"  Records with coordinates: {stats['records_with_coords']:,}")
    print()

    # Generate reports
    logger.info("Generating statistical reports...")
    report_gen = ReportGenerator(df, df_map, config)
    report_gen.generate_all_reports()
    print("\n✓ Statistical reports and charts generated")

    # Generate maps
    logger.info("Generating interactive maps...")
    map_gen = MapGenerator(df_map, config)
    map_gen.generate_all_maps()
    print("✓ Interactive maps generated")

    # Final summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  Charts:")
    print("    - output/charts/chart1_crime_types.png")
    print("    - output/charts/chart2_monthly_trends.png")
    print("    - output/charts/chart3_areas.png")
    print("    - output/charts/chart4_outcomes.png")
    print("  Maps:")
    print("    - output/maps/map1_crime_heatmap.html")
    print("    - output/maps/map2_crime_markers.html")
    print("    - output/maps/map3_crime_clusters.html")
    print("  Data:")
    print("    - output/data/top_dangerous_locations.csv")
    print("  Reports:")
    print("    - output/reports/summary_statistics.txt")
    print("\n🔥 Open the HTML files in your browser to view interactive maps!")


if __name__ == "__main__":
    setup_logging()
    try:
        main()
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Check crime_analysis.log for details.")