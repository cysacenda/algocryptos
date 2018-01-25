from dbaccess.dbconnection import DbConnection
from config.config import Config
import utils
import logging
from datetime import datetime

conf = Config()

# region Subscribers

# % increase
def calcul_kpi_subscribers_trend():
    logging.warning("calcul_kpi_subscribers_trend - start")

    dbconn = DbConnection()
    rows = dbconn.get_query_result('select distinct "IdCoinCryptoCompare" from social_stats_reddit')
    for row in rows:
        increase_1d = __calcul_kpi_subscribers_trend(row[0], 1, 'day')
        increase_3d = __calcul_kpi_subscribers_trend(row[0], 3, 'days')
        increase_7d = __calcul_kpi_subscribers_trend(row[0], 7, 'days')
        increase_15d = __calcul_kpi_subscribers_trend(row[0], 15, 'days')
        increase_30d = __calcul_kpi_subscribers_trend(row[0], 30, 'days')
        increase_60d = __calcul_kpi_subscribers_trend(row[0], 60, 'days')
        increase_90d = __calcul_kpi_subscribers_trend(row[0], 90, 'days')

        if(increase_1d != None or increase_3d != None or increase_7d != None or increase_15d != None or increase_30d != None or increase_60d != None or increase_90d != None):
            insertquery = 'INSERT INTO public.kpi_reddit_subscribers ("IdCryptoCompare",'
            if(increase_1d != None):
                insertquery += 'subscribers_1d_trend, '
            if (increase_3d != None):
                insertquery += 'subscribers_3d_trend, '
            if (increase_7d != None):
                insertquery += 'subscribers_7d_trend, '
            if (increase_15d != None):
                insertquery += 'subscribers_15d_trend, '
            if (increase_30d != None):
                insertquery += 'subscribers_30d_trend, '
            if (increase_60d != None):
                insertquery += 'subscribers_60d_trend, '
            if (increase_90d != None):
                insertquery += 'subscribers_90d_trend, '
            insertquery += '"timestamp")\n'
            insertquery += 'VALUES \n('
            insertquery += str(row[0]) + ','
            if (increase_1d != None):
                insertquery += str(increase_1d) + ','
            if (increase_3d != None):
                insertquery += str(increase_3d) + ','
            if (increase_7d != None):
                insertquery += str(increase_7d) + ','
            if (increase_15d != None):
                insertquery += str(increase_15d) + ','
            if (increase_30d != None):
                insertquery += str(increase_30d) + ','
            if (increase_60d != None):
                insertquery += str(increase_60d) + ','
            if (increase_90d != None):
                insertquery += str(increase_90d) + ','

            insertquery += 'current_timestamp)'
            dbconn.exexute_query(insertquery)

    logging.warning("calcul_kpi_subscribers_trend - end")

def __calcul_kpi_subscribers_trend(coin_id, days, text):
    period = str(days) + ' ' + text
    squery_select = __create_query_subscribers_trend(coin_id, period)
    dbconn = DbConnection()
    rows = dbconn.get_query_result(squery_select)

    # datetime.now().astimezone() - rows[0][3]
    if (len(rows) == 2 and rows[0][1] != 0):
        dateOlder = rows[1][3]
        dateYounger = rows[0][3]
        if(dateOlder != None and dateYounger != None and dateOlder != dateYounger):
            diffDaysOlder = (datetime.now().astimezone() - dateOlder).days
            diffDaysYounger = (datetime.now().astimezone() - dateYounger).days
            if(diffDaysOlder == 0 and abs(diffDaysYounger - days) < 2):
                # increase = (ValueAfter-ValueBefore)/(ValueBefore)
                return (rows[1][1] - rows[0][1]) / (rows[0][1])

    return None


def __create_query_subscribers_trend(coin_id, period):

    # Get today's infos + infos from 30d ago
    squery = '(select "IdCoinCryptoCompare", "Reddit_subscribers", "Reddit_active_users", "timestamp" from social_stats_reddit\n'
    squery += 'where "IdCoinCryptoCompare" = ' + "'" + str(coin_id) + "'\n"
    squery += "and timestamp > CURRENT_TIMESTAMP - interval '" + period + "'\n"
    squery += 'order by timestamp asc\n'
    squery += 'LIMIT 1)\n'
    squery += 'UNION ALL\n'
    squery += '(select "IdCoinCryptoCompare", "Reddit_subscribers", "Reddit_active_users", "timestamp" from social_stats_reddit\n'
    squery += 'where "IdCoinCryptoCompare" = ' + "'" + str(coin_id) + "'\n"
    squery += "and timestamp > CURRENT_TIMESTAMP - interval '" + period + "'\n"
    squery += 'order by timestamp desc\n'
    squery += 'LIMIT 1)\n'
    return squery

# endregion