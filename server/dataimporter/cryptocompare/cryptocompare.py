import requests
import time
import datetime

# API
URL_COIN_LIST = 'https://www.cryptocompare.com/api/data/coinlist/'
URL_PRICE = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'
URL_PRICE_MULTI = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'
URL_PRICE_MULTI_FULL = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}'
URL_HIST_PRICE = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym={}&tsyms={}&ts={}'
URL_AVG = 'https://min-api.cryptocompare.com/data/generateAvg?fsym={}&tsym={}&markets={}'
URL_SOCIAL_STATS = 'https://www.cryptocompare.com/api/data/socialstats/?id={}'

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


class CryptoCompare:

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
        response = self.query_cryptocompare(URL_COIN_LIST, False)['Data']
        if format:
            return list(response.keys())
        else:
            return response

    # TODO: add option to filter json response according to a list of fields
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

    def get_socialstats(self, coin_id):
        return self.query_cryptocompare(URL_SOCIAL_STATS.format(coin_id))['Data']
