# db_helpers.py
import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict
from constants import DB_CONFIG, SCHEMA
import logging
from extractors import parse_pg_array

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def batch_insert(conn, table: str, data: List[Dict], columns: List[str]):
    """Generic batch insert with ON CONFLICT DO UPDATE"""
    if not data:
        logging.warning(f"No data to insert for {table}.")
        return

    placeholders = ", ".join(["%s"] * len(columns))
    update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != "id"])
    query = f"""
        INSERT INTO "{SCHEMA}".{table} ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE SET {update_set};
    """
    values = [[row[col] for col in columns] for row in data]
    with conn.cursor() as cur:
        execute_batch(cur, query, values, page_size=1000)
        conn.commit()
    logging.info(f"Inserted/updated {len(data)} {table} records.")

def insert_characters_with_fk(conn, characters: List[Dict], locations_lookup: Dict[str, int]):
    """Insert characters and map origin/location foreign keys"""
    for char in characters:
        #char["origin_id"] = locations_lookup.get(char.get("origin"))
        char["location_id"] = locations_lookup.get(char.get("location"))
    columns = ["id","name","status","species","gender","location_id","image","created","created_by_ini"]
    batch_insert(conn, "characters", characters, columns)

def insert_relations(conn, table: str, parent_id: int, related_urls, parent_col: str, child_col: str, url_col: str):
    """
    Generic function to insert many-to-many relationships.
    - related_urls: list of URLs or TEXT[] string from Postgres
    - url_col: the column name for storing the URL
    """
    urls = parse_pg_array(related_urls)
    if not urls:
        return

    data = [(parent_id, int(url.rstrip('/').split('/')[-1]), url) for url in urls]

    query = f"""
        INSERT INTO "{SCHEMA}".{table} ({parent_col}, {child_col}, {url_col})
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    """
    with conn.cursor() as cur:
        execute_batch(cur, query, data, page_size=1000)
        conn.commit()
