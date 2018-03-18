from commons.config import Config
from datetime import datetime
import tzlocal
import decimal
import platform

conf = Config()
DATE_FORMAT = conf.get_config('cryptocompare_params', 'date_format')

# create a new context for this task
ctx = decimal.Context()
ctx.prec = 20

# Format a unix timestamp ex : 1515926107 to timestamp format for database PostgreSQL
def format_linux_timestamp_to_db(integer_timestamp):
    return format_linux_timestamp_to_datetime(integer_timestamp).strftime(DATE_FORMAT)

# Format a unix timestamp ex : 1515926107 to datetime
def format_linux_timestamp_to_datetime(integer_timestamp):
    unix_timestamp = float(integer_timestamp)
    local_timezone = tzlocal.get_localzone()  # get pytz timezone
    return datetime.fromtimestamp(unix_timestamp, local_timezone)

# Convert the given float to a string, without resorting to scientific notation
def float_to_str(f):
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')

def get_connection_string():
    dbhost = conf.get_config('db', 'dbhost')
    dbname = conf.get_config('db', 'dbname')
    dbuser = conf.get_config('db', 'dbuser')
    dbpassword = conf.get_config('db', 'dbpassword')
    dbport = conf.get_config('db', 'dbport')
    # 'postgresql://dbuser:algocryptos@localhost:5432/algocryptos'
    return 'postgresql://' + dbuser + ':' + dbpassword + '@' + dbhost + ':' + dbport + '/' + dbname

def get_path_for_system(linux_path, other_path):
    if platform.system() == 'Linux':
        return linux_path
    else:
        return other_path

def get_slash_for_system():
    if platform.system() == 'Linux':
        return '/'
    else:
        return '\\'

def get_path_for_system_spe(os_getcwd, local_path):
    if platform.system() == 'Linux':
        return local_path
    else:
        return os_getcwd + local_path

