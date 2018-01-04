from dbaccess.dbconnection import dbConnection
from cryptocompare.cryptocompare import CryptoCompare
from coinmarketcap.coinmarketcap import CoinMarketCap
import datetime
import time
from datetime import datetime
import tzlocal

# Cryptocompare : Insert coins list into BDD
def extract_crytopcompare_coins():
    dbconn = dbConnection()
    dbconn.exexute_query(create_query_coins())


# Cryptocompare : Get coins list and create insert query for BDD
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
