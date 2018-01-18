import requests

# API
URL_PRICE_LIST = 'https://api.coinmarketcap.com/v1/ticker/?limit=0'

# FIELDS
PRICE = 'PRICE'
HIGH = 'HIGH24HOUR'
LOW = 'LOW24HOUR'
VOLUME = 'VOLUME24HOUR'
CHANGE = 'CHANGE24HOUR'
CHANGE_PERCENT = 'CHANGEPCT24HOUR'
MARKETCAP = 'MKTCAP'

# DEFAULTS
CURR = 'USD'

class CoinMarketCap:

    # region Get prices

    def get_price_list(self, format=False):
        response = self.query_coinmarketcap(URL_PRICE_LIST, False)
        if format:
            return list(response.keys())
        else:
            return response

    # endregion

    # region Utils

    def query_coinmarketcap(self, url,errorCheck=True):
        try:
            response = requests.get(url).json()
        except Exception as e:
            print('Error getting prices information from CMC. %s' % str(e))
            return None
        if errorCheck and 'Response' in response.keys():
            print('[ERROR] %s' % response['Message'])
            return None
        return response

    def format_parameter(self, parameter):
        if isinstance(parameter, list):
            return ','.join(parameter)
        else:
            return parameter

    # endregion
