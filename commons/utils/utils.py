from commons.config import Config
from datetime import datetime
import tzlocal
import decimal

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