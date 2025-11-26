import configparser
import logging
import time
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
table_name = config["constants"]["table_name"]

logging.info(f"Starting optimized COPY for: {csv_path}")

with DBConnection("config.ini") as db:
    cur = db.cur

    # 1. Create Table (UNLOGGED for speed)
    step_start = time.time()
    create_sql = CREATE_TABLE_SQL.replace("CREATE TABLE", "CREATE UNLOGGED TABLE", 1)
    cur.execute(create_sql)
    db.conn.commit()  # Commit table creation to avoid COPY FREEZE issues
    logging.info(f"Table prepared in {time.time() - step_start:.2f}s")

    # 2. Optimize session parameters for bulk load
    step_start = time.time()
    cur.execute("SET maintenance_work_mem = '256MB'")
    cur.execute("SET work_mem = '128MB'")
    cur.execute("SET synchronous_commit = OFF")
    cur.execute("SET commit_delay = 100000")
    cur.execute("SET commit_siblings = 5")
    logging.info(f"Session parameters optimized in {time.time() - step_start:.2f}s")

    # 3. Drop non-primary-key indexes
    step_start = time.time()
    query = f"SELECT indexname FROM pg_indexes WHERE tablename = '{table_name}' AND indexname NOT LIKE '%_pkey'"
    cur.execute(query)
    indexes = cur.fetchall()
    for (idx_name,) in indexes:
        cur.execute(f"DROP INDEX IF EXISTS {idx_name} CASCADE")
        logging.info(f"Dropped index: {idx_name}")
    logging.info(f"Indexes dropped in {time.time() - step_start:.2f}s")

    # 4. Stream Data with COPY (without FREEZE)
    step_start = time.time()
    sql_copy = f"""
        COPY {table_name} 
        FROM STDIN 
        WITH (
            FORMAT CSV, 
            HEADER TRUE, 
            DELIMITER ',',
            ENCODING 'UTF8'
        )
    """
    try:
        with open(csv_path, 'r', encoding='utf-8', buffering=8192 * 16) as f:
            cur.copy_expert(sql_copy, f)
        logging.info(f"Data streamed in {time.time() - step_start:.2f}s")
    except Exception as e:
        logging.error("Import Failed.")
        if "date format" in str(e).lower():
            logging.error("TIP: Date format mismatch. Consider changing 'event_dates' to TEXT in sql_queries.py")
        logging.error(e)
        raise

    # 5. Recreate indexes (if needed)
    step_start = time.time()
    # Example indexes:
    # cur.execute(f"CREATE INDEX idx_athlete ON {table_name}(athlete_id)")
    # cur.execute(f"CREATE INDEX idx_event ON {table_name}(event_name)")
    logging.info(f"Indexes rebuilt in {time.time() - step_start:.2f}s")

    # 6. Analyze table for query optimizer
    cur.execute(f"ANALYZE {table_name}")

logging.info(f"Total Duration: {time.time() - start_time:.2f}s")
