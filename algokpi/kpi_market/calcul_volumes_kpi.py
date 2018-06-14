from commons.config import Config
from commons.utils import utils
import logging
import pandas.io.sql as psql
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta, date
import numpy as np
import matplotlib
matplotlib.use('Agg') # Set matplotlib use in backend mode
import matplotlib.pyplot as plt
from pytz import timezone

conf = Config()
local_images_path = utils.get_path_for_system(conf.get_config('s3_bucket', 'local_generated_images_path_linux'), conf.get_config('s3_bucket', 'local_generated_images_path'))


def calcul_kpi_volumes_trend():
    logging.warning("calcul_kpi_volumes_trend - start")

    # region Retrieve data from database

    connection = create_engine(utils.get_connection_string())

    # get data with query
    squery = 'select co.id_cryptocompare, volume_aggregated as volume_mean_last_30d, timestamp from histo_ohlcv hi\n'
    squery += 'inner join coins co on (co.id_cryptocompare = hi.id_cryptocompare)\n'
    squery += 'where hi.timestamp > CURRENT_TIMESTAMP - interval \'30 days\'\n'
    squery += 'and hi.volume_aggregated is not null\n'
    squery += 'order by hi.timestamp'

    df = psql.read_sql_query(squery, connection)

    # endregion

    # region Manipulate data into panda dataframe

    # set index on column timestamp
    df.set_index('timestamp', inplace=True)

    # 30d mean
    df2 = df.groupby('id_cryptocompare').mean()

    # working with utc because timestamp retrieved into panda DataFrame are in UTC
    date_after = datetime.utcnow()

    # 1h/3h/6h/12h/24h/3d/7d
    arr = [1, 3, 6, 12, 24, 24 * 3, 24 * 7]
    for elt in arr:
        # elt+1 because : dataimporter -O at 15:05 get volumes for 14:00-15:00 period with timestamp = 14:00.
        # algokpi -v at 15:10 => need 13:10 (so minus 2h) to get volumes for pediod
        date_before = date_after - timedelta(hours=elt + 1)  # elt => to be changed with timezone ?
        df_tmp = df.truncate(before=date_before, after=date_after).groupby('id_cryptocompare').mean()

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

'''''    
    Rendu IHM :
    -----------
    -Dans vignette :
        -24h change (vs history 24h avant)
        -courbe globale (générée à la volée)
    -Indicateurs accessibles via clic sur vignette 24h vol dans popup
        vol 1h / 3h / 6h / 12h /  24h / 3d / 7d /// 30d
        vol 1h / 3h / 6h / 12h /  24h / 3d /// 7d
        vol 1h / 3h / 6h / 12h /// 24h
    '''''
