import psycopg2
from config.config import Config

class dbConnection:
    conn = None
    conf = None

    #Connect to database
    def __init__(self):
        self.conf = Config()
        connstring = "dbname='" + self.conf.get_config('db','dbname') + "' user='" + self.conf.get_config('db','dbuser') + "' password='" + self.conf.get_config('db','dbpassword') + "'"
        try:
            self.conn=psycopg2.connect(connstring)
        except:
            print("Error while connecting to database : " + connstring)

    def get_query_result(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
        except:
            print("Error while executing query : " + query)

        rows = cursor.fetchall()
        return rows

    def exexute_query(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            self.conn.commit()
            return 0
        except:
            print("Error while executing query : " + query)
            return -1

