import logging
from config.config import Config
from dbaccess.dbconnection import DbConnection

class ProcessManager:
    dbconn = None
    conf = None

    def __init__(self):
        self.conf = Config()
        self.dbconn=DbConnection()

        #except:
        #    logging.error("Error while connecting to database : " + connstring)

    def start_process(self, idProcess, name):
        blockingprocesses = self.conf.get_config('process_params',str(idProcess))

        # Check if blocking process running
        rows = self.dbconn.get_query_result('Select * from process_params where "IdProcess" IN (' + str(blockingprocesses) + ');')
        if(rows != None and len(rows) > 0):
            logging.error("start_process - blocking processes running")
            return False
        else:
            squeryinsert = 'Insert Into process_params ("IdProcess", "Name", "timestamp")\n'
            squeryinsert += 'VALUES('
            squeryinsert += str(idProcess) + ','
            squeryinsert += "'" + name + "',"
            squeryinsert += 'current_timestamp)'
            self.dbconn.exexute_query(squeryinsert)

        # If not
        return True

    def stop_process(self, idProcess):
        return self.dbconn.exexute_query('Delete from process_params where "IdProcess" = ' + str(idProcess) + ';') == 0