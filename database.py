import sqlite3
import time


class DBHelper:
    dbname: str
    conn: sqlite3.Connection

    def __init__(self, dbname: str):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False,
                                    detect_types=sqlite3.PARSE_DECLTYPES |
                                    sqlite3.PARSE_COLNAMES)

    def setup(self):
        stmt = """CREATE TABLE IF NOT EXISTS ratehistory (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER,
        rates TEXT,
        last_query INTEGER)"""
        self.conn.execute(stmt)
        self.conn.commit()

    def fetch_rates(self, chat_id):
        stmt = """SELECT * FROM ratehistory WHERE chat_id = (?) AND last_query >= (?) ORDER BY last_query"""
        results = [[rates, last_date]
                   for (id, chat_id, rates, last_date)
                   in self.conn.execute(stmt, (chat_id, time.time() - 600))]
        return results

    def insert_rates(self, chat_id, rates, last_query):
        stmt = """INSERT INTO ratehistory (chat_id, rates, last_query) values (?,?,?)"""
        self.conn.execute(stmt, (chat_id, str(rates), last_query))
        self.conn.commit()
