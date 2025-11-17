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
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
        self.cur = self.conn.cursor()
        return self.cur

    def commit(self):
        if self.conn:
            self.conn.commit()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
