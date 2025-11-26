import configparser
import logging
import time
import os
from db_connection import DBConnection
from sql_queries import CREATE_TABLE_SQL

# -----------------------------
# Setup
# -----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
start_time = time.time()

config = configparser.ConfigParser()
config.read("config.ini")

csv_path = config["files"]["csv_path"]
table_name = config["constants"]["table_name"]  # "ultra_marathon_results"

# -----------------------------
# EXECUTE
# -----------------------------
logging.info(f"Starting Client-Side COPY stream for: {csv_path}")

with DBConnection("config.ini") as db:
    cur = db.cur

    # 1. Create Table
    step_start = time.time()
    cur.execute(CREATE_TABLE_SQL)
    logging.info(f"Table prepared in {time.time() - step_start:.2f}s")

    # 2. Stream Data (Client-Side COPY)
    step_start = time.time()

    sql_copy = f"""
        COPY {table_name} 
        FROM STDIN 
        WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',')
    """

    try:
        # Python opens the file (bypassing DB permission issues on your .cache folder)
        with open(csv_path, 'r', encoding='utf-8') as f:
            cur.copy_expert(sql_copy, f)

        logging.info(f"Streamed data to DB in {time.time() - step_start:.2f}s")

    except Exception as e:
        logging.error("Import Failed.")
        if "date format" in str(e).lower():
            logging.error(
                "TIP: The CSV date format doesn't match Postgres 'DATE' type. Change 'event_dates' to 'TEXT' in sql_queries.py.")
        logging.error(e)
        raise

logging.info(f"Total Duration: {time.time() - start_time:.2f}s")