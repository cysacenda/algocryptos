from commons.config import Config
from trading.trading_api import TradingApi
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

class TradingApiBinance(TradingApi):
    # override
    def __init__(self):
        conf = Config()
        self.API_KEY = conf.get_config('binance', 'api_key')
        self.API_SECRET = conf.get_config('binance', 'api_secret')
        self.client = Client(self.api_key, self.api_secret) # python-binance

    # override
    def check_status_api(self):
        global_status = False
        authorized_trading_pairs = []

        try:
            # test ping
            ping_status = self.client.ping()
            # Check system status
            status = self.client.get_system_status()
            if (status['msg'] == 'normal') and (status['status'] == 0):
                # Check account status
                status_client = self.client.get_account_status()
                if (status_client['msg'] == 'Normal') and (status_client['success'] == True):
                    # Check account status related to trading
                    info_client = self.client.get_account()
                    if info_client['canTrade'] == True:
                        global_status = True
            # Exchange info to verify which tradingpairs are tradable
            exchange_info = self.client.get_exchange_info()
            for symbol in exchange_info['symbols']:
                authorized_trading_pairs.append(symbol['symbol'])

        except BinanceRequestException as e:
            # TODO
            print(e)
        except BinanceAPIException as e:
            # TODO
            print(e)
        except Exception as e:
            # TODO
            print(e)

        return global_status, authorized_trading_pairs

    # override: return current price of asset (cf. trading pair)
    def get_price(self, base_asset, quote_asset, key):
        return todo

    # override
    def get_available_amount_crypto(self, symbol):
        return todo

    # override
    def get_portfolio_value(self, trading_pairs, cash_asset, key):
        return todo

    # market for the moment => to be scheduled with like market minus 0.5%
    # override
    def create_order(self, base_asset, quote_asset, side, quantity_from, key):  # ex: USDT, ETH, 1000, BUY
        todo = 0

    # override
    def get_order(self, id_order):
        return todo

    # override
    def get_orders(self):
        return todo

    # override
    def cancel_open_orders(self):
        return todo