def calcul_kpi_volumes_trend_global():
    connection = create_engine(utils.get_connection_string())

    # get data with query
    squery = 'select sum(hi.close_price * hi.volume_aggregated) as global_volume_usd_1h, sum(hi.close_price * pr.available_supply) as global_market_cap_usd, hi.timestamp\n'
    squery += 'from histo_ohlcv hi\n'
    squery += 'inner join coins co on (hi.id_cryptocompare = co.id_cryptocompare)\n'
    squery += 'left outer join prices pr on (pr.id_cryptocompare = hi.id_cryptocompare)\n'
    squery += 'where timestamp > CURRENT_TIMESTAMP - interval \'30 days\''
    squery += 'group by timestamp\n'
    squery += 'order by timestamp'

    df = psql.read_sql_query(squery, connection)

    # mandatory when different timezones in database (column not recognized as datetime). To be careful : format = UTC, no timezone
    df['timestamp'] = pd.to_datetime(df.timestamp, utc=True)

    # set index on column timestamp
    df.set_index('timestamp', inplace=True)

    # delete problematic values (difference of more than 70% of median value)
    df2 = df[
        abs((df.global_market_cap_usd - df.global_market_cap_usd.median()) / df.global_market_cap_usd.median()) < 0.7]
    df2 = df2[
        abs((df2.global_volume_usd_1h - df2.global_volume_usd_1h.median()) / df2.global_volume_usd_1h.median()) < 5]


    # ---------- GENERATE PICTURE 7d ---------------------------------------------------------------------

    # resample for figure on last 7 days
    df_picture = df2.tail(24 * 7).resample('6H').agg(
        {'global_volume_usd_1h': np.sum, 'global_market_cap_usd': np.mean}).interpolate()

    # Figure
    fig = plt.figure()
    df_picture.global_market_cap_usd.plot(legend=False, color='red', linewidth=5).axis('off')
    df_picture.global_volume_usd_1h.plot(secondary_y=True, style='white', linestyle='-', linewidth=2).axis('off')
    fig.set_size_inches(5, 1.2)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(local_images_path + utils.get_slash_for_system() + "global_7d.png", dpi=30, transparent=True)
    plt.close('all')

    # ---------- GENERATE PICTURE 30d ---------------------------------------------------------------------

    # resample for figure on last 30 days
    df_picture2 = df2.resample('12H').agg(
        {'global_volume_usd_1h': np.sum, 'global_market_cap_usd': np.mean}).interpolate()

    # Figure
    fig2 = plt.figure()
    df_picture2.global_market_cap_usd.plot(legend=False, color='red', linewidth=5).axis('off')
    df_picture2.global_volume_usd_1h.plot(secondary_y=True, style='grey', linestyle='-', linewidth=2).axis('off')
    fig2.set_size_inches(5, 1.2)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(local_images_path + utils.get_slash_for_system() + "global_30d.png", dpi=30, transparent=True)
    plt.close('all')


    # ---------- VARIATIONS DATA ---------------------------------------------------------------------

    # resample for data
    df_data = df2.resample('1H').agg({'global_volume_usd_1h': np.sum, 'global_market_cap_usd': np.mean}).interpolate()
    df_data_last_24h = df_data.tail(25)
    df_data_last_24h = df_data_last_24h.drop('global_volume_usd_1h', 1)
    df_data_last_24h.columns = ['global_market_cap_24h_pctchange']
    df_data_pct_change = df_data_last_24h.pct_change(24).tail(1)

    # remove index
    df_data_pct_change = df_data_pct_change.reset_index()

    date = df_data_pct_change.at[(0, 'timestamp')]
    value = df_data_pct_change.at[(0, 'global_market_cap_24h_pctchange')]
    squery = 'insert into kpi_global_data(global_market_cap_24h_pctchange, timestamp)\n'
    squery += 'values(' + str(value) + ', \'' + date.strftime('%Y-%m-%d %H:%M:%S') + '\')'

    # empty table
    connection.execute('delete from kpi_global_data')

    # insert data into database (last kpis table)
    connection.execute(squery)

    # insert data into database (table with historical data)
    connection.execute('insert into kpi_global_data_histo select * from kpi_global_data')


    # ---------- VOLUMES KPIS ---------------------------------------------------------------------

    # delete useless colomns
    df3 = df2.drop('global_market_cap_usd', 1)

    # resample with one hour period
    df_final = df3.resample('1H').agg({'global_volume_usd_1h': np.sum}).interpolate()

    # Prepare dataframe , col1 = 30d mean
    df_final = df_final.mean()
    df_final = df_final.to_frame()
    df_final = df_final.reset_index(drop=True)
    df_final.columns = ['volume_mean_last_30d']

    date_after = datetime.utcnow()

    # 1h/3h/6h/12h/24h/3d/7d
    arr = [1, 3, 6, 12, 24, 24 * 3, 24 * 7]
    for elt in arr:
        # elt+1 because : dataimporter -O at 15:05 get volumes for 14:00-15:00 period with timestamp = 14:00.
        date_before = date_after - timedelta(hours=elt + 1)
        df_tmp = df3.truncate(before=date_before, after=date_after).mean()

        # rename column to avoid problem
        df_tmp = df_tmp.to_frame()
        df_tmp = df_tmp.reset_index(drop=True)
        df_tmp.columns = ['col' + str(elt)]

        # join dataframes
        df_final = df_final.join(df_tmp)
        df_final['col' + str(elt)] = (df_final['col' + str(elt)] - df_final['volume_mean_last_30d']) / df_final[
            'volume_mean_last_30d']

    df_final.columns = ['volume_mean_last_30d', 'volume_mean_last_1h_vs_30d', 'volume_mean_last_3h_30d',
                        'volume_mean_last_6h_30d', 'volume_mean_last_12h_30d', 'volume_mean_last_24h_30d',
                        'volume_mean_last_3d_30d', 'volume_mean_last_7d_30d']
    df_final = df_final.drop('volume_mean_last_30d', 1)
    df_final.dropna(axis=0, thresh=3, inplace=True)

    # empty table
    connection.execute('delete from kpi_global_data_volumes')

    # insert data into database (last kpis table)
    df_final.to_sql(name='kpi_global_data_volumes', con=connection, if_exists='append', index=False)

    # insert data into database (table with historical data)
    connection.execute('insert into kpi_global_data_volumes_histo select * from kpi_global_data_volumes')