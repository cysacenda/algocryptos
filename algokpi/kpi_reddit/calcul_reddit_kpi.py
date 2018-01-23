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

    __calcul_kpi_subscribers_30d_trend(172091) #Raiblocks

    logging.warning("calcul_kpi_subscribers_trend - end")

def __calcul_kpi_subscribers_1d_trend():
    toto = 0

def calcul_kpi_subscribers_3d_trend():
    toto = 0

def __calcul_kpi_subscribers_7d_trend():
    toto = 0

def __calcul_kpi_subscribers_15d_trend():
    toto = 0

def __calcul_kpi_subscribers_30d_trend(coin_id):
    squery = __create_query_subscribers_30d_trend(coin_id)
    dbconn = DbConnection()
    rows = dbconn.get_query_result(squery)

    # if(rows.count)
    #if we get information from db
    if(len(rows) == 2):
        #increase = (ValueAfter-ValueBefore)/(ValueBefore)
        increase = (rows[1][1] - rows[0][1]) / (rows[0][1])

def __create_query_subscribers_30d_trend(coin_id):

    # Get today's infos + infos from 30d ago
    squery = '(select "IdCoinCryptoCompare", "Reddit_subscribers", "Reddit_active_users", "timestamp" from social_stats_reddit\n'
    squery += 'where "IdCoinCryptoCompare" = ' + "'" + str(coin_id) + "'\n"
    squery += "and timestamp > CURRENT_TIMESTAMP - interval '30 days'\n"
    squery += 'order by timestamp asc\n'
    squery += 'LIMIT 1)\n'
    squery += 'UNION ALL\n'
    squery += '(select "IdCoinCryptoCompare", "Reddit_subscribers", "Reddit_active_users", "timestamp" from social_stats_reddit\n'
    squery += 'where "IdCoinCryptoCompare" = ' + "'" + str(coin_id) + "'\n"
    squery += "and timestamp > CURRENT_TIMESTAMP - interval '30 days'\n"
    squery += 'order by timestamp desc\n'
    squery += 'LIMIT 1)\n'
    return squery




def __calcul_kpi_subscribers_60d_trend():
    toto = 0

def __calcul_kpi_subscribers_90d_trend():
    toto = 0

# endregion