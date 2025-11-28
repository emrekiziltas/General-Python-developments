import pandas as pd
import logging


class DataLoader:
    """Handles loading and cleaning crime data."""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.df = None
        self.df_map = None

    def load_data(self):
        """
        Load crime data from CSV file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data_path = self.config.get_data_path()
            self.logger.info(f"Loading data from: {data_path}")

            self.df = pd.read_csv(data_path)
            self.logger.info(f"Successfully loaded {len(self.df):,} records")

            return True

        except FileNotFoundError:
            self.logger.error(f"Data file not found: {data_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return False

    def clean_data(self):
        """
        Clean and preprocess the data.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info("Cleaning data...")

            # Convert Month to datetime
            self.df['Month'] = pd.to_datetime(self.df['Month'])

            # Check for missing values
            missing = self.df.isnull().sum()
            if missing.any():
                self.logger.warning(f"Missing values found:\n{missing[missing > 0]}")

            # Create map dataframe with valid coordinates
            self.df_map = self.df.dropna(subset=['Longitude', 'Latitude']).copy()

            self.logger.info(f"Cleaned data: {len(self.df_map):,} records with valid coordinates")
            self.logger.info(f"Date range: {self.df['Month'].min()} to {self.df['Month'].max()}")
            self.logger.info(f"Unique crime types: {self.df['Crime type'].nunique()}")
            self.logger.info(f"Unique LSOA areas: {self.df['LSOA name'].nunique()}")

            return True

        except Exception as e:
            self.logger.error(f"Error cleaning data: {e}")
            return False

    def get_data(self):
        """Return the cleaned dataframes."""
        return self.df, self.df_map

    def get_summary_stats(self):
        """Get summary statistics about the data."""
        if self.df is None:
            return None

        return {
            'total_records': len(self.df),
            'date_range': (self.df['Month'].min(), self.df['Month'].max()),
            'unique_crime_types': self.df['Crime type'].nunique(),
            'unique_areas': self.df['LSOA name'].nunique(),
            'records_with_coords': len(self.df_map)
        }
