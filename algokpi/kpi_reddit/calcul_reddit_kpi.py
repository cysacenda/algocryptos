from dbaccess.dbconnection import DbConnection
from config.config import Config
import utils
import logging
from datetime import datetime

conf = Config()

# region Subscribers

# % increase
def calcul_kpi_subscribers_trend():
    toto = 0

def __calcul_kpi_subscribers_1d_trend():
    toto = 0

def calcul_kpi_subscribers_3d_trend():
    toto = 0

def __calcul_kpi_subscribers_7d_trend():
    toto = 0

def __calcul_kpi_subscribers_15d_trend():
    toto = 0

def __calcul_kpi_subscribers_30d_trend(coin_id):
    squery = __create_query_subscribers_30d_trend()

def __create_query_subscribers_30d_trend(coin_id):
    squery = '(select * from social_stats_reddit\n'
    squery += 'where "IdCoinCryptoCompare" = ' + "'" + str(coin_id) + "'\n"
    squery += "and timestamp > CURRENT_TIMESTAMP - interval '30 days'\n"
    squery += 'order by timestamp asc\n'
    squery += 'LIMIT 1)\n'
    squery += 'UNION ALL\n'
    squery += '(select * from social_stats_reddit\n'
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