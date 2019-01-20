import numpy as np

# import talib # https://github.com/mrjbq7/ta-lib    -    https://mrjbq7.github.io/ta-lib/
from talib.abstract import *


class PreprocFeatureEngineering:

    @staticmethod
    def join_ohlcv_1h_1d(df_ohlcv_p, df_ohlcv_1d_p):
        # drop columns that are in both dataframes
        df_ohlcv_1d_p = df_ohlcv_1d_p.drop(
            ['open_price', 'high_price', 'low_price', 'close_price', 'volume_aggregated_1h'],
            axis=1)

        # Interpolation ok (checked with ploting before / after each indicator)
        # TODO : Check if interpolation ok
        return df_ohlcv_p.join(df_ohlcv_1d_p.resample('1H')
                               #.agg({'close_price': np.mean, 'volume_aggregated': np.sum})
                               .interpolate())

    # ======== FEATURE ENGINEERING ========
    @staticmethod
    def feature_engineering_ohlcv(df_ohlcv_p):
        df_ohlcv = df_ohlcv_p.copy()

        # volume_aggregated_24h
        df_ohlcv['volume_aggregated_24h'] = df_ohlcv.volume_aggregated_1h.rolling(24).sum()

        # close price variance on different scales
        df_ohlcv['close_price_variance_3h'] = df_ohlcv.close_price.rolling(3).var()
        df_ohlcv['close_price_variance_12h'] = df_ohlcv.close_price.rolling(12).var()
        df_ohlcv['close_price_variance_24h'] = df_ohlcv.close_price.rolling(24).var()
        df_ohlcv['close_price_variance_7d'] = df_ohlcv.close_price.rolling(7 * 24).var()
        df_ohlcv['close_price_variance_15d'] = df_ohlcv.close_price.rolling(15 * 24).var()
        df_ohlcv['close_price_variance_30d'] = df_ohlcv.close_price.rolling(30 * 24).var()

        # variance high / low on period
        df_ohlcv['last_period_high_low_price_var_pct'] = abs(df_ohlcv['low_price'] - df_ohlcv['high_price']) / \
                                                         df_ohlcv['close_price']

        # volumes kpis 1h, 3h, 6h, 12h, 24h, 3d, 7d, 15d
        df_ohlcv['mean_volume_1h_30d'] = df_ohlcv.volume_aggregated_1h / df_ohlcv.volume_aggregated_1h.rolling(
            30 * 24).mean()
        arr_nums = [3, 6, 12, 24, 3 * 24, 7 * 24, 15 * 24]
        arr_labels = ['3h', '6h', '12h', '24h', '3d', '7d', '15d']
        for i in range(len(arr_nums)):
            df_ohlcv['mean_volume_' + arr_labels[i] + '_30d'] = df_ohlcv.volume_aggregated_1h.rolling(
                arr_nums[i]).mean() / df_ohlcv.volume_aggregated_1h.rolling(30 * 24).mean()

        # change vs n days low / n days high - pct_change for periods : 3d, 7d, 15d, 30d
        arr_nums = np.array([3, 7, 15, 30], dtype=int) * 24
        arr_labels = ['3d', '7d', '15d', '30d']

        # lows
        for i in range(len(arr_nums)):
            df_ohlcv['close_price_pct_change_vs_' + arr_labels[i] + '_low'] = \
                (df_ohlcv.close_price - df_ohlcv.close_price.rolling(arr_nums[i]).min()) \
                / df_ohlcv.close_price.rolling(arr_nums[i]).min()

        # highs
        for i in range(len(arr_nums)):
            df_ohlcv['close_price_pct_change_vs_' + arr_labels[i] + '_high'] \
                = (df_ohlcv.close_price - df_ohlcv.close_price.rolling(arr_nums[i]).max()) \
                  / df_ohlcv.close_price.rolling(
                arr_nums[i]).max()

        # price trends
        arr_nums = [3, 6, 12, 24, 3 * 24, 7 * 24, 15 * 24, 30 * 24]
        arr_labels = ['3h', '6h', '12h', '24h', '3d', '7d', '15d', '30d']
        for i in range(len(arr_nums)):
            df_ohlcv['trend_pct_' + arr_labels[i]] = df_ohlcv['close_price'].pct_change(periods=arr_nums[i])

        return df_ohlcv

    @staticmethod
    def feature_engineering_ohlcv_all_cryptos(df_ohlcv_all_p):
        # volume_aggregated_24h
        df_ohlcv_all_p['global_volume_usd_24h'] = df_ohlcv_all_p.global_volume_usd_1h.rolling(24).sum()
        return df_ohlcv_all_p

    @staticmethod
    def feature_engineering_reddit(df_reddit_p):
        # pct_change for periods : 1d, 3d, 7d, 15d, 30d
        arr_nums = np.array([1, 3, 7, 15, 30], dtype=int) * 24
        arr_labels = ['1d', '3d', '7d', '15d', '30d']
        for i in range(len(arr_nums)):
            df_reddit_p['reddit_subscribers_pct_change_' + arr_labels[i]] = df_reddit_p.reddit_subscribers.pct_change(
                periods=arr_nums[i])
        return df_reddit_p

    @staticmethod
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
                'gg_trend_value_standalone_pct_change_' + arr_labels[
                    i]] = df_google_trend_p.value_standalone.pct_change(
                periods=arr_nums[i])
            df_google_trend_p['gg_trend_value_compared_pct_change_' + arr_labels[
                i]] = df_google_trend_p.value_compared_to_standard.pct_change(periods=arr_nums[i])
        return df_google_trend_p

    @staticmethod
    def feature_engineering_technical_analysis(df_ohlcv_p):
        df_ohlcv_tmp = df_ohlcv_p.copy()

        # ========== INDICATORS CALCUL ==========

        # [Overlap Studies] EMA 30 days
        df_ohlcv_p['Indic_EMA_30d'] = EMA(df_ohlcv_p, price='close_price', timeperiod=30 * 24)
        # [Overlap Studies] EMA 15 days
        df_ohlcv_p['Indic_EMA_15d'] = EMA(df_ohlcv_p, price='close_price', timeperiod=15 * 24)
        # [Overlap Studies] EMA 7 days
        df_ohlcv_p['Indic_EMA_7d'] = EMA(df_ohlcv_p, price='close_price', timeperiod=7 * 24)

        # [Overlap Studies] MA 30 days
        df_ohlcv_p['Indic_MA_30d'] = MA(df_ohlcv_p, price='close_price', timeperiod=30 * 24, matype=0)
        # [Overlap Studies] MA 15 days
        df_ohlcv_p['Indic_MA_15d'] = MA(df_ohlcv_p, price='close_price', timeperiod=15 * 24, matype=0)
        # [Overlap Studies] MA 7 days
        df_ohlcv_p['Indic_MA_7d'] = MA(df_ohlcv_p, price='close_price', timeperiod=7 * 24, matype=0)

        # [Overlap Studies] BBands
        bands = BBANDS(df_ohlcv_p, price='close_price', timeperiod=20 * 24, nbdevup=2, nbdevdn=2, matype=0)
        bands.columns = ['Indic_Bbands_20d_upperband', 'Indic_Bbands_20d_middleband', 'Indic_Bbands_20d_lowerband']
        df_ohlcv_p = df_ohlcv_p.join(bands)

        # [Momentum Indicator] RSI 14 days
        df_ohlcv_p['Indic_RSI_14d'] = RSI(df_ohlcv_p, price='close_price', timeperiod=14 * 24)

        # [Momentum Indicators] STOCH
        # ta-lib abstract API KO with dataframe : use workaround
        dataset = {'high': df_ohlcv_p.high_price.values, 'low': df_ohlcv_p.low_price.values,
                   'close': df_ohlcv_p.close_price.values}
        kd = STOCH(dataset, fastk_period=14 * 24, slowk_period=3 * 24, slowk_matype=0, slowd_period=3 * 24, slowd_matype=0)
        df_ohlcv_p['Indic_Stoch_14_3_3_k'] = kd[0]
        df_ohlcv_p['Indic_Stoch_14_3_3_d'] = kd[1]

        # [Momentum Indicators] MACD
        macd = MACD(df_ohlcv_p, price='close_price', fastperiod=12 * 24, slowperiod=26 * 24, signalperiod=9 * 24)
        macd.columns = ['Indic_Macd_12_26_9_macd', 'Indic_Macd_12_26_9_macdsignal', 'Indic_Macd_12_26_9_macdhist']
        df_ohlcv_p = df_ohlcv_p.join(macd)

        # [Volume Indicators] OBV
        dataset = {'close': df_ohlcv_p.close_price.values, 'volume': df_ohlcv_p.volume_aggregated_1h.values}
        obv = OBV(dataset)
        df_ohlcv_p['Indic_OBV'] = obv

        # join dataframes on 1h scale
        # df_ohlcv_tmp = PreprocFeatureEngineering.join_ohlcv_1h_1d(df_ohlcv_tmp, df_ohlcv_1d)
        df_ohlcv_tmp = df_ohlcv_p

        # ========== ADD FEATURES FOR INTERPRETATION ==========

        # [Interpretation] EMA 30 days pct change on last nb_periods=12h
        # TODO : Feature engineering => tests different nb_periods
        nb_periods = 12
        df_ohlcv_tmp['Indic_EMA_30d_uptrend'] = (df_ohlcv_tmp.Indic_EMA_30d.pct_change(periods=nb_periods)).astype(
            float)
        # [Interpretation] EMA 15 days pct change on last nb_periods=12h
        df_ohlcv_tmp['Indic_EMA_15d_uptrend'] = (df_ohlcv_tmp.Indic_EMA_15d.pct_change(periods=nb_periods)).astype(
            float)
        # [Interpretation] EMA 7 days pct change on last nb_periods=12h
        df_ohlcv_tmp['Indic_EMA_7d_uptrend'] = (df_ohlcv_tmp.Indic_EMA_7d.pct_change(periods=nb_periods)).astype(
            float)

        # [Interpretation] MA 30 days pct change on last nb_periods=12h
        df_ohlcv_tmp['Indic_MA_30d_uptrend'] = (df_ohlcv_tmp.Indic_MA_30d.pct_change(periods=nb_periods)).astype(
            float)
        # [Interpretation] MA 15 days pct change on last nb_periods=12h
        df_ohlcv_tmp['Indic_MA_15d_uptrend'] = (df_ohlcv_tmp.Indic_MA_15d.pct_change(periods=nb_periods)).astype(
            float)
        # [Interpretation] MA 7 days pct change on last nb_periods=12h
        df_ohlcv_tmp['Indic_MA_7d_uptrend'] = (df_ohlcv_tmp.Indic_MA_7d.pct_change(periods=nb_periods)).astype(
            float)

        # [Interpretation] BBands close_price - Indic_Bbands_20d_upperband
        df_ohlcv_tmp[
            'Indic_Bbands_20d_diff_close_upperband'] = df_ohlcv_tmp.close_price \
                                                       - df_ohlcv_tmp.Indic_Bbands_20d_upperband
        # [Interpretation] BBands close_price - Indic_Bbands_20d_middleband
        df_ohlcv_tmp[
            'Indic_Bbands_20d_diff_close_upperband'] = df_ohlcv_tmp.close_price \
                                                       - df_ohlcv_tmp.Indic_Bbands_20d_middleband
        # [Interpretation] BBands close_price - Indic_Bbands_20d_middleband
        df_ohlcv_tmp[
            'Indic_Bbands_20d_diff_close_lowerband'] = df_ohlcv_tmp.close_price \
                                                       - df_ohlcv_tmp.Indic_Bbands_20d_lowerband

        # [Interpretation] RSI 14 days pct change  on last nb_periods=12h
        df_ohlcv_tmp['Indic_RSI_14d_uptrend'] = (df_ohlcv_tmp.Indic_RSI_14d.pct_change(periods=nb_periods)).astype(
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

        # [Interpretation] OBV pct change on last 3d
        df_ohlcv_tmp['Indic_OBV_uptrend_3d'] = (df_ohlcv_tmp.Indic_OBV.pct_change(periods=3 * 24)).astype(
            float)
        # [Interpretation] OBV pct change on last 7d
        df_ohlcv_tmp['Indic_OBV_uptrend_7d'] = (df_ohlcv_tmp.Indic_OBV.pct_change(periods=7 * 24)).astype(
            float)
        # [Interpretation] OBV pct change on last 15d
        df_ohlcv_tmp['Indic_OBV_uptrend_15d'] = (df_ohlcv_tmp.Indic_OBV.pct_change(periods=15 * 24)).astype(
            float)
        # [Interpretation] OBV pct change on last 30d
        df_ohlcv_tmp['Indic_OBV_uptrend_30d'] = (df_ohlcv_tmp.Indic_OBV.pct_change(periods=30 * 24)).astype(
            float)

        return df_ohlcv_tmp.drop(['open_price', 'high_price', 'low_price', 'close_price', 'volume_aggregated_1h'],
                                 axis=1)
