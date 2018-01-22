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

def __calcul_kpi_subscribers_30d_trend():
    squery = 'select * from social_stats_reddit'
    squery += 'where "IdCoinCryptoCompare" = 172091'
    squery += "and timestamp > CURRENT_TIMESTAMP - interval '30 days'"
    squery += 'order by timestamp'

def __calcul_kpi_subscribers_60d_trend():
    toto = 0

def __calcul_kpi_subscribers_90d_trend():
    toto = 0

# endregion