from commons.dbaccess import DbConnection
from commons.config import Config
import logging
from datetime import datetime

conf = Config()


# region Volumes

# % increase
def calcul_kpi_volumes_trend():
    logging.warning("calcul_kpi_volumes_trend - start")

    dbconn = DbConnection()

    # Get all cryptos for which we have to calculate KPIs
    rows = dbconn.get_query_result('select distinct "IdCoinCryptoCompare" from histo_ohlcv')

    # For each crypto, calculate KPIs
    for row in rows:
        'select * from histo_ohlcv'
        'where "IdCoinCryptoCompare" = 283116'
        'and timestamp < CURRENT_TIMESTAMP - interval \'1 hour\''
        'order by timestamp desc limit 24*30'
    # TODO : Numpy / Panda

        increase_1h = __calcul_kpi_volumes_trend(row[0], 1, 'days')
        increase_3h = __calcul_kpi_volumes_trend(row[0], 3, 'days')
        increase_6h = __calcul_kpi_volumes_trend(row[0], 7, 'days')
        increase_12h = __calcul_kpi_volumes_trend(row[0], 15, 'days')
        increase_24h = __calcul_kpi_volumes_trend(row[0], 30, 'days')
        increase_3d = __calcul_kpi_volumes_trend(row[0], 60, 'days')
        increase_7d = __calcul_kpi_volumes_trend(row[0], 90, 'days')

        if (increase_1h is not None or increase_3h is not None or increase_6h is not None
                or increase_12h is not None or increase_24h is not None
                or increase_3d is not None or increase_7d is not None):
            insertquery = 'INSERT INTO public.kpi_reddit_subscribers_histo ("IdCryptoCompare",'
            if increase_1h is not None:
                insertquery += 'subscribers_1d_trend, '
            if increase_3h is not None:
                insertquery += 'subscribers_3d_trend, '
            if increase_6h is not None:
                insertquery += 'subscribers_7d_trend, '
            if increase_12h is not None:
                insertquery += 'subscribers_15d_trend, '
            if increase_24h is not None:
                insertquery += 'subscribers_30d_trend, '
            if increase_3d is not None:
                insertquery += 'subscribers_60d_trend, '
            if increase_7d is not None:
                insertquery += 'subscribers_90d_trend, '
            insertquery += '"timestamp")\n'
            insertquery += 'VALUES \n('
            insertquery += str(row[0]) + ','
            if increase_1h is not None:
                insertquery += str(increase_1h) + ','
            if increase_3h is not None:
                insertquery += str(increase_3h) + ','
            if increase_6h is not None:
                insertquery += str(increase_6h) + ','
            if increase_12h is not None:
                insertquery += str(increase_12h) + ','
            if increase_24h is not None:
                insertquery += str(increase_24h) + ','
            if increase_3d is not None:
                insertquery += str(increase_3d) + ','
            if increase_7d is not None:
                insertquery += str(increase_7d) + ','

            insertquery += 'current_timestamp)'
            dbconn.exexute_query(insertquery)

    # Empty table containing last KPIs (already saved in histo)
    deletequery = 'delete from kpi_reddit_subscribers'
    dbconn.exexute_query(deletequery)

    # Save in histo
    insertquery2 = 'INSERT INTO public.kpi_reddit_subscribers\n'
    insertquery2 += 'select * from kpi_reddit_subscribers_histo\n'
    insertquery2 += 'where "timestamp" > current_timestamp  - interval ' + "'1 hour'"

    dbconn.exexute_query(insertquery2)

    logging.warning("calcul_kpi_volumes_trend - end")


def __calcul_kpi_volumes_trend(coin_id, days, text):
    period = str(days + 1) + ' ' + text
    squery_select = __create_query_subscribers_trend(coin_id, period)
    dbconn = DbConnection()
    rows = dbconn.get_query_result(squery_select)

    # datetime.now().astimezone() - rows[0][3]
    if len(rows) == 2 and rows[0][1] != 0:
        date_today = rows[1][3]
        date_past = rows[0][3]
        if date_today is not None and date_past is not None and date_today != date_past:
            diff_days_today = (datetime.now().astimezone() - date_today).days
            diff_days_past = (datetime.now().astimezone() - date_past).days
            if diff_days_today == 0 and abs(diff_days_past - days) < 2:
                # increase = (ValueAfter-ValueBefore)/(ValueBefore)
                return (rows[1][1] - rows[0][1]) / (rows[0][1])

    return None


def __create_query_subscribers_trend(coin_id, period):
    # Get today's infos + infos from 30d ago
    squery = '(select "IdCoinCryptoCompare", "Reddit_subscribers", "Reddit_active_users", '
    squery += '"timestamp" from social_stats_reddit\n'
    squery += 'where "IdCoinCryptoCompare" = ' + "'" + str(coin_id) + "'\n"
    squery += "and timestamp > CURRENT_TIMESTAMP - interval '" + period + "'\n"
    squery += 'order by timestamp asc\n'
    squery += 'LIMIT 1)\n'
    squery += 'UNION ALL\n'
    squery += '(select "IdCoinCryptoCompare", "Reddit_subscribers", "Reddit_active_users", '
    squery += '"timestamp" from social_stats_reddit\n'
    squery += 'where "IdCoinCryptoCompare" = ' + "'" + str(coin_id) + "'\n"
    squery += "and timestamp > CURRENT_TIMESTAMP - interval '" + period + "'\n"
    squery += 'order by timestamp desc\n'
    squery += 'LIMIT 1)\n'
    return squery

# endregion
