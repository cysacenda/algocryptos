from commons.config import Config
from commons.utils import utils
import logging
import pandas.io.sql as psql
import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine

conf = Config()


# region Subscribers

def calcul_kpi_subscribers_trend():
    logging.warning("calcul_kpi_subscribers_trend - start")

    connection = create_engine(utils.get_connection_string())

    # get data with query
    squery = 'select so.id_cryptocompare, so.reddit_subscribers, so.timestamp from social_stats_reddit_histo so\n'
    squery += 'inner join coins co on (co.id_cryptocompare = so.id_cryptocompare)\n'
    squery += 'where so.timestamp > CURRENT_TIMESTAMP - interval \'90 days\';'

    df = psql.read_sql_query(squery, connection)

    # set index on column timestamp
    df.set_index('timestamp', 'id_cryptocompare', inplace=True)

    # group by crypto
    df2 = df.groupby('id_cryptocompare')

    # resample with period 1D + interpolation for missing values
    df2 = df2.resample('1D').agg({'reddit_subscribers': 'max'}).interpolate()
    df2['reddit_subscribers'] = df2['reddit_subscribers'].astype(int)

    # regroup by crypto
    df3 = df2.groupby('id_cryptocompare')

    # get last value for each crypto
    dftoday = df3.last()

    # today's date
    date_after = datetime.combine(date.today(), datetime.min.time())

    # array of periods on which we want to calculate kpis
    arr = [1, 3, 7, 15, 30, 60, 90]
    for elt in arr:
        date_before = date_after - timedelta(days=elt)

        # manipulate dataframe
        df_tmp = df2.reset_index(level=[0, 1])
        df_tmp.set_index('timestamp', inplace=True)
        df_tmp.sort_index(inplace=True)

        # truncate dataframe to get data on a specific period
        df_tmp = df_tmp.truncate(before=date_before, after=date_after).groupby('id_cryptocompare').first()

        # rename column to avoid problem
        df_tmp.columns = ['col' + str(elt)]
        dftoday = dftoday.join(df_tmp)
        dftoday['col' + str(elt)] = (dftoday['reddit_subscribers'] - dftoday['col' + str(elt)]) / dftoday[
            'col' + str(elt)]

    # rename columns
    dftoday.columns = ['reddit_subscribers', 'subscribers_1d_trend', 'subscribers_3d_trend', 'subscribers_7d_trend',
                       'subscribers_15d_trend', 'subscribers_30d_trend', 'subscribers_60d_trend',
                       'subscribers_90d_trend']
    dftoday = dftoday.drop('reddit_subscribers', 1)

    # empty table
    connection.execute('delete from kpi_reddit_subscribers')

    # insert data into database (last kpis table)
    dftoday.to_sql(name='kpi_reddit_subscribers', con=connection, if_exists='append', index=True)

    # insert data into database (table with historical data)
    connection.execute('insert into kpi_reddit_subscribers_histo select * from kpi_reddit_subscribers')

    logging.warning("calcul_kpi_subscribers_trend - end")

# endregion
