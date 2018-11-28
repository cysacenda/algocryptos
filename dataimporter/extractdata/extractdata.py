from random import randint
from commons.dbaccess import DbConnection
from cryptocompare.cryptocompare import CryptoCompare
from coinmarketcap.coinmarketcap import CoinMarketCap
import reddit
import time
import json
from commons.config import Config
from commons.utils import utils
import logging
import pandas.io.sql as psql
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from pytrends.request import TrendReq
from googletrend.googletrend import get_info_google_trend
from commons.processmanager import ProcessManager
from matplot import matplot

conf = Config()
MINIMUM_MARKET_CAP_USD = conf.get_config('market_params', 'minimum_market_cap_usd')

# region Coins list

# Cryptocompare : Insert coins list into BDD
def extract_crytopcompare_coins():
    logging.warning("extract_crytopcompare_coins - start")
    dbconn = DbConnection()
    dbconn.exexute_query("Delete from coins;")
    dbconn.exexute_query(__create_query_coins())
    logging.warning("extract_crytopcompare_coins - end")


# Cryptocompare : Get coins list and create insert query for BDD
# TODO : Add system which insert / update depending on information already in DB
def __create_query_coins():
    cryptocomp = CryptoCompare()
    data = cryptocomp.get_coin_list()

    insertquery = 'INSERT INTO public.coins (id_cryptocompare, crypto_name, symbol, coin_name, total_coin_supply, ' \
                  'sort_order, proof_type, algorithm, image_url)\n'
    insertquery += 'VALUES \n('
    for key in data:
        if not insertquery.endswith('('):
            insertquery += ',\n('
        insertquery += data[key]['Id'] + ','
        insertquery += "'" + data[key]['Name'] + "',"
        insertquery += "'" + data[key]['Symbol'] + "',"
        insertquery += "'" + data[key]['CoinName'].replace('"', '').replace("'", "") + "',"
        insertquery += "'" + data[key]['TotalCoinSupply'] + "',"
        insertquery += data[key]['SortOrder'] + ','
        insertquery += "'" + data[key]['ProofType'] + "',"
        insertquery += "'" + data[key]['Algorithm'] + "',"
        if 'ImageUrl' in data[key].keys():
            insertquery += "'" + data[key]['ImageUrl'] + "'"
        else:
            insertquery += "''"
        insertquery += ')'
    insertquery += ';'
    return insertquery


# endregion

# region Coins current prices

# TODO : Add system which insert / update depending on information already in DB
def extract_coinmarketcap_prices():
    logging.warning("extract_coinmarketcap_prices - start")
    dbconn = DbConnection()
    dbconn.exexute_query("Delete from prices;")
    dbconn.exexute_query(__create_query_prices())
    logging.warning("extract_coinmarketcap_prices - end")


