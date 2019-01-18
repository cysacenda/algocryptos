import requests
import time
from commons.config import Config
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
    URL_HISTO_DAY_PAIR = None
    CURR = None

    def __init__(self):
        self.conf = Config()

        # API Key
        self.API_KEY = self.conf.get_config('cryptocompare_params', 'api_key_cryptocompare')
        self.HEADERS = {
            "authorization": "Apikey " + self.API_KEY
        }

        # API urls
        self.URL_COIN_LIST = self.conf.get_config('cryptocompare_params', 'url_coin_list')
        self.URL_PRICE = self.conf.get_config('cryptocompare_params', 'url_price')
        self.URL_HIST_PRICE = self.conf.get_config('cryptocompare_params', 'url_hist_price')
        self.URL_SOCIAL_STATS = self.conf.get_config('cryptocompare_params', 'url_social_stats')
        self.URL_TRADING_PAIRS = self.conf.get_config('cryptocompare_params', 'url_trading_pairs')
        self.URL_HISTO_HOUR_PAIR = self.conf.get_config('cryptocompare_params', 'url_histo_hour_pair')
        self.URL_HISTO_DAY_PAIR = self.conf.get_config('cryptocompare_params', 'url_histo_day_pair')

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

    @rate_limited(4, 1)
    def get_socialstats(self, coin_id):
        return self.query_cryptocompare(self.URL_SOCIAL_STATS.format(coin_id))['Data']

    @rate_limited(5, 1)
    def get_trading_pairs(self, symbol, max_trading_pairs):
        url = self.URL_TRADING_PAIRS.format(symbol, max_trading_pairs)
        data = self.query_cryptocompare(url)
        return self.__get_data_manage_errors(data, url)

    @rate_limited(5, 1)
    def get_histo_hour_pair(self, symbol1, symbol2, limit):
        if limit > 2000:
            limit = 2000
        url = self.URL_HISTO_HOUR_PAIR.format(symbol1, symbol2, limit)
        data = self.query_cryptocompare(url)
        return self.__get_data_manage_errors(data, url)

    @rate_limited(7, 1)
    def get_histo_day_pair(self, symbol1):
        url = self.URL_HISTO_DAY_PAIR.format(symbol1, self.CURR, 2000)
        data = self.query_cryptocompare(url, False, False)
        return data.content

    def __get_data_manage_errors(self, data, url):
        if data is None:
            time.sleep(10)
            data = self.query_cryptocompare(url)
        if data is None:
            return None
        if 'Data' not in data.keys():
            time.sleep(5)
            data = self.query_cryptocompare(url)
        if 'Data' not in data.keys():
            return None
        return data['Data']

    # endregion

    # region Utils

    def query_cryptocompare(self, url, error_check=True, json_format=True):
        try:
            response = requests.get(url, self.HEADERS)
            if json_format:
                response = response.json()
        except Exception as e:
            logging.error("Error getting information from cryptocompare. " + str(e))
            return None
        if error_check and 'Response' in response.keys() and response['Response'] != 'Success':
            logging.warning(response['Message'] + ' | url=' + url)
            return None
        return response

    @staticmethod
    def format_parameter(parameter):
        if isinstance(parameter, list):
            return ','.join(parameter)
        else:
            return parameter

    # endregion
