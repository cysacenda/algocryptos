import extractdata

#TODO : Add Ids au lieu d'utiliser les symbols comme PK (doublons)

# -----------------------------------------------
# Get coin list from Cryptocompare and insert in BDD
# -----------------------------------------------

#extractdata.extract_crytopcompare_coins()

# -----------------------------------------------
# Insert current prices into BDD
# -----------------------------------------------

#extractdata.extract_coinmarketcap_prices()

# -----------------------------------------------
# Delete coins and prices that are judged useless (market cap to low, no match between CMC & Cryptocompare names)
# -----------------------------------------------

#extractdata.remove_useless_prices_coins()
#extractdata.add_ids()


# -----------------------------------------------
# Social stats from Cryptocompare (replace with orginal website info post MVP ?)
# -----------------------------------------------
#extractdata.extract_cryptocompare_social()

# Lib reddit
# https://github.com/praw-dev/praw
#
extractdata.import_Reddit_data()


# -----------------------------------------------
# Social stats from Google trends
# -----------------------------------------------


# -----------------------------------------------
# Insert OHLCV into BDD
# -----------------------------------------------

# -----------------------------------------------
# SocialStats Cryptocompare pour avoir les adresses des twitter, etc.
# -----------------------------------------------

# -----------------------------------------------
# Reddit directement (60 call max / sec)
# -----------------------------------------------

# -----------------------------------------------
# Twitter directement
# -----------------------------------------------

# -----------------------------------------------
# Github directement ou cryptocompare ?
# -----------------------------------------------


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



