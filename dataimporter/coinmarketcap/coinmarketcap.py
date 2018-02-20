import requests
import logging
from commons.config import Config


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
