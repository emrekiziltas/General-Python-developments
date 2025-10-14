# constants.py
from typing import Dict

API_ENDPOINTS: Dict[str, str] = {
    "characters": "https://rickandmortyapi.com/api/character",
    "locations": "https://rickandmortyapi.com/api/location",
    "episodes": "https://rickandmortyapi.com/api/episode"
}

SCHEMA = "Apple"
DB_CONFIG = {
    "host": "localhost",
    "database": "PROD_INI",
    "user": "postgres",
    "password": "Password"
}
