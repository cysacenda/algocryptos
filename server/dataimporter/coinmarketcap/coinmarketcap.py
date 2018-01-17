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

###############################################################################


class CoinMarketCap:

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

    ###############################################################################

    def get_price_list(self, format=False):
        response = self.query_coinmarketcap(URL_PRICE_LIST, False)
        if format:
            return list(response.keys())
        else:
            return response

"""""
    def get_price(self, coin, curr=CURR, full=False):
        if full:
            return self.query_cryptocompare(URL_PRICE_MULTI_FULL.format(self.format_parameter(coin),
                self.format_parameter(curr)))
        if isinstance(coin, list):
            return self.query_cryptocompare(URL_PRICE_MULTI.format(self.format_parameter(coin),
                self.format_parameter(curr)))
        else:
            return self.query_cryptocompare(URL_PRICE.format(coin, self.format_parameter(curr)))

    def get_historical_price(self, coin, curr=CURR, timestamp=time.time()):
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp.timetuple())
        return self.query_cryptocompare(URL_HIST_PRICE.format(coin, self.format_parameter(curr), int(timestamp)))
"""""