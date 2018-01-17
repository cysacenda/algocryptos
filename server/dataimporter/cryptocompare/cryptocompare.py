import requests
import time
import datetime
from config.config import Config
from ratelimit import rate_limited

class CryptoCompare:
    conf = None

    # Cryptocompare params
    URL_COIN_LIST = None
    URL_PRICE = None
    URL_HIST_PRICE = None
    URL_SOCIAL_STATS = None
    URL_TRADING_PAIRS = None
    URL_HISTO_HOUR_PAIR = None
    CURR = None
    MAX_TRADING_PAIRS_FOR_CRYPTO = None

    def __init__(self):
        self.conf = Config()

        # API urls
        self.URL_COIN_LIST = self.conf.get_config('cryptocompare_params', 'url_coin_list')
        self.URL_PRICE = self.conf.get_config('cryptocompare_params', 'url_price')
        self.URL_HIST_PRICE = self.conf.get_config('cryptocompare_params', 'url_hist_price')
        self.URL_SOCIAL_STATS = self.conf.get_config('cryptocompare_params', 'url_social_stats')
        self.URL_TRADING_PAIRS = self.conf.get_config('cryptocompare_params', 'url_trading_pairs')
        self.MAX_TRADING_PAIRS_FOR_CRYPTO = self.conf.get_config('cryptocompare_params', 'max_trading_pairs_for_crypto')
        self.URL_HISTO_HOUR_PAIR = self.conf.get_config('cryptocompare_params', 'url_histo_hour_pair')

        # DEFAULTS
        self.CURR = self.conf.get_config('cryptocompare_params', 'default_currency')

    def query_cryptocompare(self, url,errorCheck=True):
        try:
            response = requests.get(url).json()
        except Exception as e:
            print('Error getting information from cryptocompare. %s' % str(e))
            return None
        if errorCheck and 'Response' in response.keys() and response['Response'] != 'Success':
            print('[ERROR] %s' % response['Message'])
            return None
        return response

    def format_parameter(self, parameter):
        if isinstance(parameter, list):
            return ','.join(parameter)
        else:
            return parameter

    ###############################################################################

    def get_coin_list(self, format=False):
        response = self.query_cryptocompare(self.URL_COIN_LIST, False)['Data']
        if format:
            return list(response.keys())
        else:
            return response

    @rate_limited(0.2)
    def get_socialstats(self, coin_id):
        return self.query_cryptocompare(self.URL_SOCIAL_STATS.format(coin_id))['Data']

    @rate_limited(0.02)
    def get_trading_pairs(self, symbol):
        url = self.URL_TRADING_PAIRS.format(symbol, self.MAX_TRADING_PAIRS_FOR_CRYPTO)
        data = self.query_cryptocompare(url)

        # retry if needed - TODO : Replace with something proper
        if('Data' not in data.keys()):
            time.sleep(5)
            data = self.query_cryptocompare(url)
        return data['Data']

    @rate_limited(0.08)
    def get_histo_hour_pair(self, symbol1, symbol2, limit):
        url = self.URL_HISTO_HOUR_PAIR.format(symbol1, symbol2, limit)
        data = self.query_cryptocompare(url)

        # retry if needed - TODO : Replace with something proper
        if ('Data' not in data.keys()):
            time.sleep(5)
            data = self.query_cryptocompare(url)
        return data['Data']




    def get_historical_price(self, coin, timestamp=time.time()):
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp.timetuple())
        return self.query_cryptocompare(self.URL_HIST_PRICE.format(coin, self.format_parameter(self.CURR), int(timestamp)))

    def get_price(self, coin, full=False):
        if full:
            return self.query_cryptocompare(self.URL_PRICE_MULTI_FULL.format(self.format_parameter(coin),
                self.format_parameter(self.CURR)))
        if isinstance(coin, list):
            return self.query_cryptocompare(self.URL_PRICE_MULTI.format(self.format_parameter(coin),
                self.format_parameter(self.CURR)))
        else:
            return self.query_cryptocompare(self.URL_PRICE.format(coin, self.format_parameter(self.CURR)))



""""" EXEMPLES A SUPPRIMER
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