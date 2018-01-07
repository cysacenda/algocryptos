from dbaccess.dbconnection import dbConnection
from cryptocompare.cryptocompare import CryptoCompare
from coinmarketcap.coinmarketcap import CoinMarketCap
import datetime
import time
from datetime import datetime
import tzlocal

#region Coins list

# Cryptocompare : Insert coins list into BDD
def extract_crytopcompare_coins():
    dbconn = dbConnection()
    dbconn.exexute_query(create_query_coins())

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

#endregion AA

#region Coins current prices
# TODO : Add system which insert / update depending on information already in DB
def extract_coinmarketcap_prices():
    dbconn = dbConnection()
    dbconn.exexute_query(create_query_prices())

def create_query_prices():
    coinmarket = CoinMarketCap()
    data = coinmarket.get_price_list()

    insertquery = 'INSERT INTO public.prices (symbol, rank, price_usd, price_btc, "24h_volume_usd", market_cap_usd, percent_change_1h, percent_change_24h,percent_change_7d, last_updated)\n'
    insertquery += 'VALUES \n('

    #print(entry['name'] + '\n')

    for entry in data:
        if (not insertquery.endswith('(')):
            insertquery += ',\n('
        insertquery += "'" + entry['symbol'] + "',"
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
            unix_timestamp = float(entry['last_updated'])
            local_timezone = tzlocal.get_localzone()  # get pytz timezone
            local_time = datetime.fromtimestamp(unix_timestamp, local_timezone)
            insertquery += "'" + datetime.fromtimestamp(unix_timestamp, local_timezone).strftime("%Y-%m-%d %H:%M:%S") + "'"

        insertquery += ')'
    insertquery += ';'
    return insertquery

#endregion

#region Coins socials stats

def extract_cryptocompare_socialstats():
    dbconn = dbConnection()
    dbconn.exexute_query(extract_cryptocompare_socialstats())

def create_cryptocompare_socialstats():
    #boucle sur tous les coins

    cryptocomp = CryptoCompare()
    data = cryptocomp.get_socialstats(1182)

    insertquery = 'INSERT INTO public.prices (symbol, rank, price_usd, price_btc, "24h_volume_usd", market_cap_usd, percent_change_1h, percent_change_24h,percent_change_7d, last_updated)\n'
    insertquery += 'VALUES \n('

    #TODO : Stockage des dernières données + historisation au fur et à mesure
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

    #Twitter
""""
       account_creation": "1390763724", - social_infos
       name": "Ethereum", - social_infos
       lists": 4567,
       statuses": 1890,
       favourites": "2241",
       followers": 287755, - social_stats
       link": "https://twitter.com/ethereumproject", - social_infos
       Points": 310591
    },
    "Reddit": {
        "posts_per_hour": "2.40", 
        "comments_per_hour": "61.96",
        "posts_per_day": "57.51", - social_stats
        "comments_per_day": 1487.09, - social_stats
        "name": "ethereum", - social_infos
        "link": "https://www.reddit.com/r/ethereum/", - social_infos
        "active_users": 6973, - social_stats
        "community_creation": "1387037735", - social_infos
        "subscribers": 253600, - social_stats
        "Points": 277493
    },
    "Facebook": {
        "likes": 120800, - social_stats
        "link": "https://www.facebook.com/ethereumproject/", - social_infos
        "is_closed": "false",
        "talking_about": "4142", - social_stats
        "name": "Ethereum", - social_infos
        "Points": 120800
    },
    "CodeRepository": {
        /////// AGGREGER LES DONNES DES DIFFERENTS REPO
        "List": [{
            "created_at": "1441653399",
            "open_total_issues": "0",
            "parent": {
                "Name": "",
                "Url": "",
                "InternalId": -1
            },
            "size": "6739",
            "closed_total_issues": "92",
            "stars": 8,
            "last_update": "1513776656",
            "forks": 28,
            "url": "https://github.com/ethereum/libweb3core", - code_infos
            "closed_issues": "0",
            "closed_pull_issues": "92",
            "fork": "false",
            "last_push": "1471550273", - code_infos
            "source": {
                "Name": "",
                "Url": "",
                "InternalId": -1
            },
            "open_pull_issues": "0",
            "language": "null",
            "subscribers": 27, - code_stats
            "open_issues": "0" - code_stats
        }, {
            "created_at": "1388063146",
            "open_total_issues": "732",
            "parent": {
                "Name": "",
                "Url": "",
                "InternalId": -1
            },
            "size": "93235",
            "closed_total_issues": "505",
            "stars": 11229,
            "last_update": "1515325492",
            "forks": 3424,
            "url": "https://github.com/ethereum/go-ethereum",
            "closed_issues": "228",
            "closed_pull_issues": "452",
            "fork": "false",
            "last_push": "1515244895",
            "source": {
                "Name": "",
                "Url": "",
                "InternalId": -1
            },
            "open_pull_issues": "29",
            "language": "Go",
            "subscribers": 1237,
            "open_issues": "52"
        }, {
            "created_at": "1399967414",
            "open_total_issues": "81",
            "parent": {
                "Name": "",
                "Url": "",
                "InternalId": -1
            },
            "size": "45235",
            "closed_total_issues": "807",
            "stars": 981,
            "last_update": "1515316347",
            "forks": 540,
            "url": "https://github.com/ethereum/ethereumj",
            "closed_issues": "355",
            "closed_pull_issues": "277",
            "fork": "false",
            "last_push": "1515275854",
            "source": {
                "Name": "",
                "Url": "",
                "InternalId": -1
            },
            "open_pull_issues": "28",
            "language": "Java",
            "subscribers": 189,
            "open_issues": "53"
        }, {
            "created_at": "1387852805",
            "open_total_issues": "81",
            "parent": {
                "Name": "",
                "Url": "",
                "InternalId": -1
            },
            "size": "5500",
            "closed_total_issues": "4636",
            "stars": 1917,
            "last_update": "1515324752",
            "forks": 567,
            "url": "https://github.com/ethereum/pyethereum",
            "closed_issues": "2163",
            "closed_pull_issues": "2473",
            "fork": "false",
            "last_push": "1514910361",
            "source": {
                "Name": "",
                "Url": "",
                "InternalId": -1
            },
            "open_pull_issues": "51",
            "language": "Python",
            "subscribers": 268,
            "open_issues": "681"
        }],
        "Points": 28416
    }
"""""

    #Reddit

    #Facebook

    #CodeRepository


    #print(entry['name'] + '\n')

#endregion
