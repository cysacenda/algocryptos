# TODO : Split into different files
import numpy as np
import pandas.io.sql as psql
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from commons.utils import utils
from sqlalchemy import create_engine

import pytz
utc=pytz.UTC
from datetime import datetime, timedelta

from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA

from ml.utils_ml import remove_outliers

# import talib # https://github.com/mrjbq7/ta-lib    -    https://mrjbq7.github.io/ta-lib/
from talib.abstract import *

ohlcv_columns_to_be_cleaned = ['close_price', 'open_price', 'low_price', 'high_price', 'volume_aggregated_1h']

str_sql = utils.get_connection_string()


# ======== UTILS ========
def do_timestamp_tasks(df_ts):
    df_ts = df_ts[~df_ts.timestamp.duplicated(keep='first')]
    df_ts['timestamp'] = pd.to_datetime(df_ts.timestamp, utc=True)
    return df_ts.set_index('timestamp')


def join_ohlcv_1h_1d(df_ohlcv_p, df_ohlcv_1d_p):
    # drop columns that are in both dataframes
    df_ohlcv_1d_p = df_ohlcv_1d_p.drop(['open_price', 'high_price', 'low_price', 'close_price', 'volume_aggregated_1h'],
                                       axis=1)

    # Interpolation ok (checked with ploting before / after each indicator)
    df_ohlcv_p = df_ohlcv_p.join(df_ohlcv_1d_p.resample('1H').interpolate())
    return df_ohlcv_p


# ======== RETRIEVE DATA FROM DB ========
def get_dataset_ohlcv(connection, id_cryptocompare):
    squery = "select oh.open_price, oh.high_price, oh.low_price, oh.close_price, oh.volume_aggregated as volume_aggregated_1h, oh.timestamp\n"  # re.reddit_subscribers,
    squery += 'from histo_ohlcv oh\n'
    squery += 'where oh.id_cryptocompare = ' + id_cryptocompare + '\n'
    squery += 'order by oh.timestamp asc\n'
    return psql.read_sql_query(squery, connection)


def get_dataset_reddit(connection, id_cryptocompare):
    squery = "select re.reddit_subscribers, date_trunc('day', re.timestamp) + '00:00:00' as timestamp\n"
    squery += 'from social_stats_reddit_histo re\n'
    squery += 'where re.reddit_subscribers <> 0 and re.id_cryptocompare = ' + id_cryptocompare + '\n'
    squery += 'order by re.timestamp asc\n'
    return psql.read_sql_query(squery, connection)


def get_dataset_all_cryptos(connection):
    squery = 'select sum(hi.close_price * hi.volume_aggregated) as global_volume_usd_1h, sum(hi.close_price * pr.available_supply) as global_market_cap_usd, hi.timestamp\n'
    squery += 'from histo_ohlcv hi\n'
    squery += 'inner join coins co on (hi.id_cryptocompare = co.id_cryptocompare)\n'
    squery += 'left outer join prices pr on (pr.id_cryptocompare = hi.id_cryptocompare)\n'
    squery += 'group by timestamp\n'
    squery += 'order by timestamp'
    return psql.read_sql_query(squery, connection)


def get_dataset_google_trend(connection, id_cryptocompare, period):
    squery = 'select value_standalone, value_compared_to_standard, timestamp\n'
    squery += 'from social_google_trend' + period + '\n'
    squery += 'where id_cryptocompare = ' + id_cryptocompare + '\n'
    squery += 'order by timestamp'
    return psql.read_sql_query(squery, connection)


def get_dataset_ohlcv_old(connection, id_cryptocompare, before_date):
    squery = "select oh.open_price, oh.high_price, oh.low_price, oh.close_price, oh.volume_usd as volume_aggregated_1h, oh.timestamp\n"
    squery += 'from histo_ohlcv_old oh\n'
    squery += 'where oh.id_cryptocompare = ' + id_cryptocompare + '\n'
    squery += "and oh.timestamp < '" + str(before_date) + "'\n"
    squery += 'order by oh.timestamp desc\n'
    squery += 'limit 60\n'
    return psql.read_sql_query(squery, connection)


def get_dataset_ids_top_n_cryptos(connection, top_n):
    squery = 'select id_cryptocompare from prices where crypto_rank between 1 and ' + str(top_n) + '\n'
    return psql.read_sql_query(squery, connection)


