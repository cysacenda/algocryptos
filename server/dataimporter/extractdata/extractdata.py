import time
from dbaccess.dbconnection import DbConnection
from cryptocompare.cryptocompare import CryptoCompare
from coinmarketcap.coinmarketcap import CoinMarketCap
from config.config import Config
import reddit
import utils
import logging
from datetime import datetime

conf = Config()
MINIMUM_MARKET_CAP_USD = conf.get_config('market_params', 'minimum_market_cap_usd')

# region Coins list

# Cryptocompare : Insert coins list into BDD
def extract_crytopcompare_coins():
    logging.warning("extract_crytopcompare_coins - start")
    dbconn = DbConnection()
    dbconn.exexute_query("Delete from coins;")
    dbconn.exexute_query(create_query_coins())
    logging.warning("extract_crytopcompare_coins - end")

# Cryptocompare : Get coins list and create insert query for BDD
# TODO : Add system which insert / update depending on information already in DB
def create_query_coins():
    cryptocomp = CryptoCompare()
    data = cryptocomp.get_coin_list()

    insertquery = 'INSERT INTO public.coins ("IdCryptoCompare", "Name", "Symbol", "CoinName", "TotalCoinSupply", "SortOrder", "ProofType", "Algorithm", "ImageUrl")\n'
    insertquery += 'VALUES \n('
    for key in data:
        if (not insertquery.endswith('(')):
            insertquery += ',\n('
        insertquery += data[key]['Id'] + ','
        insertquery += "'" + data[key]['Name'] + "',"
        insertquery += "'" + data[key]['Symbol'] + "',"
        insertquery += "'" + data[key]['CoinName'] + "',"
        insertquery += "'" + data[key]['TotalCoinSupply'] + "',"
        insertquery += data[key]['SortOrder'] + ','
        insertquery += "'" + data[key]['ProofType'] + "',"
        insertquery += "'" + data[key]['Algorithm'] + "',"
        if ('ImageUrl' in data[key].keys()):
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
    dbconn.exexute_query(create_query_prices())
    logging.warning("extract_coinmarketcap_prices - end")

def create_query_prices():
    logging.warning("create_query_prices - start")
    coinmarket = CoinMarketCap()
    data = coinmarket.get_price_list()

    insertquery = 'INSERT INTO public.prices (symbol, "Name", rank, price_usd, price_btc, "24h_volume_usd", market_cap_usd, percent_change_1h, percent_change_24h,percent_change_7d, last_updated)\n'
    insertquery += 'VALUES \n('

    for entry in data:
        #TODO : For the moment, do not take into account cryptos with ' in name
        if (not str(entry['name']).__contains__("'")):
            if (not insertquery.endswith('(')):
                insertquery += ',\n('
            insertquery += "'" + entry['symbol'] + "',"
            insertquery += "'" + entry['name'] + "',"
            insertquery += entry['rank'] + ","

            if entry['price_usd'] == None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['price_usd'] + ","

            if entry['price_btc'] == None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['price_btc'] + ","

            if entry['24h_volume_usd'] == None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['24h_volume_usd'] + ","

            if entry['market_cap_usd'] == None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['market_cap_usd'] + ","

            if entry['percent_change_1h'] == None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['percent_change_1h'] + ","

            if entry['percent_change_24h'] == None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['percent_change_24h'] + ","

            if entry['percent_change_7d'] == None:
                insertquery += 'NULL' + ","
            else:
                insertquery += entry['percent_change_7d'] + ","

            if entry['last_updated'] == None:
                insertquery += 'NULL'
            else:
                insertquery += "'" + utils.format_linux_timestamp_to_db(float(entry['last_updated'])) + "'"

            insertquery += ')'
    insertquery += ';'
    logging.warning("create_query_prices - end")
    return insertquery

# endregion

# region Remove useless coins / prices

def remove_useless_prices_coins():
    logging.warning("remove_useless_prices_coins - start")
    remove_useless_prices()
    remove_useless_coins()
    logging.warning("remove_useless_prices_coins - end")


def remove_useless_prices():
    dbconn = DbConnection()
    dbconn.exexute_query("delete from prices where market_cap_usd < {} or market_cap_usd is null".format(MINIMUM_MARKET_CAP_USD))


def remove_useless_coins():
    dbconn = DbConnection()
    dbconn.exexute_query('delete from coins where "CoinName" not in (select "Name" from prices) AND "Symbol" not in (select symbol from prices)')


