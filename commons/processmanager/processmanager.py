import logging
from commons.config import Config
from commons.dbaccess import DbConnection
import time


class ProcessManager:
    dbconn = None
    conf = None
    RUNNING = None
    WAITING = None
    SUCCESS = None
    ERROR = None
    IsError = None

    def __init__(self):
        self.conf = Config()
        self.dbconn = DbConnection()
        self.RUNNING = self.conf.get_config('process_params', 'status_running')
        self.WAITING = self.conf.get_config('process_params', 'status_waiting')
        self.SUCCESS = self.conf.get_config('process_params', 'status_success')
        self.ERROR = self.conf.get_config('process_params', 'status_error')
        self.IsError = False

    # When starting a process
    def start_process(self, process_id, name, args, retry_count=0):
        # If no args => Error => Kill process
        if args is None or len(args) < 2:
            logging.error("start_process - no args")
            return False

        #if help, ok
        if args[1] == '-h':
            return True

        concatname = name + " " + str(args[1])
        logging.warning("------------------------------")
        logging.warning("START PROCESS - " + concatname)

        self.__delete_old_processes()
        blockingprocesses = self.conf.get_config('process_params', str(process_id))

        # Check if blocking processes are running (SQL perspective, not linux processes - should be equivalent btw)
        rows = self.dbconn.get_query_result('Select * from process_params where (process_id IN (' + str(
            blockingprocesses) + ') and status = ' + "'" + self.RUNNING + "')" + 'OR(process_name = \'' + concatname + "')")
        if rows is not None and len(rows) > 0:
            # Check if process should be placed in Waiting
            if retry_count == 0:
                if self.__should_be_waiting(process_id, concatname):
                    self.__insert_process(process_id, concatname, self.WAITING)
                else:
                    logging.error("start_process - blocking processes running")
                    return False

            # Try n retries before stopping current process
            if retry_count < int(self.conf.get_config('process_params', 'max_nb_retries')):
                time.sleep(int(self.conf.get_config('process_params', 'waiting_time_for_retry')))
                return self.start_process(process_id, name, args, retry_count + 1)
            else:
                logging.error("start_process - blocking processes running")
                self.stop_process(process_id, name, args, self.WAITING)
                return False
        else:
            if retry_count > 0:
                self.__update_process(process_id, concatname)
            else:
                self.__insert_process(process_id, concatname, self.RUNNING)

        # If not
        return True

    # When ending a process
    def stop_process(self, process_id, name, args, status=None):
        concatname = name + " " + str(args[1])
        logging.warning("STOP PROCESS - " + concatname)
        logging.warning("------------------------------")
        if status is None:
            status = self.RUNNING
        # Save process info into historic
        self.__insert_process(process_id, concatname, self.ERROR if self.IsError else self.SUCCESS, True)
        squery = 'Delete from process_params where process_id = ' + str(process_id)
        squery += ' and status = ' + "'" + status + "'" + ' and process_name = ' + "'" + concatname + "'" + ';'
        return self.dbconn.exexute_query(squery) == 0

    # If process there for too long (shouldn't be), delete process from table
    def __delete_old_processes(self):
        max_duration = self.conf.get_config('process_params', 'max_duration_for_process')
        self.dbconn.exexute_query(
            "Delete from process_params where timestamp < CURRENT_TIMESTAMP - interval '" + max_duration + "';")

    # If same process already in status running / waiting => Kill
    def __should_be_waiting(self, process_id, name):
        squeryselect = 'Select * from process_params where process_id = ' + str(process_id) + '\n'
        squeryselect += 'and process_name = ' + "'" + name + "'"
        rows = self.dbconn.get_query_result(squeryselect)
        return rows is None or len(rows) == 0

    def __insert_process(self, process_id, name, status, is_histo=False):
        sql_table = 'process_params'
        if is_histo:
            sql_table = 'process_params_histo'
        squeryinsert = 'INSERT INTO ' + sql_table + ' (process_id, process_name, status, timestamp)\n'
        squeryinsert += 'VALUES('
        squeryinsert += str(process_id) + ','
        squeryinsert += "'" + name + "',"
        squeryinsert += "'" + status + "',"
        squeryinsert += 'current_timestamp)'
        self.dbconn.exexute_query(squeryinsert)

    def __update_process(self, process_id, name):
        squeryupdate = 'UPDATE process_params SET status = ' + "'" + self.RUNNING + "',\n"
        squeryupdate += 'timestamp = current_timestamp\n'
        squeryupdate += 'WHERE process_id = ' + str(process_id) + ' AND process_name = ' + "'" + name + "'"
        self.dbconn.exexute_query(squeryupdate)

    def setIsError(self):
        self.IsError = True