# ======== PROCESS / DATA ========
def get_ohlcv_1d_plus_missing_infos(connection, df_ohlcv_p, id_cryptocompare):
    # TODO : Perf : do only one call to these two lines (cf. get_ohlcv_1h_plus_missing_infos)
    df_ohlcv_old = get_dataset_ohlcv_old(connection, id_cryptocompare, df_ohlcv_p.index.min())

    # resample to 1d
    df_ohlcv_1d = df_ohlcv_p.resample("1D").agg({'open_price': 'first', 'high_price': 'max', 'low_price': 'min',
                                                 'close_price': 'last', 'volume_aggregated_1h': 'sum'})

    df_final = df_ohlcv_1d

    # Only when datafarme contains rows
    if len(df_ohlcv_old.index) > 0:
        df_ohlcv_old = clean_dataset_ohlcv_std(df_ohlcv_old, ohlcv_columns_to_be_cleaned, resample='1D')

        # resample to 1d
        df_ohlcv_old = df_ohlcv_old.resample("1D").agg({'open_price': 'first', 'high_price': 'max', 'low_price': 'min',
                                                        'close_price': 'last', 'volume_aggregated_1h': 'sum'})

        # quick & dirty way to have coherents volumes between both dataset
        mean_vol_old = df_ohlcv_old.tail(5).volume_aggregated_1h.mean()
        mean_vol_1d = df_ohlcv_1d.head(5).volume_aggregated_1h.mean()
        df_ohlcv_old.volume_aggregated_1h = df_ohlcv_old.volume_aggregated_1h / (mean_vol_old / mean_vol_1d)
        df_final = pd.concat([df_ohlcv_old, df_ohlcv_1d])

        df_final = df_final[~df_final.index.duplicated()]

    # trick to allow to have data for indicators on last rows
    df_last_row = df_ohlcv_p.tail(1).copy()
    df_last_row.index = [pd.to_datetime(df_final.tail(1).index.values[0] + np.timedelta64(1, 'D'), utc=True)]

    # extrapolate 24h vol from mean of last 6 hours
    df_last_row.volume_aggregated_1h = df_ohlcv_p.tail(6).volume_aggregated_1h.mean() * 4

    df_final = df_final.append(df_last_row)
    return df_final


def get_ohlcv_1h_plus_missing_infos(connection, df_ohlcv_p, id_cryptocompare):
    # get data older than 12/2017
    df_ohlcv_old = get_dataset_ohlcv_old(connection, id_cryptocompare, df_ohlcv_p.index.min())

    df_final = df_ohlcv_p

    # Only when datafarme contains rows
    if len(df_ohlcv_old.index) > 0:
        df_ohlcv_old = clean_dataset_ohlcv_std(df_ohlcv_old, ohlcv_columns_to_be_cleaned, resample='1D')

        # resample to 1h
        df_ohlcv_old = df_ohlcv_old.resample("1H").interpolate()
        df_ohlcv_old.volume_aggregated_1h = df_ohlcv_old.volume_aggregated_1h / 24

        # quick & dirty way to have coherents volumes between both dataset
        mean_vol_old = df_ohlcv_old.tail(5).volume_aggregated_1h.mean()
        mean_vol_ohlcv = df_ohlcv_p.head(5).volume_aggregated_1h.mean()
        df_ohlcv_old.volume_aggregated_1h = df_ohlcv_old.volume_aggregated_1h / (mean_vol_old / mean_vol_ohlcv)
        df_final = pd.concat([df_ohlcv_old, df_ohlcv_p])

    df_final = df_final[~df_final.index.duplicated()]
    return df_final


def merge_google_trend_data(df_google_trend_crypto_1m_p, df_google_trend_crypto_5y_p):
    # put data on the same scale
    first_row_1m = df_google_trend_crypto_1m_p.head(1)
    equiv_row_5y = df_google_trend_crypto_5y_p.loc[first_row_1m.index.values[0]]

    ratio_standalone = first_row_1m.value_standalone[0] / equiv_row_5y.value_standalone
    ratio_compared_to_standard = first_row_1m.value_compared_to_standard[0] / equiv_row_5y.value_compared_to_standard

    df_google_trend_crypto_1m_p.value_standalone = df_google_trend_crypto_1m_p.value_standalone / ratio_standalone
    df_google_trend_crypto_1m_p.value_compared_to_standard = df_google_trend_crypto_1m_p.value_compared_to_standard / ratio_compared_to_standard

    # replace data from 5y with more precise data from 1m
    start_remove = df_google_trend_crypto_1m_p.head(1).index.values[0]
    end_remove = df_google_trend_crypto_1m_p.tail(1).index.values[0]

    df_google_trend_crypto_5y_p = df_google_trend_crypto_5y_p.loc[
        (df_google_trend_crypto_5y_p.index.values < start_remove) | (
                    df_google_trend_crypto_5y_p.index.values > end_remove)]
    df_google_trend_crypto_5y_p = pd.concat([df_google_trend_crypto_5y_p, df_google_trend_crypto_1m_p])

    return df_google_trend_crypto_5y_p