def delete_excluded_coins():
    logging.warning("delete_excluded_coins - start")
    dbconn = DbConnection()
    dbconn.exexute_query('delete from prices where "IdCryptoCompare" in (select * from excluded_coins);')
    dbconn.exexute_query('delete from coins where "IdCryptoCompare" in (select * from excluded_coins);')
    logging.warning("delete_excluded_coins - end")

#endregion

# region Add Ids

def add_ids():
    logging.warning("add_ids - start")
    dbconn = DbConnection()
    dbconn.exexute_query(create_add_ids())

    # TODO : Gérer un mapping dans une table de paramétrage pour ces cryptos car rapprochement impossible entre cryptocompare et CMC
    """"" 
    -- KO dans table prices idCryptoCompare null
    -- requête: select *
    from prices where
    "IdCryptoCompare" is null
    'BCC', 'BitConnect'
    'GXS', 'GXShares'
    'XPA', 'XPlay'
    'ST', 'Simple Token'
    'JINN', 'Jinn'
    'INK', 'Ink'
    'DPY', 'Delphy'
    'PAYX', 'Paypex'
    'BOT', 'Bodhi'
    'TIPS', 'FedoraCoin'
    'ECN', 'E-coin'
    """""
    logging.warning("add_ids - end")

def create_add_ids():
    update_query = 'UPDATE prices as pr\n'
    update_query += 'SET "IdCryptoCompare" = co."IdCryptoCompare"\n'
    update_query += 'FROM coins as co\n'
    update_query += 'WHERE co."Symbol" = pr.symbol;\n\n'

    update_query += 'UPDATE prices as pr\n'
    update_query += 'SET "IdCryptoCompare" = co."IdCryptoCompare"\n'
    update_query += 'FROM coins as co\n'
    update_query += 'WHERE co."CoinName" = pr."Name";'
    return update_query;

# endregion

#region Coins socials stats

def extract_cryptocompare_social():
    logging.warning("extract_cryptocompare_social - start")
    # Get coins id to be retrieved from APIs
    dbconn = DbConnection()
    dbconn.exexute_query("Delete from social_infos;")
    dbconn.exexute_query("Delete from social_stats;")
    rows = dbconn.get_query_result('select "IdCryptoCompare" from coins')

    #TODO : utiliser url_limit_second / url_limit_hout pour limiter le nombre d'appels / période
    icount = 1
    for row in rows:
        dbconn.exexute_query(create_cryptocompare_social(row[0]))
        if icount % 5 == 0:
            time.sleep(0.1)

    logging.warning("extract_cryptocompare_social - end")


def create_cryptocompare_social(coin_id):
    cryptocomp = CryptoCompare()
    data = cryptocomp.get_socialstats(coin_id)
    return create_cryptocompare_social_infos(coin_id, data) + "\n" + create_cryptocompare_social_stats(coin_id, data)


def create_cryptocompare_social_infos(coin_id, data):
    insertquery_socialinfos = 'INSERT INTO public.social_infos("IdCoinCryptoCompare", "Twitter_account_creation", "Twitter_name", "Twitter_link", "Reddit_name", "Reddit_link", "Reddit_community_creation", "Facebook_name", "Facebook_link")\n'
    insertquery_socialinfos += 'VALUES \n('
    insertquery_socialinfos += str(coin_id) + ','

    # Twitter
    if ('name' in data['Twitter'].keys()):
        insertquery_socialinfos += "'" + utils.format_linux_timestamp_to_db(float(data['Twitter']['account_creation'])) + "',"
        insertquery_socialinfos += "'" + data['Twitter']['name'].replace('"', '').replace("'", "") + "',"
        insertquery_socialinfos += "'" + data['Twitter']['link'] + "',"
    else:
        insertquery_socialinfos += "NULL, NULL, NULL,"

    # Reddit
    if ('name' in data['Reddit'].keys() and data['Reddit']['name'] != 'undefined'):
        insertquery_socialinfos += "'" + data['Reddit']['name'] + "',"
        insertquery_socialinfos += "'" + data['Reddit']['link'] + "',"
        insertquery_socialinfos += "'" + utils.format_linux_timestamp_to_db(float(data['Reddit']['community_creation'])) + "',"
    else:
        insertquery_socialinfos += "NULL, NULL, NULL,"

    # Facebook
    if ('name' in data['Facebook'].keys() and 'link' in data['Facebook'].keys()):
        insertquery_socialinfos += "'" + data['Facebook']['name'] + "',"
        insertquery_socialinfos += "'" + data['Facebook']['link'] + "'"
    else:
        insertquery_socialinfos += "NULL, NULL"

    insertquery_socialinfos += ');'
    return insertquery_socialinfos


