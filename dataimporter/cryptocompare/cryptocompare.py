import requests
import time
from config.config import Config
from ratelimit import rate_limited
import logging


class CryptoCompare:
    conf = None

    # region Params / Constructor

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

    # endregion

    # region Retrieve infos from CryptoCompare

    def get_coin_list(self, format_response=False):
        response = self.query_cryptocompare(self.URL_COIN_LIST, False)['Data']
        if format_response:
            return list(response.keys())
        else:
            return response

    @rate_limited(0.2)
    def get_socialstats(self, coin_id):
        return self.query_cryptocompare(self.URL_SOCIAL_STATS.format(coin_id))['Data']

    @rate_limited(0.04)
    def get_trading_pairs(self, symbol):
        url = self.URL_TRADING_PAIRS.format(symbol, self.MAX_TRADING_PAIRS_FOR_CRYPTO)
        data = self.query_cryptocompare(url)
        return self.__get_data_manage_errors(data, url)

    @rate_limited(0.1)
    def get_histo_hour_pair(self, symbol1, symbol2, limit):
        url = self.URL_HISTO_HOUR_PAIR.format(symbol1, symbol2, limit)
        data = self.query_cryptocompare(url)
        return self.__get_data_manage_errors(data, url)

    def __get_data_manage_errors(self, data, url):
        if data is not None:
            if 'Data' not in data.keys():
                time.sleep(5)
                data = self.query_cryptocompare(url)
            if 'Data' not in data.keys():
                return None
            return data['Data']
        else:
            return None

    # endregion

    # region Useless for the moment

    """""
    def get_historical_price(self, coin, timestamp=time.time()):
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp.timetuple())
        return self.query_cryptocompare(self.URL_HIST_PRICE.format(
        coin, self.format_parameter(self.CURR), int(timestamp)))

    def get_price(self, coin, full=False):
        if full:
            return self.query_cryptocompare(self.URL_PRICE_MULTI_FULL.format(self.format_parameter(coin),
                self.format_parameter(self.CURR)))
        if isinstance(coin, list):
            return self.query_cryptocompare(self.URL_PRICE_MULTI.format(self.format_parameter(coin),
                self.format_parameter(self.CURR)))
        else:
            return self.query_cryptocompare(self.URL_PRICE.format(coin, self.format_parameter(self.CURR)))
    """""

    # endregion

    # region Utils

    @staticmethod
    def query_cryptocompare(url, error_check=True):
        try:
            response = requests.get(url).json()
        except Exception as e:
            logging.error("Error getting information from cryptocompare. " + str(e))
            return None
        if error_check and 'Response' in response.keys() and response['Response'] != 'Success':
            logging.warning("[ERROR] " + response['Message'])
            return None
        return response

    @staticmethod
    def format_parameter(parameter):
        if isinstance(parameter, list):
            return ','.join(parameter)
        else:
            return parameter

    # endregion