def clean_dataset_google_trend(df_google_trend_p):
    df_google_trend_p = do_timestamp_tasks(df_google_trend_p)
    df_google_trend_p = df_google_trend_p.resample('1H').interpolate()
    df_google_trend_p['value_standalone'] = df_google_trend_p['value_standalone'].astype(int)
    df_google_trend_p['value_compared_to_standard'] = df_google_trend_p['value_compared_to_standard'].astype(int)

    # avoid infinity values (bias not big)
    df_google_trend_p.value_standalone = df_google_trend_p.value_standalone.replace(0, 1)
    df_google_trend_p.value_compared_to_standard = df_google_trend_p.value_compared_to_standard.replace(0, 1)
    return df_google_trend_p


def clean_dataset_ohlcv_spe(df_ohlcv_p):
    # drop rows with missing values (OHLCV)
    df_ohlcv_p = df_ohlcv_p.loc[
        (df_ohlcv_p.open_price != 0.0) & (df_ohlcv_p.high_price != 0.0) & (df_ohlcv_p.low_price != 0.0) & (
                    df_ohlcv_p.close_price != 0.0) & (df_ohlcv_p.volume_aggregated_1h != 0.0)]
    return clean_dataset_ohlcv_std(df_ohlcv_p, ohlcv_columns_to_be_cleaned)


def clean_dataset_ohlcv_std(df_ohlcv_p, columns_name, do_ts_tasks=True, resample='1H'):
    # perform different tasks on df
    if do_ts_tasks:
        df_ohlcv_p = do_timestamp_tasks(df_ohlcv_p)
    df_ohlcv_p = remove_outliers(df_ohlcv_p, columns_name)

    # no scale change (regarding calls done in code)
    df_ohlcv_p = df_ohlcv_p.resample(resample).interpolate()
    return df_ohlcv_p


# ======== FEATURE ENGINEERING ========
def feature_engineering_ohlcv(df_ohlcv_p):
    df_ohlcv_p = df_ohlcv_p.copy()

    # volume_aggregated_24h
    df_ohlcv_p['volume_aggregated_24h'] = df_ohlcv_p.volume_aggregated_1h.rolling(24).sum()

    # close price variance on different scales
    df_ohlcv_p['close_price_variance_3h'] = df_ohlcv_p.close_price.rolling(3).var()
    df_ohlcv_p['close_price_variance_12h'] = df_ohlcv_p.close_price.rolling(12).var()
    df_ohlcv_p['close_price_variance_24h'] = df_ohlcv_p.close_price.rolling(24).var()
    df_ohlcv_p['close_price_variance_7d'] = df_ohlcv_p.close_price.rolling(7 * 24).var()
    df_ohlcv_p['close_price_variance_15d'] = df_ohlcv_p.close_price.rolling(15 * 24).var()
    df_ohlcv_p['close_price_variance_30d'] = df_ohlcv_p.close_price.rolling(30 * 24).var()

    # variance high / low on period
    df_ohlcv_p['last_period_high_low_price_var_pct'] = abs(df_ohlcv_p['low_price'] - df_ohlcv_p['high_price']) / \
                                                       df_ohlcv_p['close_price']

    # volumes kpis 1h, 3h, 6h, 12h, 24h, 3d, 7d, 15d
    df_ohlcv_p['mean_volume_1h_30d'] = df_ohlcv_p.volume_aggregated_1h / df_ohlcv_p.volume_aggregated_1h.rolling(
        30 * 24).mean()
    arr_nums = [3, 6, 12, 24, 3 * 24, 7 * 24, 15 * 24]
    arr_labels = ['3h', '6h', '12h', '24h', '3d', '7d', '15d']
    for i in range(len(arr_nums)):
        df_ohlcv_p['mean_volume_' + arr_labels[i] + '_30d'] = df_ohlcv_p.volume_aggregated_1h.rolling(
            arr_nums[i]).mean() / df_ohlcv_p.volume_aggregated_1h.rolling(30 * 24).mean()

    # change vs n days low / n days high - pct_change for periods : 3d, 7d, 15d, 30d
    arr_nums = np.array([3, 7, 15, 30], dtype=int) * 24
    arr_labels = ['3d', '7d', '15d', '30d']

    # lows
    for i in range(len(arr_nums)):
        df_ohlcv_p['close_price_pct_change_vs_' + arr_labels[i] + '_low'] = (
                                                                                        df_ohlcv_p.close_price - df_ohlcv_p.close_price.rolling(
                                                                                    arr_nums[
                                                                                        i]).min()) / df_ohlcv_p.close_price.rolling(
            arr_nums[i]).min()

        # highs
    for i in range(len(arr_nums)):
        df_ohlcv_p['close_price_pct_change_vs_' + arr_labels[i] + '_high'] = (
                                                                                         df_ohlcv_p.close_price - df_ohlcv_p.close_price.rolling(
                                                                                     arr_nums[
                                                                                         i]).max()) / df_ohlcv_p.close_price.rolling(
            arr_nums[i]).max()
    return df_ohlcv_p


