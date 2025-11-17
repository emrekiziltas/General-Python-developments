# db_operations.py
import random
from datetime import datetime, timedelta

class DBOperations:
    def __init__(self, cursor, connection):
        self.cur = cursor
        self.conn = connection

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS active_users_week (
                user_id SERIAL PRIMARY KEY,
                last_login TIMESTAMP,
                actions_count INT
            )
        """)
        self.conn.commit()

    def generate_random_user(self):
        last_login = datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        actions_count = random.randint(0, 20)
        return last_login, actions_count

    def insert_random_rows(self, n=10):
        for _ in range(n):
            last_login, actions_count = self.generate_random_user()
            self.cur.execute("""
                INSERT INTO active_users_week (last_login, actions_count)
                VALUES (%s, %s)
            """, (last_login, actions_count))
        self.conn.commit()
