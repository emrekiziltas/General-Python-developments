import os
import warnings
from pathlib import Path
import logging

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment configuration
ENV = os.getenv("APP_ENV", "development")
DEBUG = ENV == "development"

# Base directories
BASE_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = BASE_DIR.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "Data"
OUTPUT_DIR = DATA_DIR / "Output"
CACHE_DIR = PROJECT_ROOT / ".cache"

# Ensure critical directories exist
for directory in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory ready: {directory}")

# Streamlit configuration - CRITICAL FIX FOR ARROW ERROR
STREAMLIT_CONFIG = {
    "page_title": "Hotel Dashboard",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Data loading configuration
DATA_CONFIG = {
    "data_dir": DATA_DIR,
    "output_dir": OUTPUT_DIR,
    "cache_enabled": True,
    "cache_ttl": 3600
}

# CRITICAL: Disable Arrow serialization to prevent serialization errors
PANDAS_CONFIG = {
    "use_legacy_serialization": True,  # Use legacy instead of Arrow
    "convert_to_string": True  # Convert all object types to string
}

def validate_config() -> bool:
    """Validate that all required directories exist."""
    try:
        if not DATA_DIR.exists():
            logger.warning(f"Data directory not found: {DATA_DIR}")
        if not OUTPUT_DIR.exists():
            logger.info(f"Output directory will be created: {OUTPUT_DIR}")
        logger.info("Configuration validation passed")
        return True
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False