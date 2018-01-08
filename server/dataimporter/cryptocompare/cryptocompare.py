import requests
import time
import datetime
from config.config import Config

class CryptoCompare:
    conf = None

    # Cryptocompare params
    URL_COIN_LIST = None
    URL_PRICE = None
    URL_HIST_PRICE = None
    URL_SOCIAL_STATS = None
    CURR = None

    def __init__(self):
        self.conf = Config()

        # API urls
        self.URL_COIN_LIST = self.conf.get_config('cryptocompare_params', 'url_coin_list')
        self.URL_PRICE = self.conf.get_config('cryptocompare_params', 'url_price')
        self.URL_HIST_PRICE = self.conf.get_config('cryptocompare_params', 'url_hist_price')
        self.URL_SOCIAL_STATS = self.conf.get_config('cryptocompare_params', 'url_social_stats')

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

    # TODO: add option to filter json response according to a list of fields
    def get_price(self, coin, full=False):
        if full:
            return self.query_cryptocompare(self.URL_PRICE_MULTI_FULL.format(self.format_parameter(coin),
                self.format_parameter(self.CURR)))
        if isinstance(coin, list):
            return self.query_cryptocompare(self.URL_PRICE_MULTI.format(self.format_parameter(coin),
                self.format_parameter(self.CURR)))
        else:
            return self.query_cryptocompare(self.URL_PRICE.format(coin, self.format_parameter(self.CURR)))

    def get_historical_price(self, coin, timestamp=time.time()):
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp.timetuple())
        return self.query_cryptocompare(self.URL_HIST_PRICE.format(coin, self.format_parameter(self.CURR), int(timestamp)))

    def get_socialstats(self, coin_id):
        return self.query_cryptocompare(self.URL_SOCIAL_STATS.format(coin_id))['Data']