def __create_query_prices():
    logging.warning("create_query_prices - start")
    coinmarket = CoinMarketCap()
    data = coinmarket.get_price_list()

    insertquery = 'INSERT INTO public.prices (symbol, crypto_name, crypto_rank, price_usd, price_btc, ' \
                  'volume_usd_24h, market_cap_usd, percent_change_1h, percent_change_24h, ' \
                  'percent_change_7d, available_supply, last_updated)\n'
    insertquery += 'VALUES \n('

    for entry in data:
        # TODO : For the moment, do not take into account cryptos with ' in name
        if not str(entry['name']).__contains__("'"):
            if not insertquery.endswith('('):
                insertquery += ',\n('
            insertquery += "'" + entry['symbol'] + "',"
            insertquery += "'" + entry['name'] + "',"
            insertquery += entry['rank'] + ","

            if entry['price_usd'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['price_usd'] + ","

            if entry['price_btc'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['price_btc'] + ","

            if entry['24h_volume_usd'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['24h_volume_usd'] + ","

            if entry['market_cap_usd'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['market_cap_usd'] + ","

            if entry['percent_change_1h'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['percent_change_1h'] + ","

            if entry['percent_change_24h'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['percent_change_24h'] + ","

            if entry['percent_change_7d'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['percent_change_7d'] + ","

            if entry['available_supply'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['available_supply'] + ","

            if entry['last_updated'] is None:
                insertquery += 'NULL'
            else:
                insertquery += "'" + utils.format_linux_timestamp_to_db(float(entry['last_updated'])) + "'"

            insertquery += ')'
    insertquery += ';'
    logging.warning("create_query_prices - end")
    return insertquery


# Decommissioned
def extract_coinmarketcap_historical_prices():
    logging.warning("extract_coinmarketcap_histo_prices - start")
    dbconn = DbConnection()
    dbconn.exexute_query(__create_query_historical_prices())
    dbconn.exexute_query(__create_add_ids("histo_prices"))
    remove_useless_prices("histo_prices")
    logging.warning("extract_coinmarketcap_histo_prices - end")


def __create_query_historical_prices():
    logging.warning("create_historical_query_prices - start")
    coinmarket = CoinMarketCap()
    data = coinmarket.get_price_list()
    current_time = time.time()

    insertquery = 'INSERT INTO public.histo_prices (symbol, crypto_name, price_usd, price_btc, ' \
                  'volume_usd_24h, market_cap_usd, timestamp)\n'
    insertquery += 'VALUES \n('

    for entry in data:
        if not str(entry['name']).__contains__("'"):
            if not insertquery.endswith('('):
                insertquery += ',\n('
            insertquery += "'" + entry['symbol'] + "',"
            insertquery += "'" + entry['name'] + "',"

            if entry['price_usd'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['price_usd'] + ","

            if entry['price_btc'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['price_btc'] + ","

            if entry['24h_volume_usd'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['24h_volume_usd'] + ","

            if entry['market_cap_usd'] is None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['market_cap_usd'] + ","

            insertquery += "'" + utils.format_linux_timestamp_to_db(current_time) + "'"
            insertquery += ')'
    insertquery += ';'
    logging.warning("create_historical_query_prices - end")
    return insertquery


# endregion

# region Remove useless coins / prices

def remove_useless_prices_coins():
    logging.warning("remove_useless_prices_coins - start")
    remove_useless_prices("prices")
    remove_useless_coins()
    logging.warning("remove_useless_prices_coins - end")


def remove_useless_prices(table):
    dbconn = DbConnection()
    dbconn.exexute_query(
        "delete from " + table + " where market_cap_usd < {} or market_cap_usd is null".format(MINIMUM_MARKET_CAP_USD))


def remove_useless_coins():
    dbconn = DbConnection()
    dbconn.exexute_query(
        'delete from coins where coin_name not in (select crypto_name from prices) '
        'AND symbol not in (select symbol from prices)')


def delete_excluded_coins():
    logging.warning("delete_excluded_coins - start")
    dbconn = DbConnection()
    dbconn.exexute_query('delete from prices where id_cryptocompare in (select * from excluded_coins);')
    dbconn.exexute_query('delete from coins where id_cryptocompare in (select * from excluded_coins);')
    logging.warning("delete_excluded_coins - end")


# endregion

# region Add Ids

def add_ids():
    logging.warning("add_ids - start")
    dbconn = DbConnection()
    dbconn.exexute_query(__create_add_ids("prices"))
    logging.warning("add_ids - end")


def __create_add_ids(table):
    update_query = 'UPDATE ' + table + ' as ta\n'
    update_query += 'SET id_cryptocompare = co.id_cryptocompare\n'
    update_query += 'FROM coins as co\n'
    update_query += 'WHERE co.symbol = ta.symbol AND ta.id_cryptocompare IS NULL;\n\n'

    update_query += 'UPDATE ' + table + ' as ta\n'
    update_query += 'SET id_cryptocompare = co.id_cryptocompare\n'
    update_query += 'FROM coins as co\n'
    update_query += 'WHERE co.coin_name = ta.crypto_name AND ta.id_cryptocompare IS NULL;'
    return update_query


# endregion

# region Coins socials stats

def extract_cryptocompare_social():
    logging.warning("extract_cryptocompare_social - start")
    # Get coins id to be retrieved from APIs
    dbconn = DbConnection()
    dbconn.exexute_query("Delete from social_infos;")
    rows = dbconn.get_query_result('select id_cryptocompare from coins')
    for row in rows:
        dbconn.exexute_query(create_cryptocompare_social(row[0]))

    logging.warning("extract_cryptocompare_social - end")


def create_cryptocompare_social(coin_id):
    cryptocomp = CryptoCompare()
    data = cryptocomp.get_socialstats(coin_id)
    return __create_cryptocompare_social_infos(coin_id, data) + "\n" + create_cryptocompare_social_stats(coin_id, data)


def __create_cryptocompare_social_infos(coin_id, data):
    insertquery_socialinfos = 'INSERT INTO public.social_infos(id_cryptocompare, ' \
                              'twitter_account_creation, twitter_name, twitter_link, ' \
                              'reddit_name, reddit_link, reddit_community_creation, ' \
                              'facebook_name, facebook_link)\n'
    insertquery_socialinfos += 'VALUES \n('
    insertquery_socialinfos += str(coin_id) + ','

    # Twitter
    if 'name' in data['Twitter'].keys():
        insertquery_socialinfos += "'" + utils.format_linux_timestamp_to_db(
            float(data['Twitter']['account_creation'])) + "',"
        insertquery_socialinfos += "'" + data['Twitter']['name'].replace('"', '').replace("'", "") + "',"
        insertquery_socialinfos += "'" + data['Twitter']['link'] + "',"
    else:
        insertquery_socialinfos += "NULL, NULL, NULL,"

    # Reddit
    if 'name' in data['Reddit'].keys() and data['Reddit']['name'] != 'undefined':
        insertquery_socialinfos += "'" + data['Reddit']['name'] + "',"
        insertquery_socialinfos += "'" + data['Reddit']['link'] + "',"
        insertquery_socialinfos += "'" + utils.format_linux_timestamp_to_db(
            float(data['Reddit']['community_creation'])) + "',"
    else:
        insertquery_socialinfos += "NULL, NULL, NULL,"

    # Facebook
    if 'name' in data['Facebook'].keys() and 'link' in data['Facebook'].keys():
        insertquery_socialinfos += "'" + data['Facebook']['name'] + "',"
        insertquery_socialinfos += "'" + data['Facebook']['link'] + "'"
    else:
        insertquery_socialinfos += "NULL, NULL"

    insertquery_socialinfos += ');'
    return insertquery_socialinfos


def create_cryptocompare_social_stats(coin_id, data):
    insertquery_socialinfos = 'INSERT INTO public.social_stats (id_cryptocompare, ' \
                              'twitter_followers, reddit_posts_per_day, reddit_comments_per_day, ' \
                              'reddit_active_users, reddit_subscribers, facebook_likes, ' \
                              'facebook_talking_about, timestamp)\n'
    insertquery_socialinfos += 'VALUES \n('
    insertquery_socialinfos += str(coin_id) + ','

    # Twitter
    if 'followers' in data['Twitter'].keys():
        insertquery_socialinfos += str(data['Twitter']['followers']) + ","
    else:
        insertquery_socialinfos += "0,"

    # Reddit
    if ('posts_per_day' in data['Reddit'].keys() and 'comments_per_day' in data['Reddit'].keys() and 'active_users' in
            data['Reddit'].keys() and 'subscribers' in data['Reddit'].keys()):
        insertquery_socialinfos += str(data['Reddit']['posts_per_day']) + ","
        insertquery_socialinfos += str(data['Reddit']['comments_per_day']) + ","
        insertquery_socialinfos += str(data['Reddit']['active_users']) + ","
        insertquery_socialinfos += str(data['Reddit']['subscribers']) + ","
    else:
        insertquery_socialinfos += "0, 0, 0, 0,"

    # Facebook
    if 'likes' in data['Facebook'].keys() and 'talking_about' in data['Facebook'].keys():
        insertquery_socialinfos += str(data['Facebook']['likes']) + ","
        insertquery_socialinfos += str(data['Facebook']['talking_about']) + ", "
    else:
        insertquery_socialinfos += "0, 0,"

    # Timestamp
    insertquery_socialinfos += "current_timestamp"

    insertquery_socialinfos += ');'
    return insertquery_socialinfos


# endregion

# region Reddit

# TODO : Gerer pour ne recuperer que ce qu'on a pas deja
def extract_reddit_data():
    logging.warning("import_reddit_histo - start")
    # Get coins and associated subreddits id to be retrieved from APIs
    dbconn = DbConnection()
    query_select = 'Select co.id_cryptocompare, ' \
                   'CASE WHEN som.reddit_name IS NULL THEN so.reddit_name ELSE som.reddit_name END ' \
                   'AS reddit_agr, max(timestamp)\n'
    query_select += 'from coins as co\n'
    query_select += 'left outer join social_infos_manual som on (co.id_cryptocompare = som.id_cryptocompare)\n'
    query_select += 'left outer join social_infos so on (co.id_cryptocompare = so.id_cryptocompare)\n'
    query_select += 'left outer join social_stats_reddit_histo ss on (so.id_cryptocompare = ss.id_cryptocompare)\n'
    query_select += 'where CASE WHEN som.reddit_name IS NULL THEN so.reddit_name ELSE som.reddit_name END ' \
                    'is not null\n'
    query_select += 'group by co.id_cryptocompare, reddit_agr;'
    rows = dbconn.get_query_result(query_select)

    for row in rows:
        # region Recuperation historique (scraping redditmetrics.com)

        # Si aucun historique, on recupere tout
        if row[2] is None:
            subscribers, dates = reddit.get_subscribers_histo(row[1])
            if not not subscribers:
                dbconn.exexute_query(__create_query_reddit_stats(row[0], subscribers, dates))

        # Si historique partiel, on essaye de recuperer l'historique aux dates manquantes
        elif (datetime.now().astimezone() - row[2]).days >= 2:
            subscribers, dates = reddit.get_subscribers_histo(row[1], after_date=row[2])
            if not not subscribers:
                dbconn.exexute_query(__create_query_reddit_stats(row[0], subscribers, dates))
        # endregion

        # region Recuperation temps reel a maintenant (reddit.com => about.json)

        req = __create_query_reddit_real_time(row[0], reddit.get_reddit_infos_real_time(row[1]))

        if req != '':
            dbconn.exexute_query(req)

        # endregion

    # Empty table containing last infos (already saved in histo)
    deletequery = 'delete from social_stats_reddit'
    dbconn.exexute_query(deletequery)

    # Retrieve last from histo
    insertquery2 = 'INSERT INTO public.social_stats_reddit\n'
    insertquery2 += 'select * from social_stats_reddit_histo\n'
    insertquery2 += 'where timestamp > current_timestamp  - interval ' + "'1 hour'"

    dbconn.exexute_query(insertquery2)

    logging.warning("import_reddit_histo - end")


def __create_query_reddit_stats(coin_id, subscribers, dates):
    insertquery_reddit_stats = 'INSERT INTO public.social_stats_reddit_histo(id_cryptocompare, ' \
                               'reddit_subscribers, timestamp)\n'
    insertquery_reddit_stats += 'VALUES\n('
    for value, integ in enumerate(subscribers):
        if not insertquery_reddit_stats.endswith('('):
            insertquery_reddit_stats += ',\n('

        insertquery_reddit_stats += str(coin_id) + ','
        insertquery_reddit_stats += str(integ) + ','
        insertquery_reddit_stats += "'" + str(dates[value]) + "'"

        insertquery_reddit_stats += ')'
    insertquery_reddit_stats += ';'
    return insertquery_reddit_stats


def __create_query_reddit_real_time(coin_id, dict_infos):
    reddit_real_time = ''

    if dict_infos is not None and 'subscribers' in dict_infos.keys() and 'active_user_count' in dict_infos.keys():
        reddit_real_time = 'INSERT INTO public.social_stats_reddit_histo (id_cryptocompare, ' \
                           'reddit_subscribers, reddit_active_users, timestamp)\n'
        reddit_real_time += 'VALUES \n('
        reddit_real_time += str(coin_id) + ','
        reddit_real_time += str(dict_infos['subscribers']) + ","
        reddit_real_time += str(dict_infos['active_user_count']) + ","
        reddit_real_time += "current_timestamp"
        reddit_real_time += ');'
    return reddit_real_time


# endregion

# region Trading pairs & histo volumes, prices

def extract_histo_ohlcv():
    logging.warning("extract_histo_ohlcv - start")
    # Get coins id to be retrieved from APIs
    dbconn = DbConnection()
    req = 'select co.id_cryptocompare, co.symbol, max(hi.timestamp),\n'
    req += 'case when tp.id_cryptocompare is null then false else true end as top_crypto \n'
    req += 'from coins as co\n'
    req += 'left outer join top_cryptos as tp on (co.id_cryptocompare = tp.id_cryptocompare)\n'
    req += 'left outer join histo_ohlcv as hi on (co.id_cryptocompare = hi.id_cryptocompare)\n'
    req += 'group by co.id_cryptocompare, co.symbol, co.sort_order, top_crypto'
    rows = dbconn.get_query_result(req)
    for row in rows:
        dict_dates_volumes = __get_histo_volumes_for_coin(row[0], row[1], row[2], row[3])
        __extract_histo_ohlc_for_coin(row[0], row[1], row[2], dict_dates_volumes)

    logging.warning("extract_histo_ohlcv - end")

def __get_histo_volumes_for_coin(coin_id, symbol, lastdate, is_topcrypto):
    dict_dates_volumes = {}
    data = __get_trading_pairs_for_crypto(symbol, is_topcrypto)

    if data is not None:
        for key in data:
            __get_histo_ohlcv_for_pair(dict_dates_volumes, symbol, key['toSymbol'], lastdate)

    return dict_dates_volumes;

def __extract_histo_ohlc_for_coin(coin_id, symbol, lastdate, dict_dates_volumes):
    cryptocomp = CryptoCompare()
    limit = 2000

    # If data already in database, retrieve only needed data
    if lastdate is not None:
        limit = int(((datetime.now().astimezone() - lastdate).total_seconds()) / 3600) - 1
        if limit == 0:
            limit = 1

    data = cryptocomp.get_histo_hour_pair(symbol, conf.get_config('cryptocompare_params', 'default_currency'), limit)

    dbconn = DbConnection()
    insertquery = __create_query_histo_ohlc(coin_id, data, dict_dates_volumes)
    if insertquery != '':
        dbconn.exexute_query(insertquery)

def __get_trading_pairs_for_crypto(symbol, is_topcrypto):
    # Main cryptos : more trading pairs taken into account
    param = 'max_trading_pairs_for_crypto'
    if is_topcrypto:
        param = 'max_trading_pairs_for_top_crypto'

    max_trading_pairs_for_crytpto = conf.get_config('cryptocompare_params', param)

    cryptocomp = CryptoCompare()
    data = cryptocomp.get_trading_pairs(symbol, max_trading_pairs_for_crytpto)
    return data


def __get_histo_ohlcv_for_pair(dict_dates_volumes, symbol_from, symbol_to, lastdate):
    cryptocomp = CryptoCompare()
    limit = 2000

    # If data already in database, retrieve only needed data
    if lastdate is not None:
        limit = int(((datetime.now().astimezone() - lastdate).total_seconds()) / 3600) - 1
        if limit == 0:
            limit = 1

    data = cryptocomp.get_histo_hour_pair(symbol_from, symbol_to, limit)
    if data is not None:
        for key in data:
            if int(key['time']) in dict_dates_volumes.keys():
                dict_dates_volumes[int(key['time'])] += key['volumefrom']
            else:
                dict_dates_volumes[int(key['time'])] = key['volumefrom']

def __create_query_histo_ohlc(coin_id, data, dict_dates_volumes):
    insertquery = ''
    if data is not None:
        for key in data:
            date = utils.format_linux_timestamp_to_datetime(float(key['time']))
            # Do not take into account unfinished period
            if (datetime.now().astimezone() - date).seconds > 60 * 60:
                insertquery += 'INSERT INTO public.histo_ohlcv (id_cryptocompare, ' \
                      'open_price, high_price, low_price, close_price, volume_aggregated, timestamp)\n'
                insertquery += 'VALUES(' + str(coin_id) + ', '
                insertquery += utils.float_to_str(key['open']) + ', '
                insertquery += utils.float_to_str(key['high']) + ', '
                insertquery += utils.float_to_str(key['low']) + ', '
                insertquery += utils.float_to_str(key['close']) + ', '

                if int(key['time']) in dict_dates_volumes.keys():
                    insertquery += utils.float_to_str(dict_dates_volumes[int(key['time'])]) + ', '
                else:
                    insertquery += 'Null, '

                insertquery += "'" + utils.format_linux_timestamp_to_db(float(key['time'])) + "');\n"
    return insertquery

# endregion

# region ATH

def extract_lower_higher_prices():
    logging.warning("extract_lower_higher_prices - start")

    dbconn = DbConnection()
    dbconn.exexute_query('Delete from lower_higher_prices;')
    rows = dbconn.get_query_result('select id_cryptocompare, symbol from coins')

    connection = create_engine(utils.get_connection_string())
    for row in rows:
        __get_query_lower_higher_prices_for_coin(connection, row[0], row[1])

    logging.warning("extract_lower_higher_prices - end")

def __get_query_lower_higher_prices_for_coin(connection, coin_id, symbol):
    cryptocomp = CryptoCompare()
    data = cryptocomp.get_histo_day_pair(symbol)

    # get data via API
    data = json.loads(data)
    df = pd.DataFrame(data["Data"])

    if not df.empty:
        # delete useless columns
        df.drop(['close', 'open', 'volumefrom', 'volumeto'], axis=1, inplace=True)

        # convert todatetime
        df['time'] = pd.to_datetime(df['time'], unit='s')

        # set index on column timestamp
        df.set_index('time', inplace=True)

        # drop rows with 0 only
        columns = ['low', 'high']
        df = df.replace(0, pd.np.nan).dropna(axis=0, how='any', subset=columns).fillna(0).astype(float)

        #empty si les données renvoyées sont toutes nulles ou 0
        if not df.empty:

            # df to insert into db
            df_final = pd.DataFrame()
            df_final['id_cryptocompare'] = [coin_id]

            # df columns
            columns_arr = ['price_low_15d', 'date_low_15d', 'price_high_15d', 'date_high_15d',
                           'price_low_1m', 'date_low_1m', 'price_high_1m', 'date_high_1m',
                           'price_low_3m', 'date_low_3m', 'price_high_3m', 'date_high_3m',
                           'price_low_6m', 'date_low_6m', 'price_high_6m', 'date_high_6m',
                           'price_low_1y', 'date_low_1y', 'price_high_1y', 'date_high_1y',
                           'price_low_5y', 'date_low_5y', 'price_high_5y', 'date_high_5y']

            # 15d/1m/3m/6m/12m/all
            arr = [15, 30, 3 * 30, 6 * 30, 12 * 30, 2000]
            date_after = datetime.now()
            i = 0
            for elt in arr:
                date_before = date_after - timedelta(days=elt)
                df_tmp = df.truncate(before=date_before, after=date_after)
                df_final[columns_arr[i]] = [df_tmp.low.min()]
                df_final[columns_arr[i + 1]] = [df_tmp.low.idxmin()]
                df_final[columns_arr[i + 2]] = [df_tmp.high.max()]
                df_final[columns_arr[i + 3]] = [df_tmp.high.idxmax()]
                i += 4

            df_final.to_sql(name='lower_higher_prices', con=connection, if_exists='append', index=False)


# endregion ATH

# region Global data

# CMC global data
def extract_cmc_global_data():
    logging.warning("extract_cmc_global_data - start")
    dbconn = DbConnection()
    dbconn.exexute_query("Delete from global_data;")
    dbconn.exexute_query(__create_query_global_data())
    logging.warning("extract_cmc_global_data - end")


# CMC : CMC global data and create insert query for BDD
# TODO : Add system which insert / update depending on information already in DB
def __create_query_global_data():
    coinmarket = CoinMarketCap()
    data = coinmarket.get_global_data()
    if data is None:
        raise Exception('__create_query_global_data - No data')

    insertquery = 'INSERT INTO public.global_data (total_market_cap_usd,' \
                  'total_24h_volume_usd, bitcoin_percentage_of_market_cap, timestamp)\n'
    insertquery += 'VALUES ('
    insertquery += str(data['total_market_cap_usd'] / 1000000000) + ', '
    insertquery += str(data['total_24h_volume_usd'] / 1000000000) + ', '
    insertquery += str(data['bitcoin_percentage_of_market_cap']) + ', '
    insertquery += 'current_timestamp);'
    return insertquery


# endregion


# region Google Trend

def extract_google_trend_info():
    extract_google_trend_info_period('today 5-y', 'social_google_trend')
    extract_google_trend_info_period('today 1-m', 'social_google_trend_1m')

def extract_google_trend_info_period(pytrend_period, sql_table):
    # Process manager
    procM = ProcessManager()

    logging.warning("extract_google_trend_info - start" + pytrend_period)

    standard = 'bitcoin'
    df_to_db = None

    pytrends = TrendReq(hl='en-US', tz=360)
    connection = create_engine(utils.get_connection_string())

    # get data with query
    squery = 'SELECT id_cryptocompare, symbol, coin_name \n'
    squery += 'FROM coins'

    df_coins = psql.read_sql_query(squery, connection)

    df_to_db = None
    count = 0
    tentative = 0

    #For each coin
    for coin_index, coin_row in df_coins.iterrows():

        try:
            #Get info from google trend
            tentative += 1
            logging.warning('Tentative number :' + str(tentative))
            # wait a random amount of time to avoid bot detection
            if (tentative % 10 == 0):
                #break
                logging.warning('Waiting ...')
                time.sleep(randint(5,15))
            df_to_db = get_info_google_trend(pytrends, df_to_db, standard, coin_row, pytrend_period)
            count += 1
            logging.warning('Number of coins done :' + str(count))
        except Exception as e:
            procM.setIsError()
            logging.error('Uncatched error :' + str(e))

    #Delete in BDD - Do not keep the historical data
    connection.execute('delete from ' + sql_table)

    #Insert in BDD
    logging.warning("extract_google_trend_info - insert BDD")

    if df_to_db is not None:
        logging.warning("df_to_db not empty")
        df_to_db.to_sql(name=sql_table, con=connection, if_exists='append', index=False)
    else:
        logging.warning("df_to_db empty")

    logging.warning("extract_google_trend_info - end" + pytrend_period)


# endregion

# region Generate images

def generate_images_prices_volumes():
    logging.warning("generate_images_prices_volumes - start")
    matplot.generate_prices_volumes_images()
    logging.warning("generate_images_prices_volumes - end")

# endregion