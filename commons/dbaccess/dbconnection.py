import psycopg2
from commons.config import Config
import logging
import socket


class DbConnection:
    conn = None
    conf = None

    def __init__(self):
        self.conf = Config()
        dbhost = self.conf.get_config('db', 'dbhost')
        dbname = self.conf.get_config('db', 'dbname')
        dbuser = self.conf.get_config('db', 'dbuser')
        dbpassword = self.conf.get_config('db', 'dbpassword')
        dbport = str(self.conf.get_config('db', 'dbport'))

        # manage when not on server AWS EC2
        machine_name = socket.gethostname()
        if machine_name in ['CSA-Server-ML']:  # 'DESKTOP-RTOK6M3'
            dbport = self.conf.get_config('db', 'dbport_ext')

        try:
            self.conn = psycopg2.connect(dbhost=dbhost, dbname=dbname, user=dbuser, password=dbpassword, dbport=dbport)
        except Exception as e:
            logging.error("Error : " + str(e) + " - " + "Error while connecting to DB : " + 'postgresql://' + dbuser + ':' + dbpassword + '@' + dbhost + ':' + dbport + '/' + dbname)

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
            raise

    def __del__(self):
        self.conn.close()