def feature_engineering_ohlcv_all_cryptos(df_ohlcv_all_p):
    # volume_aggregated_24h
    df_ohlcv_all_p['global_volume_usd_24h'] = df_ohlcv_all_p.global_volume_usd_1h.rolling(24).sum()
    return df_ohlcv_all_p


def feature_engineering_reddit(df_reddit_p):
    # pct_change for periods : 1d, 3d, 7d, 15d, 30d
    arr_nums = np.array([1, 3, 7, 15, 30], dtype=int) * 24
    arr_labels = ['1d', '3d', '7d', '15d', '30d']
    for i in range(len(arr_nums)):
        df_reddit_p['reddit_subscribers_pct_change_' + arr_labels[i]] = df_reddit_p.reddit_subscribers.pct_change(
            periods=arr_nums[i])
    return df_reddit_p


def feature_engineering_google_trend(df_google_trend_p, period):
    # period = month
    arr_nums = np.array([1, 3, 7, 15, 30], dtype=int) * 24
    arr_labels = ['1d', '3d', '7d', '15d', '30d']

    # period = year
    if period == 'y':
        # pct_change for periods : 2m, 3m, 6m, 1y
        arr_nums = np.array([2, 3, 6, 12], dtype=int) * 24 * 30
        arr_labels = ['2m', '3m', '6m', '1y']

    for i in range(len(arr_nums)):
        df_google_trend_p[
            'gg_trend_value_standalone_pct_change_' + arr_labels[i]] = df_google_trend_p.value_standalone.pct_change(
            periods=arr_nums[i])
        df_google_trend_p['gg_trend_value_compared_pct_change_' + arr_labels[
            i]] = df_google_trend_p.value_compared_to_standard.pct_change(periods=arr_nums[i])
    return df_google_trend_p


