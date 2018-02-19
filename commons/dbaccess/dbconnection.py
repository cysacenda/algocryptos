import psycopg2
from commons.config import Config
import logging


class DbConnection:
    conn = None
    conf = None

    def __init__(self):
        self.conf = Config()
        dbhost = self.conf.get_config('db', 'dbhost')
        dbname = self.conf.get_config('db', 'dbname')
        dbuser = self.conf.get_config('db', 'dbuser')
        dbpassword = self.conf.get_config('db', 'dbpassword')

        connstring = "host='" + dbhost + "' dbname='" + dbname + "' user='" + dbuser \
                     + "' password='" + dbpassword + "'"
        try:
            self.conn = psycopg2.connect(connstring)
        except Exception as e:
            logging.error("Error : " + str(e) + " - " + "Error while connecting to DB : " + connstring)

    def get_query_result(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
        except Exception as e:
            logging.error("Error : " + str(e) + " - " + "Error while executing query : " + query)
            return None

        rows = cursor.fetchall()
        cursor.close()
        return rows

    def exexute_query(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            self.conn.commit()
            cursor.close()
            return 0
        except Exception as e:
            logging.error("Error : " + str(e) + " - " + "Error while executing query : " + query)
            return -1

    def __del__(self):
        self.conn.close()