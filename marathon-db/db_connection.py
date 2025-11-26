import psycopg2
import configparser


class DBConnection:
    def __init__(self, config_file="config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)

        db = config["database"]

        self.host = db.get("host")
        self.port = db.getint("port")
        self.dbname = db.get("dbname")
        self.user = db.get("user")
        self.password = db.get("password")

        self.conn = None
        self.cur = None

    def connect(self):
        if not self.conn:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                client_encoding = 'utf8'
            )
            self.cur = self.conn.cursor()
            self.cur.execute("SET client_encoding = 'UTF8';")
        return self.cur


    def commit(self):
        if self.conn:
            self.conn.commit()

    def close(self):
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.close()
