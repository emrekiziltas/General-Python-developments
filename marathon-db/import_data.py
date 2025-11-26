import pandas as pd
from psycopg2.extras import execute_batch
import configparser
import logging
import time

from db_connection import DBConnection
from sql_queries import CREATE_TABLE_SQL, INSERT_SQL

# -----------------------------
# Logging setup
# -----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------
# Load config
# -----------------------------
start_time = time.time()
config = configparser.ConfigParser()
config.read("config.ini")
csv_path = config["files"]["csv_path"]
batch_size = config["constants"].getint("batch_size")
logging.info(f"Config loaded in {time.time() - start_time:.2f}s")

# -----------------------------
# 1. LOAD CSV
# -----------------------------
start_csv = time.time()
df = pd.read_csv(csv_path, low_memory=False)
df = df.where(pd.notnull(df), None)
records = list(df.itertuples(index=False, name=None))
logging.info(f"CSV loaded and converted to records ({len(records)} records) in {time.time() - start_csv:.2f}s")

# -----------------------------
# 2. LOAD INTO DATABASE
# -----------------------------
start_db = time.time()
with DBConnection("config.ini") as db:
    cur = db.cur

    step_start = time.time()
    cur.execute("SET CLIENT_ENCODING TO 'UTF8';")
    logging.info(f"Client encoding set in {time.time() - step_start:.2f}s")

    step_start = time.time()
    cur.execute(CREATE_TABLE_SQL)
    logging.info(f"Table creation executed in {time.time() - step_start:.2f}s")

    step_start = time.time()
    execute_batch(cur, INSERT_SQL, records, page_size=batch_size)
    logging.info(f"Inserted {len(records)} records in {time.time() - step_start:.2f}s")

logging.info(f"All database operations completed in {time.time() - start_db:.2f}s")
logging.info(f"Total ETL duration: {time.time() - start_time:.2f}s")
