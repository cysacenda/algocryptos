import requests
import logging
from config.config import Config


class CoinMarketCap:
    conf = None
    URL_PRICE_LIST = None

    def __init__(self):
        self.conf = Config()

        # API urls
        self.URL_PRICE_LIST = self.conf.get_config('cmc_params', 'url_prices')

    # region Get prices

    def get_price_list(self, format_response=False):
        response = self.query_coinmarketcap(self.URL_PRICE_LIST, False)
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
            logging.warning("[WARNING] " + response['Message'])
            return None
        return response

    @staticmethod
    def format_parameter(parameter):
        if isinstance(parameter, list):
            return ','.join(parameter)
        else:
            return parameter

    # endregion
