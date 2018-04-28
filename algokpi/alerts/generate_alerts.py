from commons.config import Config
from commons.slack import slack
from commons.utils import utils
import logging
import pandas.io.sql as psql
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from commons.dbaccess import DbConnection

def create_slack_alerts():
    logging.warning("create_slack_alerts - start")
    # Get coins and associated subreddits id to be retrieved from APIs
    dbconn = DbConnection()
    query_select = 'select\n'
    query_select += 'replace(replace(replace(replace(alt.description, \'#val1_double#\', CAST(COALESCE(al.val1_double, 0) AS text)), \'#val2_double#\', CAST(COALESCE(al.val2_double, 0) AS text)), \'#crypto_name#\',  pr.crypto_name), \'#crypto_symbol#\', pr.symbol) as description,\n'
    query_select += 'al.timestamp\n'
    query_select += 'from alerts al\n'
    query_select += 'inner join alert_type alt on (al.id_alert_type = alt.id_alert_type)\n'
    query_select += 'left outer join prices pr on (al.id_cryptocompare = pr.id_cryptocompare)\n'
    query_select += 'left outer join prices co on (al.id_cryptocompare = co.id_cryptocompare)\n'
    query_select += 'where timestamp > CURRENT_TIMESTAMP - interval \'10 minutes\'\n'
    rows = dbconn.get_query_result(query_select)

    for row in rows:
        slack.post_message_to_bot_alert(row[0])

    logging.warning("create_slack_alerts - end")

def generate_alert_price_variation():
    logging.warning("generate_alert_price_variation - start")
    connection = create_engine(utils.get_connection_string())

    # get data with query
    squery = 'select hi.id_cryptocompare, hi.close_price, hi.volume_aggregated, hi.timestamp, pr.crypto_name, pr.symbol from histo_ohlcv hi\n'
    squery += 'inner join coins co on (co.id_cryptocompare = hi.id_cryptocompare)\n'
    squery += 'inner join prices pr on (pr.id_cryptocompare = hi.id_cryptocompare)\n'
    squery += 'where (hi.timestamp > CURRENT_TIMESTAMP - interval \'30 days\') and pr.crypto_rank < 100\n'
    squery += 'order by hi.timestamp\n'
    df = psql.read_sql_query(squery, connection)

    # mandatory when different timezones in database (column not recognized as datetime)
    df['timestamp'] = pd.to_datetime(df.timestamp, utc=True)

    # set index on column timestamp
    df.set_index('timestamp', 'id_cryptocompare', inplace = True)

    # dropna
    df2 = df.replace(0, pd.np.nan).dropna(axis=0, thresh=2).fillna(0.0)

    # group by crypto
    df2 = df2.groupby('id_cryptocompare')

    # rescale if values have been droped
    df2 = df2.resample('1H').agg({'close_price': np.mean}).interpolate()
    df3 = df2.groupby('id_cryptocompare')

    # ---------------------------------------------------------------
    # [1/h] Crypto Top 100 : Grosse variation de prix abs > 8% en 1h
    # ---------------------------------------------------------------

    # get last value for each crypto
    dftoday = df3.last()

    # today's date
    date_after = datetime.utcnow()

    # array of periods on which we want to calculate kpis
    arr = [1]
    for elt in arr:
        # +2 because :
        # at 2:05pm we get it for period from 1pm to 2pm and it's written for 1pm (.last())
        # we also want to get the period before that so 12am
        # meaning we need at 2:05pm to get for 11:05 (12:05 is after 12am)
        date_before = date_after - timedelta(hours=elt + 2)

        # manipulate dataframe
        df_tmp = df2.reset_index()
        df_tmp.set_index('timestamp', inplace=True)
        df_tmp.sort_index(inplace=True)

        # truncate dataframe to get data on a specific period
        df_tmp = df_tmp.truncate(before=date_before, after=date_after).groupby('id_cryptocompare').first()

        # rename column to avoid problem
        df_tmp.columns = ['col' + str(elt)]

        dftoday = dftoday.join(df_tmp)
        dftoday['col' + str(elt)] = round(
            ((dftoday['close_price'] - dftoday['col' + str(elt)]) / dftoday['col' + str(elt)]) * 100, 2)

    # rename / drop columns
    dftoday.columns = ['close_price', 'val1_double']
    dftoday = dftoday.drop('close_price', 1)

    # keep values only when condition is met
    dftoday = dftoday[abs(dftoday.val1_double) > 10]

    # add infos
    dftoday['id_alert_type'] = 1

    # insert data into database
    dftoday.to_sql(name='alerts', con=connection, if_exists = 'append', index=True)

    logging.warning("generate_alert_price_variation - end")