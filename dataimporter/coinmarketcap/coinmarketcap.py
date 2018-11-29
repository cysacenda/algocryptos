import requests
import logging
from commons.config import Config
import pandas as pd
import time, requests, json


class CoinMarketCap:
    conf = None
    URL_PRICE_LIST = None
    URL_GLOBAL_DATA = None

    def __init__(self):
        self.conf = Config()

        # API urls
        self.URL_PRICE_LIST = self.conf.get_config('cmc_params', 'url_prices')
        self.URL_GLOBAL_DATA = self.conf.get_config('cmc_params', 'url_global_data')

    # region Get prices

    def get_price_list(self, format_response=False):
        response = self.query_coinmarketcap(self.URL_PRICE_LIST, False)
        if format_response:
            return list(response.keys())
        else:
            return response

    # endregion

    # region Get global data

    def get_global_data(self, format_response=False):
        response = self.query_coinmarketcap(self.URL_GLOBAL_DATA, False)
        if format_response:
            return list(response.keys())
        else:
            return response

    # endregion

    # region Utils

    @staticmethod
    def query_coinmarketcap(url, error_check=True):
        try:
            response = requests.get(url).json()
        except Exception as e:
            logging.error("Error getting prices information from CMC. " + str(e))
            return None
        if error_check and 'Response' in response.keys():
            logging.warning(response['Message'])
            return None
        return response

    @staticmethod
    def format_parameter(parameter):
        if isinstance(parameter, list):
            return ','.join(parameter)
        else:
            return parameter

    # endregion


class CoinMarketCapNew:
    conf = None
    URL_PRICE_LIST = None
    API_KEY = None

    def __init__(self):
        self.conf = Config()

        # API urls
        self.URL_PRICE_LIST = self.conf.get_config('cmc_params_new', 'url_prices')
        self.API_KEY = self.conf.get_config('cmc_params_new', 'api_key')

    # region Get prices
    def get_price_list(self):
        return self.get_dataframe_from_response(self.URL_PRICE_LIST)

    def get_dataframe_from_response(self, url):
        df = pd.DataFrame()
        try:
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'deflate, gzip',
                'X-CMC_PRO_API_KEY': self.API_KEY,
            }
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                response = json.loads(r.text)
                df = pd.DataFrame(response['data'])
            else:
                logging.error("Error getting prices information from CMC. Response status_code= " + str(r.status_code))
                logging.error("Message= " + str(r.text))
        except Exception as e:
            logging.error("Error getting prices information from CMC. " + str(e))
        return df

    # endregion