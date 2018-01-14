from config.config import Config
from datetime import datetime
import tzlocal

conf = Config()
DATE_FORMAT = conf.get_config('cryptocompare_params', 'date_format')

# Format a unix timestamp ex : 1515926107 to timestamp format for database PostgreSQL
def format_linux_timestamp_to_db(integer_timestamp):
    unix_timestamp = float(integer_timestamp)
    local_timezone = tzlocal.get_localzone()  # get pytz timezone
    local_time = datetime.fromtimestamp(unix_timestamp, local_timezone)
    return local_time.strftime(DATE_FORMAT)