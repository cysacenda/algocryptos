import datetime
import time
import sys
import os
import json
from cryptocompare.cryptocompare import CryptoCompare
from dbaccess.dbconnection import dbConnection

# Utile ?
# PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(PROJECT_DIR, 'cryptocompare'))

insertquery = 'INSERT INTO public.coins ("IdCryptoCompare", "Name", "Symbol", "CoinName", "TotalCoinSupply", "SortOrder", "ProofType", "Algorithm", "ImageUrl")\n'
insertquery += 'VALUES \n('

cryptocomp = CryptoCompare()
data = cryptocomp.get_coin_list()
for key in data:
    if(not insertquery.endswith('(')):
        insertquery += ',\n('
    insertquery +=  data[key]['Id'] + ','
    insertquery += "'" + data[key]['Name'] + "',"
    insertquery += "'" + data[key]['Symbol'] + "',"
    insertquery += "'" + data[key]['CoinName'] + "',"
    insertquery += "'" + data[key]['TotalCoinSupply'] + "',"
    insertquery += data[key]['SortOrder'] + ','
    insertquery += "'" + data[key]['ProofType'] + "',"
    insertquery += "'" + data[key]['Algorithm'] + "',"
    if('ImageUrl' in data[key].keys()):
        insertquery += "'" + data[key]['ImageUrl'] + "'"
    else:
        insertquery += "''"
    insertquery += ')'
insertquery += ';'

dbconn = dbConnection()
dbconn.exexute_query(insertquery)

rows = dbconn.get_query_result('SELECT * FROM coins')
for row in rows:
    print("   ", row)





"""""
coins = ['BTC', 'ETH', 'XMR', 'NEO']
currencies = ['EUR', 'USD', 'GBP']

print('================== COIN LIST =====================')
print(cryptocompare.get_coin_list())
print(cryptocompare.get_coin_list(True))

print('===================== PRICE ======================')
print(cryptocompare.get_price(coins[0]))
print(cryptocompare.get_price(coins[1], curr='USD'))
print(cryptocompare.get_price(coins[2], curr=['EUR','USD','GBP']))
print(cryptocompare.get_price(coins[2], full=True))
print(cryptocompare.get_price(coins[0], curr='USD', full=True))
print(cryptocompare.get_price(coins[1], curr=['EUR','USD','GBP'], full=True))

print('==================================================')
print(cryptocompare.get_price(coins))
print(cryptocompare.get_price(coins, curr='USD'))
print(cryptocompare.get_price(coins, curr=['EUR','USD','GBP']))

print('==================== HIST PRICE ==================')
print(cryptocompare.get_historical_price(coins[0]))
print(cryptocompare.get_historical_price(coins[0], curr='USD'))
print(cryptocompare.get_historical_price(coins[1], curr=['EUR','USD','GBP']))
print(cryptocompare.get_historical_price(coins[1], 'USD',datetime.datetime.now()))
print(cryptocompare.get_historical_price(coins[2], ['EUR','USD','GBP'],time.time()))
"""""