def feature_engineering_technical_analysis(df_ohlcv_p, df_ohlcv_1d_p):
    df_ohlcv_tmp = df_ohlcv_p.copy()
    df_ohlcv_1d = df_ohlcv_1d_p.copy()

    # ========== INDICATORS CALCUL ==========

    # [Overlap Studies] EMA 30 days
    df_ohlcv_1d['Indic_EMA_30d'] = EMA(df_ohlcv_1d, price='close_price', timeperiod=30)
    # [Overlap Studies] EMA 15 days
    df_ohlcv_1d['Indic_EMA_15d'] = EMA(df_ohlcv_1d, price='close_price', timeperiod=15)
    # [Overlap Studies] EMA 7 days
    df_ohlcv_1d['Indic_EMA_7d'] = EMA(df_ohlcv_1d, price='close_price', timeperiod=7)

    # [Overlap Studies] MA 30 days
    df_ohlcv_1d['Indic_MA_30d'] = MA(df_ohlcv_1d, price='close_price', timeperiod=30, matype=0)
    # [Overlap Studies] MA 15 days
    df_ohlcv_1d['Indic_MA_15d'] = MA(df_ohlcv_1d, price='close_price', timeperiod=15, matype=0)
    # [Overlap Studies] MA 7 days
    df_ohlcv_1d['Indic_MA_7d'] = MA(df_ohlcv_1d, price='close_price', timeperiod=7, matype=0)

    # [Overlap Studies] BBands - TODO : 20 days ?
    bands = BBANDS(df_ohlcv_1d, price='close_price', timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    bands.columns = ['Indic_Bbands_20d_upperband', 'Indic_Bbands_20d_middleband', 'Indic_Bbands_20d_lowerband']
    df_ohlcv_1d = df_ohlcv_1d.join(bands)

    # [Momentum Indicator] RSI 14 days
    df_ohlcv_1d['Indic_RSI_14d'] = RSI(df_ohlcv_1d, price='close_price', timeperiod=14)

    # [Momentum Indicators] STOCH
    # ta-lib abstract API KO with dataframe : use workaround
    dataset = {'high': df_ohlcv_1d.high_price.values, 'low': df_ohlcv_1d.low_price.values,
               'close': df_ohlcv_1d.close_price.values}
    kd = STOCH(dataset, fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    df_ohlcv_1d['Indic_Stoch_14_3_3_k'] = kd[0]
    df_ohlcv_1d['Indic_Stoch_14_3_3_d'] = kd[1]

    # [Momentum Indicators] MACD
    macd = MACD(df_ohlcv_1d, price='close_price', fastperiod=12, slowperiod=26, signalperiod=9)
    macd.columns = ['Indic_Macd_12_26_9_macd', 'Indic_Macd_12_26_9_macdsignal', 'Indic_Macd_12_26_9_macdhist']
    df_ohlcv_1d = df_ohlcv_1d.join(macd)

    # [Volume Indicators] OBV
    dataset = {'close': df_ohlcv_1d.close_price.values, 'volume': df_ohlcv_1d.volume_aggregated_1h.values}
    obv = OBV(dataset)
    df_ohlcv_1d['Indic_OBV'] = obv

    # join dataframes on 1h scale
    df_ohlcv_tmp = join_ohlcv_1h_1d(df_ohlcv_tmp, df_ohlcv_1d)

    # ========== ADD FEATURES FOR INTERPRETATION ==========

    # [Interpretation] EMA 30 days in uptrend : True / downtrend : False
    df_ohlcv_tmp['Indic_EMA_30d_uptrend'] = (df_ohlcv_tmp.Indic_EMA_30d.pct_change(periods=1) > 0).astype(int).astype(
        float)
    # [Interpretation] EMA 15 days in uptrend : True / downtrend : False
    df_ohlcv_tmp['Indic_EMA_15d_uptrend'] = (df_ohlcv_tmp.Indic_EMA_15d.pct_change(periods=1) > 0).astype(int).astype(
        float)
    # [Interpretation] EMA 7 days in uptrend : True / downtrend : False
    df_ohlcv_tmp['Indic_EMA_7d_uptrend'] = (df_ohlcv_tmp.Indic_EMA_7d.pct_change(periods=1) > 0).astype(int).astype(
        float)

    # [Interpretation] MA 30 days in uptrend : True / downtrend : False
    df_ohlcv_tmp['Indic_MA_30d_uptrend'] = (df_ohlcv_tmp.Indic_MA_30d.pct_change(periods=1) > 0).astype(int).astype(
        float)
    # [Interpretation] MA 15 days in uptrend : True / downtrend : False
    df_ohlcv_tmp['Indic_MA_15d_uptrend'] = (df_ohlcv_tmp.Indic_MA_15d.pct_change(periods=1) > 0).astype(int).astype(
        float)
    # [Interpretation] MA 7 days in uptrend : True / downtrend : False
    df_ohlcv_tmp['Indic_MA_7d_uptrend'] = (df_ohlcv_tmp.Indic_MA_7d.pct_change(periods=1) > 0).astype(int).astype(float)

    # [Interpretation] BBands close_price - Indic_Bbands_20d_upperband
    df_ohlcv_tmp[
        'Indic_Bbands_20d_diff_close_upperband'] = df_ohlcv_tmp.close_price - df_ohlcv_tmp.Indic_Bbands_20d_upperband
    # [Interpretation] BBands close_price - Indic_Bbands_20d_middleband
    df_ohlcv_tmp[
        'Indic_Bbands_20d_diff_close_upperband'] = df_ohlcv_tmp.close_price - df_ohlcv_tmp.Indic_Bbands_20d_middleband
    # [Interpretation] BBands close_price - Indic_Bbands_20d_middleband
    df_ohlcv_tmp[
        'Indic_Bbands_20d_diff_close_lowerband'] = df_ohlcv_tmp.close_price - df_ohlcv_tmp.Indic_Bbands_20d_lowerband

    # [Interpretation] RSI 14 days in uptrend : True / downtrend : False
    df_ohlcv_tmp['Indic_RSI_14d_uptrend'] = (df_ohlcv_tmp.Indic_RSI_14d.pct_change(periods=1) > 0).astype(int).astype(
        float)
    # [Interpretation] RSI 14 days > value 70
    df_ohlcv_tmp['Indic_RSI_sup_70'] = (df_ohlcv_tmp.Indic_RSI_14d > 70).astype(int).astype(float)
    # [Interpretation] RSI 14 days < value 30
    df_ohlcv_tmp['Indic_RSI_inf_30'] = (df_ohlcv_tmp.Indic_RSI_14d < 30).astype(int).astype(float)

    # [Interpretation] STOCH > value 80
    df_ohlcv_tmp['Indic_Stoch_14_3_3_sup_80'] = (
                (df_ohlcv_tmp.Indic_Stoch_14_3_3_k > 80) & (df_ohlcv_tmp.Indic_Stoch_14_3_3_d > 80)).astype(int).astype(
        float)
    # [Interpretation] STOCH < value 20
    df_ohlcv_tmp['Indic_Stoch_14_3_3_inf_20'] = (
                (df_ohlcv_tmp.Indic_Stoch_14_3_3_k < 20) & (df_ohlcv_tmp.Indic_Stoch_14_3_3_d < 20)).astype(int).astype(
        float)
    # [Interpretation] STOCH diff
    df_ohlcv_tmp['Indic_Stoch_14_3_3_diff'] = df_ohlcv_tmp.Indic_Stoch_14_3_3_k - df_ohlcv_tmp.Indic_Stoch_14_3_3_d

    # [Interpretation] OBV in uptrend on last 3d : True / downtrend : False
    df_ohlcv_tmp['Indic_OBV_uptrend_3d'] = (df_ohlcv_tmp.Indic_OBV.pct_change(periods=3 * 24) > 0).astype(int).astype(
        float)
    # [Interpretation] OBV in uptrend on last 7d : True / downtrend : False
    df_ohlcv_tmp['Indic_OBV_uptrend_7d'] = (df_ohlcv_tmp.Indic_OBV.pct_change(periods=7 * 24) > 0).astype(int).astype(
        float)
    # [Interpretation] OBV in uptrend on last 15d : True / downtrend : False
    df_ohlcv_tmp['Indic_OBV_uptrend_15d'] = (df_ohlcv_tmp.Indic_OBV.pct_change(periods=15 * 24) > 0).astype(int).astype(
        float)
    # [Interpretation] OBV in uptrend on last 30d : True / downtrend : False
    df_ohlcv_tmp['Indic_OBV_uptrend_30d'] = (df_ohlcv_tmp.Indic_OBV.pct_change(periods=30 * 24) > 0).astype(int).astype(
        float)

    return df_ohlcv_tmp.drop(['open_price', 'high_price', 'low_price', 'close_price', 'volume_aggregated_1h'], axis=1)


def get_global_dataset_for_crypto(id_cryptocompare_crypto):
    # ------------------ PRE-PROCESSING : Data retrieving & cleaning ------------------ #

    # TODO : Replace with info from config file
    connection = create_engine(str_sql)

    # Crypto ids
    id_cryptocompare_crypto = str(id_cryptocompare_crypto)
    id_cryptocompare_tether = "171986"
    id_cryptocompare_bitcoin = "1182"

    # --------------------------------
    # OHLCV
    # --------------------------------
    df_ohlcv = get_dataset_ohlcv(connection, id_cryptocompare_crypto)
    df_ohlcv = clean_dataset_ohlcv_spe(df_ohlcv)
    min_date = df_ohlcv.index.min()

    df_ohlcv = get_ohlcv_1h_plus_missing_infos(connection, df_ohlcv, id_cryptocompare_crypto)

    df_ohlcv_tether = get_dataset_ohlcv(connection, id_cryptocompare_tether)
    df_ohlcv_tether = clean_dataset_ohlcv_spe(df_ohlcv_tether)
    df_ohlcv_tether = get_ohlcv_1h_plus_missing_infos(connection, df_ohlcv_tether, id_cryptocompare_tether)

    df_ohlcv_bitcoin = get_dataset_ohlcv(connection, id_cryptocompare_bitcoin)
    df_ohlcv_bitcoin = clean_dataset_ohlcv_spe(df_ohlcv_bitcoin)
    df_ohlcv_bitcoin = get_ohlcv_1h_plus_missing_infos(connection, df_ohlcv_bitcoin, id_cryptocompare_bitcoin)

    df_ohlcv_1d = get_ohlcv_1d_plus_missing_infos(connection, df_ohlcv, id_cryptocompare_crypto)

    # TODO : could be used later if we want TA on bitcoin
    # df_ohlcv_1d_tether = get_ohlcv_1d_plus_missing_infos(connection, df_ohlcv_tether, id_cryptocompare_tether)
    # could be used to do technical analysis also
    # df_ohlcv_1d_bitcoin = get_ohlcv_1d_plus_missing_infos(connection, df_ohlcv_bitcoin, id_cryptocompare_bitcoin)

    # --------------------------------
    # REDDIT SUBSCRIBERS
    # --------------------------------
    df_reddit = get_dataset_reddit(connection, id_cryptocompare_crypto)
    df_reddit = df_reddit[df_reddit.reddit_subscribers.notnull()]
    df_reddit = do_timestamp_tasks(df_reddit)
    df_reddit = df_reddit.resample('1H').interpolate()
    df_reddit['reddit_subscribers'] = df_reddit['reddit_subscribers'].astype(int)

    # --------------------------------
    # ALL CRYPTOS
    # --------------------------------
    df_all_cryptos = get_dataset_all_cryptos(connection)
    df_all_cryptos = clean_dataset_ohlcv_std(df_all_cryptos,
                                             columns_name=['global_volume_usd_1h', 'global_market_cap_usd'])

    # --------------------------------
    # GOOGLE TREND
    # --------------------------------
    # crypto - last month => Need to import and keep old data
    df_google_trend_crypto_1m = get_dataset_google_trend(connection, id_cryptocompare_crypto, '_1m')
    df_google_trend_crypto_1m = clean_dataset_google_trend(df_google_trend_crypto_1m)

    # crypto - 5 years
    df_google_trend_crypto_5y = get_dataset_google_trend(connection, id_cryptocompare_crypto, '')
    df_google_trend_crypto_5y = clean_dataset_google_trend(df_google_trend_crypto_5y)

    # bitcoin - last month
    df_google_trend_bitcoin_1m = get_dataset_google_trend(connection, id_cryptocompare_bitcoin, '_1m')
    df_google_trend_bitcoin_1m = clean_dataset_google_trend(df_google_trend_bitcoin_1m)

    # bitcoin - 5 years
    df_google_trend_bitcoin_5y = get_dataset_google_trend(connection, id_cryptocompare_bitcoin, '')
    df_google_trend_bitcoin_5y = clean_dataset_google_trend(df_google_trend_bitcoin_5y)

    # merge data
    df_google_trend_crypto_5y = merge_google_trend_data(df_google_trend_crypto_1m, df_google_trend_crypto_5y)
    df_google_trend_bitcoin_5y = merge_google_trend_data(df_google_trend_bitcoin_1m, df_google_trend_bitcoin_5y)

    # ------------------ PRE-PROCESSING : Feature engineering ------------------ #
    df_reddit = feature_engineering_reddit(df_reddit)
    df_ohlcv_fe = feature_engineering_ohlcv(df_ohlcv)
    df_ohlcv_tether_fe = feature_engineering_ohlcv(df_ohlcv_tether)
    df_ohlcv_bitcoin_fe = feature_engineering_ohlcv(df_ohlcv_bitcoin)
    df_technical_analysis = feature_engineering_technical_analysis(df_ohlcv, df_ohlcv_1d)
    df_all_cryptos = feature_engineering_ohlcv_all_cryptos(df_all_cryptos)
    df_google_trend_crypto_5y = feature_engineering_google_trend(df_google_trend_crypto_5y, 'y')
    df_google_trend_bitcoin_5y = feature_engineering_google_trend(df_google_trend_bitcoin_5y, 'y')

    # Join dfs
    df_ohlcv_fe = df_ohlcv_fe.join(df_ohlcv_tether_fe, rsuffix='_tether')
    df_ohlcv_fe = df_ohlcv_fe.join(df_ohlcv_bitcoin_fe, rsuffix='_bitcoin')

    df_global = df_ohlcv_fe.join(df_technical_analysis)
    df_global = df_global.join(df_reddit)
    df_global = df_global.join(df_all_cryptos)
    df_global = df_global.join(df_google_trend_crypto_5y, rsuffix='_crypto_5y')
    df_global = df_global.join(df_google_trend_bitcoin_5y, rsuffix='_bitcoin_5y')
    df_global.resample('1H').interpolate()
    df_global.reddit_subscribers = df_global.reddit_subscribers.interpolate(method='linear', limit_area='outside')

    # remove data added only to be able to calcul indicators, etc. => we don't want to take it into account
    df_global = df_global[min_date:df_global.index.max()]

    # remove 24 first hours (some things can't be extrapolated well)
    df_global = df_global.iloc[24:]
    df_global = df_global.interpolate(method='nearest', axis=0).ffill()

    # drop na if exist
    df_final = df_global.dropna(axis='rows')
    diff = df_global.shape[0] - df_final.shape[0]
    if (diff > 0):
        print(str(diff) + ' rows containing Nan dropped')

    # index with id_crypto + date
    df_final['id_cryptocompare'] = id_cryptocompare_crypto
    df_final.reset_index(drop=False, inplace=True)
    df_final.set_index(['timestamp', 'id_cryptocompare'], inplace=True)

    return df_final  # .reset_index(drop=True)


def get_global_datasets_for_cryptos(ids_cryptocompare_crypto):
    dict_df = {}
    for id_crypto in ids_cryptocompare_crypto:
        print('Crypto : ' + str(id_crypto))
        try:
            df = get_global_dataset_for_crypto(id_crypto)
            if df.empty:
                print('ALERT : Empty dataframe')
            else:
                dict_df[str(id_crypto)] = df
        except Exception as e:
            print('ERROR : get_global_dataset_for_crypto() for crypto : ' + str(id_crypto))
            print(str(e))

    return dict_df


def get_global_datasets_for_top_n_cryptos(top_n=20):
    connection_tmp = create_engine(str_sql)
    df = get_dataset_ids_top_n_cryptos(connection_tmp, top_n)
    return get_global_datasets_for_cryptos(df.id_cryptocompare.tolist())


# ------------------ PRE-PROCESSING : Calcul y + split data ------------------ #
def calcul_values_of_y(df, dict_hours_labels, increase_target_pct):
    increase_target_pct = increase_target_pct / 100

    for key in dict_hours_labels:
        label_value = 'y_+' + dict_hours_labels[key] + '_value'
        label_classif = 'y_+' + dict_hours_labels[key] + '_classif'
        # calcul several y searched (value)
        df[label_value] = df.close_price.shift(-key)

        # perform calcul to use binary classification
        if increase_target_pct > 0:
            df[label_classif] = ((df[label_value] - df['close_price']) / df['close_price']) >= increase_target_pct
        else:
            df[label_classif] = ((df[label_value] - df['close_price']) / df['close_price']) <= increase_target_pct

    return df


def do_split_data(df_p, columns_nb_p, min_index, nb_days):
    date_split = min_index + timedelta(days=round(nb_days * 0.75))  # 75 / 25 %
    df_train = df_p[df_p.index.get_level_values(0) <= date_split]
    df_test = df_p[df_p.index.get_level_values(0) > date_split]

    # separe x,y
    X_train = df_train.iloc[:, range(0, columns_nb_p)]
    y_train = df_train.iloc[:, range(columns_nb_p, len(df_p.columns))]

    X_test = df_test.iloc[:, range(0, columns_nb_p)]
    y_test = df_test.iloc[:, range(columns_nb_p, len(df_p.columns))]

    return X_train, X_test, y_train, y_test


def get_preprocessed_data(dict_df, dict_hours_labels, close_price_increase_targeted, predict_only_one_crypto,
                          do_scale=True, do_pca=False, id_cryptocompare=0, useless_features=None):
    if useless_features is None:
        useless_features = []
    columns_nb = 0
    df_new_dict = {}
    df_new_list = []

    min_index = utc.localize(datetime.max)
    max_index = utc.localize(datetime.min)

    columns = None

    # calcul y for each crypto
    for key_id_cryptocompare, df_one_crypto in dict_df.items():

        # delete useless columns if needed
        if len(useless_features) > 0:
            df_one_crypto = df_one_crypto.drop(useless_features, axis=1)

        if columns is None:
            columns = df_one_crypto.columns

        # used to be able to split the dataset between train & test data
        mini = df_one_crypto.index.get_level_values(0).min()
        maxi = df_one_crypto.index.get_level_values(0).max()
        if mini < min_index:
            min_index = mini
        if maxi > max_index:
            max_index = maxi

            # number of columns before adding y values - could be done once only
        columns_nb = len(df_one_crypto.columns)

        # calcul all y values we are interested in and add it to the dataframe
        df_one_crypto = calcul_values_of_y(df_one_crypto.copy(), dict_hours_labels, close_price_increase_targeted)

        # remove rows where y can't be calculed (need more data in the future)
        # TODO : Attention ! Ok pour testing mais pas pour production car on perd la data de la fin !
        df_one_crypto.dropna(subset=list(df_one_crypto.iloc[:, range(columns_nb, len(df_one_crypto.columns))]),
                             inplace=True)

        df_new_dict[key_id_cryptocompare] = df_one_crypto
        df_new_list.append(df_one_crypto)

        # date to split dataset
    nb_days = (max_index - min_index).days

    # concat to get only one dataframe instead of a list of dataframes
    df_global = pd.concat(df_new_list).sort_index()

    # All cryptos
    X_train, X_test, y_train, y_test = do_split_data(df_global, columns_nb, min_index, nb_days)

    # One crypto
    if predict_only_one_crypto:
        # The one to predict
        X_train_one_crypto, X_test_one_crypto, y_train_one_crypto, y_test_one_crypto = do_split_data(
            df_new_dict[id_cryptocompare], columns_nb, min_index, nb_days)
        X_test = X_test_one_crypto
        y_test = y_test_one_crypto

    # ------------------ PRE-PROCESSING ------------------ #

    X_train_close_price = X_train.close_price
    X_test_close_price = X_test.close_price

    # Scaling Data
    if do_scale:
        scaler = MinMaxScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    # PCA to reduce dimensionality
    if do_pca:
        pca = PCA(n_components=35)  # approx 97% variance
        X_train = pca.fit_transform(X_train)
        X_test = pca.transform(X_test)

    # re-index
    X_train = pd.DataFrame(X_train)
    X_train.index = y_train.index
    X_test = pd.DataFrame(X_test)
    X_test.index = y_test.index

    # retrieve columns name (useful for feature importance / feature engineering)
    if not do_pca:
        X_train.columns = columns
        X_test.columns = columns

    return X_train, X_test, y_train, y_test, X_train_close_price, X_test_close_price
