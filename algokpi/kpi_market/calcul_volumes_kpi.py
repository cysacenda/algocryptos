from commons.config import Config
import logging
import pandas.io.sql as psql
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta

conf = Config()

def calcul_kpi_volumes_trend():
    logging.warning("calcul_kpi_volumes_trend - start")

    # region Retrieve data from database

    # TODO : Replace with info from config file
    connection = create_engine('postgresql://dbuser:algocryptos@localhost:5432/algocryptos')

    # get data with query
    squery = 'select \"IdCoinCryptoCompare\", volume_aggregated as volume_mean_last_30d, timestamp from histo_ohlcv hi\n'
    squery += 'inner join coins co on (co."IdCryptoCompare" = hi."IdCoinCryptoCompare")\n'
    squery += 'where hi.timestamp > CURRENT_TIMESTAMP - interval \'30 days\'\n'
    squery += 'and hi.volume_aggregated is not null\n'
    squery += 'order by hi.timestamp'

    df = psql.read_sql_query(squery, connection)

    # endregion

    # region Manipulate data into panda dataframe

    # set index on column timestamp
    df.set_index('timestamp', inplace=True)

    # 30d mean
    df2 = df.groupby('IdCoinCryptoCompare').mean()

    # working with utc because timestamp retrieved into panda DataFrame are in UTC
    date_after = datetime.utcnow()

    # 1h/3h/6h/12h/24h/3d/7d
    arr = [1, 3, 6, 12, 24, 24 * 3, 24 * 7]
    for elt in arr:
        # elt+1 because : dataimporter -O at 15:05 get volumes for 14:00-15:00 period with timestamp = 14:00.
        # algokpi -v at 15:10 => need 13:10 (so minus 2h) to get volumes for pediod
        date_before = date_after - timedelta(hours=elt + 1)  # elt => to be changed with timezone ?
        df_tmp = df.truncate(before=date_before, after=date_after).groupby('IdCoinCryptoCompare').mean()

        # rename column to avoid conflicts
        df_tmp.columns = ['col' + str(elt)]
        df2 = df2.join(df_tmp)
        df2['col' + str(elt)] = (df2['col' + str(elt)] - df2['volume_mean_last_30d']) / df2['volume_mean_last_30d']

    df2.columns = ['volume_mean_last_30d', 'volume_mean_last_1h_vs_30d', 'volume_mean_last_3h_30d',
                   'volume_mean_last_6h_30d', 'volume_mean_last_12h_30d', 'volume_mean_last_24h_30d',
                   'volume_mean_last_3d_30d', 'volume_mean_last_7d_30d']
    df2 = df2.drop('volume_mean_last_30d', 1)
    df2.dropna(axis=0, thresh=3, inplace=True)

    # endregion

    # region Save data into database

    # empty table
    connection.execute('delete from kpi_market_volumes')

    # insert data into database (last kpis table)
    df2.to_sql(name='kpi_market_volumes', con=connection, if_exists='append', index=True)

    # insert data into database (table with historical data)
    connection.execute('insert into kpi_market_volumes_histo select * from kpi_market_volumes')

    # endregion

    logging.warning("calcul_kpi_volumes_trend - end")