def create_cryptocompare_social_stats(coin_id, data):
    insertquery_socialinfos = 'INSERT INTO public.social_stats ("IdCoinCryptoCompare", "Twitter_followers", "Reddit_posts_per_day", "Reddit_comments_per_day", "Reddit_active_users", "Reddit_subscribers", "Facebook_likes", "Facebook_talking_about", "timestamp")\n'
    insertquery_socialinfos += 'VALUES \n('
    insertquery_socialinfos += str(coin_id) + ','

    # Twitter
    if ('followers' in data['Twitter'].keys()):
        insertquery_socialinfos += str(data['Twitter']['followers']) + ","
    else:
        insertquery_socialinfos += "0,"

    # Reddit
    if ('posts_per_day' in data['Reddit'].keys() and 'comments_per_day' in data['Reddit'].keys() and 'active_users' in data['Reddit'].keys() and 'subscribers' in data['Reddit'].keys()):
        insertquery_socialinfos += str(data['Reddit']['posts_per_day']) + ","
        insertquery_socialinfos += str(data['Reddit']['comments_per_day']) + ","
        insertquery_socialinfos += str(data['Reddit']['active_users']) + ","
        insertquery_socialinfos += str(data['Reddit']['subscribers']) + ","
    else:
        insertquery_socialinfos += "0, 0, 0, 0,"

    # Facebook
    if ('likes' in data['Facebook'].keys() and 'talking_about' in data['Facebook'].keys()):
        insertquery_socialinfos += str(data['Facebook']['likes']) + ","
        insertquery_socialinfos += str(data['Facebook']['talking_about']) + ", "
    else:
        insertquery_socialinfos += "0, 0,"

    # Timestamp
    insertquery_socialinfos += "current_timestamp"

    insertquery_socialinfos += ');'
    return insertquery_socialinfos

#endregion

# region Reddit

# TODO : Gérer pour ne récupérer que ce qu'on a pas déjà
def extract_reddit_data():
    logging.warning("import_reddit_histo - start")
    # Get coins and associated subreddits id to be retrieved from APIs
    dbconn = DbConnection()
    # TODO : A modifier quand on aura aussi des donneés des infos reddit saisies à la main (nouvelle table)
    query_select = 'Select co."IdCryptoCompare", CASE WHEN som."Reddit_name" IS NULL THEN so."Reddit_name" ELSE som."Reddit_name" END AS reddit_agr, max(timestamp)\n'
    query_select += 'from coins as co\n'
    query_select += 'left outer join social_infos_manual som on (co."IdCryptoCompare" = som."IdCoinCryptoCompare")\n'
    query_select += 'left outer join social_infos so on (co."IdCryptoCompare" = so."IdCoinCryptoCompare")\n'
    query_select += 'left outer join social_stats_reddit ss on (so."IdCoinCryptoCompare" = ss."IdCoinCryptoCompare")\n'
    query_select += 'where CASE WHEN som."Reddit_name" IS NULL THEN so."Reddit_name" ELSE som."Reddit_name" END is not null\n'
    query_select += 'group by co."IdCryptoCompare", reddit_agr;'
    rows = dbconn.get_query_result(query_select)

    # TODO : utiliser url_limit_second / url_limit_hout pour limiter le nombre d'appels / période
    for row in rows:
        # region Récupération historique (scraping redditmetrics.com)

        # Si aucun historique, on récupère tout
        if(row[2] == None):
            subscribers, dates = reddit.get_subscribers_histo(row[1])
            if(not not subscribers):
                dbconn.exexute_query(create_query_reddit_stats(row[0], subscribers, dates))

        # Si historique partiel, on essaye de récupérer l'historique aux dates manquantes
        elif((datetime.now().astimezone() - row[2]).days >= 2):
            # TODO : Filtrer sur date dans scraping
            subscribers, dates = reddit.get_subscribers_histo(row[1], after_date=row[2])
            if (not not subscribers):
                dbconn.exexute_query(create_query_reddit_stats(row[0], subscribers, dates))
        # endregion

        # region Récupération temps réel à maintenant (reddit.com => about.json)

        # endregion


    logging.warning("import_reddit_histo - end")

