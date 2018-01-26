import psycopg2
from config.config import Config
import logging

class DbConnection:
    conn = None
    conf = None

    def __init__(self):
        self.conf = Config()
        connstring = "host='" + self.conf.get_config('db','dbhost') + "' dbname='" + self.conf.get_config('db','dbname') + "' user='" + self.conf.get_config('db','dbuser') + "' password='" + self.conf.get_config('db','dbpassword') + "'"
        try:
            self.conn=psycopg2.connect(connstring)
        except:
            logging.error("Error while connecting to database : " + connstring)

    def get_query_result(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
        except Exception as e:
            logging.error("Error : " + str(e) + " - " + "Error while executing query : " + query)
            return None

        rows = cursor.fetchall()
        return rows

    def exexute_query(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            self.conn.commit()
            return 0
        except Exception as e:
            logging.error("Error : " + str(e) + " - " + "Error while executing query : " + query)
            return -1