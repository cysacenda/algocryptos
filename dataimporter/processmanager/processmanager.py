import logging
from config.config import Config
from dbaccess.dbconnection import DbConnection
import time

class ProcessManager:
    dbconn = None
    conf = None
    RUNNING = None
    WAITING = None

    def __init__(self):
        self.conf = Config()
        self.dbconn=DbConnection()
        self.RUNNING = self.conf.get_config('process_params','status_running')
        self.WAITING = self.conf.get_config('process_params', 'status_waiting')

    # When starting a process
    def start_process(self, idProcess, name, args, retry_count=0):
        # If no args => Error => Kill process
        if(args == None or len(args) < 2):
            logging.error("start_process - blocking processes running")
            return False

        concatname = name + " " + str(args[1])
        self.delete_old_processes()
        blockingprocesses = self.conf.get_config('process_params',str(idProcess))

        # Check if blocking processes are running (SQL perspective, not linux processes)
        rows = self.dbconn.get_query_result('Select * from process_params where "IdProcess" IN (' + str(blockingprocesses) + ') and "Status" = ' + "'" + self.RUNNING + "';")
        if(rows != None and len(rows) > 0):
            # Check if process should be placed in Waiting
            if(retry_count == 0):
                if(self.should_be_waiting(idProcess, concatname)):
                    self.insert_process(idProcess, concatname, self.WAITING)
                else:
                    logging.error("start_process - blocking processes running")
                    return False

            # Try n retries before stopping current process
            if(retry_count < int(self.conf.get_config('process_params','max_nb_retries'))):
                time.sleep(int(self.conf.get_config('process_params','waiting_time_for_retry')))
                return self.start_process(idProcess, name, args, retry_count + 1)
            else:
                logging.error("start_process - blocking processes running")
                return False
        else:
            if(retry_count > 0):
                self.update_process(idProcess, concatname)
            else:
                self.insert_process(idProcess, concatname, self.RUNNING)

        # If not
        return True

    # When ending a process
    def stop_process(self, idProcess):
        return self.dbconn.exexute_query('Delete from process_params where "IdProcess" = ' + str(idProcess) + ' and "Status" = '+ "'" + self.RUNNING + "'" + ';') == 0

    # If process there for too long (shouldn't be), delete process from table
    def delete_old_processes(self):
        max_duration = self.conf.get_config('process_params','max_duration_for_process')
        self.dbconn.exexute_query("Delete from process_params where timestamp < CURRENT_TIMESTAMP - interval '" + max_duration + "';")


    # If same process already in status running / waiting => Kill
    def should_be_waiting(self, idProcess, name):
        squeryselect = 'Select * from process_params where "IdProcess" = ' + str(idProcess) + '\n'
        squeryselect += 'and "Name" = ' + "'" + name + "'"
        rows = self.dbconn.get_query_result(squeryselect)
        return (rows == None or len(rows) == 0)

    def insert_process(self, idProcess, name, status):
        squeryinsert = 'INSERT INTO process_params ("IdProcess", "Name", "Status", "timestamp")\n'
        squeryinsert += 'VALUES('
        squeryinsert += str(idProcess) + ','
        squeryinsert += "'" + name + "',"
        squeryinsert += "'" + status + "',"
        squeryinsert += 'current_timestamp)'
        self.dbconn.exexute_query(squeryinsert)

    def update_process(self, idProcess, name):
        squeryupdate = 'UPDATE process_params SET "Status" = ' + "'" + self.RUNNING + "',\n"
        squeryupdate += '"timestamp" = current_timestamp\n'
        squeryupdate += 'WHERE "IdProcess" = ' + str(idProcess) + ' AND "Name" = ' + "'" + name + "'"
        self.dbconn.exexute_query(squeryupdate)