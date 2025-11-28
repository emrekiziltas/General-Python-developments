import configparser
import logging
from pathlib import Path
import os


class Config:
    """Manages configuration settings for the analysis."""

    def __init__(self, config_file='config.ini'):
        # Get the directory where this script is located (scripts folder)
        self.script_dir = Path(__file__).parent
        self.config_file = self.script_dir / config_file
        self.project_root = self.script_dir.parent  # Go up one level to project root

        self.settings = self._load_config()
        self._setup_directories()

    def _load_config(self):
        """Load configuration from INI file."""
        config = configparser.ConfigParser()

        try:
            config.read(self.config_file)

            # Get data folder path and convert to absolute path
            data_folder = config['Settings']['folder_path'].strip('"').strip()

            # If it's a relative path, resolve it relative to script directory
            data_folder_path = Path(data_folder)
            if not data_folder_path.is_absolute():
                data_folder_path = (self.script_dir / data_folder_path).resolve()

            # Get data file name (with default)
            data_file = config['Settings'].get('data_file', 'merged_file.csv').strip()

            return {
                'data_folder': str(data_folder_path),
                'data_file': data_file
            }
        except Exception as e:
            logging.warning(f"Could not load config: {e}. Using defaults.")
            # Default: assume data is in ../data/raw relative to script
            default_data_folder = (self.script_dir / '../data/raw').resolve()
            return {
                'data_folder': str(default_data_folder),
                'data_file': 'merged_file.csv'
            }

    def _setup_directories(self):
        """Create output directory structure in project root."""
        # Output directories are relative to project root, not scripts folder
        output_base = self.project_root / 'output'

        self.dirs = {
            'charts': output_base / 'charts',
            'maps': output_base / 'maps',
            'data': output_base / 'data',
            'reports': output_base / 'reports'
        }

        for directory in self.dirs.values():
            directory.mkdir(parents=True, exist_ok=True)

        logging.info(f"Output directories created at: {output_base}")

    def get_data_path(self):
        """Get full path to data file."""
        data_path = Path(self.settings['data_folder']) / self.settings['data_file']
        return str(data_path)

    def get_output_path(self, output_type, filename):
        """
        Get full path for output file.

        Args:
            output_type: 'charts', 'maps', 'data', or 'reports'
            filename: Name of the output file
        """
        return self.dirs[output_type] / filename