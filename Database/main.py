# main.py
from db_connection import DBConnection
from db_operations import DBOperations

def main():
    # --- Connect to DB ---
    db_conn = DBConnection()
    cursor = db_conn.connect()

    # --- Perform operations ---
    db_ops = DBOperations(cursor, db_conn)
    db_ops.create_table()
    db_ops.insert_random_rows(10)

    # --- Close connection ---
    db_conn.close()
    print("10 random rows inserted successfully!")

if __name__ == "__main__":
    main()
