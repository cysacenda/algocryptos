from commons.utils import utils
import logging
import pandas.io.sql as psql
import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
import pytz

# region Subscribers

def calcul_kpi_googletrend():
    logging.warning("calcul_kpi_googletrend - start")

    connection = create_engine(utils.get_connection_string())

    # get data with query
    squery = 'select "id_cryptocompare" as "id_cryptocompare", so."value_standalone", so."timestamp" from social_google_trend so;'

    df = psql.read_sql_query(squery, connection)

    # set index on column timestamp
    df.set_index('timestamp', 'id_cryptocompare', inplace=True)

    # group by crypto
    df2 = df.groupby('id_cryptocompare').last()
    dftoday = df2

    # today's date
    utc = pytz.UTC
    date_after = datetime.combine(date.today(), datetime.min.time())
    date_after = utc.localize(date_after)

    # array of periods on which we want to calculate kpis
    arr = [1, 3, 7, 15, 100]
    for elt in arr:
        date_before = date_after - timedelta(days=elt)
        df_tmp = df
        df_tmp.sort_index(inplace=True)

        # IF elt = 100, take the oldest (no need for truncate)
        if (elt == 100):
            df_tmp = df_tmp.groupby('id_cryptocompare').first()
        else:
            # truncate dataframe to get data on a specific period
            df_tmp = df_tmp.truncate(before=date_before, after=date_after).groupby('id_cryptocompare').first()

        # rename column to avoid problem
        df_tmp.columns = ['col_standalone_' + str(elt)]
        dftoday = dftoday.join(df_tmp)

        dftoday['col_standalone_' + str(elt)] = (dftoday['value_standalone'] - dftoday['col_standalone_' + str(elt)]) / dftoday['col_standalone_' + str(elt)]


    # rename columns
    dftoday.columns = ['value_standalone', 'search_1d_trend', 'search_3d_trend', 'search_7d_trend',
                       'search_15d_trend', 'search_1m_trend']
    dftoday = dftoday.drop('value_standalone', 1)

    # empty table
    connection.execute('delete from kpi_googletrend')

    # insert data into database (last kpis table)
    dftoday.to_sql(name='kpi_googletrend', con=connection, if_exists='append', index=True)

    # insert data into database (table with historical data)
    connection.execute('insert into kpi_googletrend_histo select * from kpi_googletrend')

    logging.warning("calcul_kpi_googletrend - end")

# endregion
