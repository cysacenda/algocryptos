import tzlocal
import pytz
from datetime import datetime


# Trick to be on same timezone as Db data (cryptocompare UTC date localized before inserting in DB)
def localize_utc_date(server_time):
    value = server_time / 1000
    local_timezone = tzlocal.get_localzone()
    date_localized = datetime.fromtimestamp(value, local_timezone)
    return date_localized.astimezone(pytz.utc)