def create_query_reddit_stats(idCoin, subscribers, dates):
    insertquery_reddit_stats = 'INSERT INTO public.social_stats_reddit("IdCoinCryptoCompare", "Reddit_subscribers", "timestamp")\n'
    insertquery_reddit_stats += 'VALUES\n('
    for value, integ in enumerate(subscribers):
        if (not insertquery_reddit_stats.endswith('(')):
            insertquery_reddit_stats += ',\n('

        insertquery_reddit_stats += str(idCoin) + ','
        insertquery_reddit_stats += str(integ) + ','
        insertquery_reddit_stats += "'" + str(dates[value]) + "'"

        insertquery_reddit_stats += ')'
    insertquery_reddit_stats += ';'
    return insertquery_reddit_stats

# TODO : Récupérer via : https://www.reddit.com/r/EthereumClassic/about.json
"""""
-Ajouter aussi la donnée active user dans la table

-Json about :
    data/subscribers : bigint
    data/created : unix date
    data/active_user_count : Bigint

Algo récupération données Reddit :
-Pour chaque crypto :
    -Récupération de la dernière occurence dans la table social_stats_reddit :
        
        select co."IdCryptoCompare", so."Reddit_name", max(timestamp)
        from coins as co
        inner join social_infos so on (co."IdCryptoCompare" = so."IdCoinCryptoCompare")
        left outer join social_stats_reddit ss on (so."IdCoinCryptoCompare" = ss."IdCoinCryptoCompare")
        where so."Reddit_name" is not null
        group by co."IdCryptoCompare", so."Reddit_name"
        
        -Si last date < yesterday ou pas de date
            -Reccup histo via redditmetric (ne récupérer que après la dernière date stockée en base)
        -Récupérer pour la date du jour via le about.json


-Pourquoi le traitement plante au bout d'un certain nombre de cryptos à l'heure actuelle ?? => Bon sur 39, à voir sur plus
-Quid du nombre de posts ?
"""""

# endregion

#region Trading pairs & histo volumes, prices

def extract_histo_ohlcv():
    logging.warning("extract_histo_ohlcv - start")
    #extract_histo_ohlcv_for_coin(4560, 'MED')
    # Get coins id to be retrieved from APIs
    dbconn = DbConnection()
    rows = dbconn.get_query_result('select "IdCryptoCompare", "Symbol" from coins')

    # TODO : utiliser url_limit_second / url_limit_hout pour limiter le nombre d'appels / période
    icount = 1
    for row in rows:
        extract_histo_ohlcv_for_coin(row[0], row[1])
        if icount % 5 == 0:
            time.sleep(0.1)

    logging.warning("extract_histo_ohlcv - end")


def extract_histo_ohlcv_for_coin(coin_id, symbol):
    dict_dates_volumes = {}
    for key in get_trading_pairs_for_crypto(symbol):
        get_histo_ohlcv_for_pair(dict_dates_volumes, symbol, key['toSymbol'])

    # if found values
    if (dict_dates_volumes):
        dbconn = DbConnection()
        dbconn.exexute_query(create_query_histo_ohlcv(coin_id, dict_dates_volumes))


def get_trading_pairs_for_crypto(symbol):
    cryptocomp = CryptoCompare()
    data = cryptocomp.get_trading_pairs(symbol)
    return data

def get_histo_ohlcv_for_pair(dict_dates_volumes, symbolFrom, symbolTo):
    cryptocomp = CryptoCompare()

    # TODO : Limit 2000 to be replaced for retrieving only what's not in database
    data = cryptocomp.get_histo_hour_pair(symbolFrom, symbolTo, limit=2000)
    for key in data:
        if int(key['time']) in dict_dates_volumes.keys():
            dict_dates_volumes[int(key['time'])] += key['volumefrom']
        else:
            dict_dates_volumes[int(key['time'])] = key['volumefrom']

def create_query_histo_ohlcv(coin_id, data):
    insertquery = 'INSERT INTO public.histo_volumes ("IdCoinCryptoCompare", "1h_volumes_aggregated_pairs", "timestamp")\n'
    insertquery += 'VALUES \n('
    for key in data:
        if (not insertquery.endswith('(')):
            insertquery += ',\n('
        insertquery += str(coin_id) + ','
        insertquery += str(data[key]) + ','
        insertquery += "'" + utils.format_linux_timestamp_to_db(float(key)) + "'"
        insertquery += ')'
    insertquery += ';'
    return insertquery

#endregion