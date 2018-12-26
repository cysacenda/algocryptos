from commons.config import Config
from trading.trading_api import TradingApi, ORDER_SELL, ORDER_BUY
from binance.client import Client
from commons.dbaccess import DbConnection
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

import logging

# https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
# TODO : Manage Binance Errors (cf. debut fichier)
# Look at orderTypes="STOP_LOSS_LIMIT"
# Infos utiles:
# https://api.binance.com/api/v1/exchangeInfo

class TradingApiBinance(TradingApi):
    # override
    def __init__(self, param_pct_order_placed):
        conf = Config()
        self.param_pct_order_placed = param_pct_order_placed
        self.API_KEY = conf.get_config('binance', 'api_key')
        self.API_SECRET = conf.get_config('binance', 'api_secret')
        self.client = Client(self.api_key, self.api_secret) # lib python-binance
        self.precision = 5  # binance api precision for amount

    def is_simulation(self):
        return False

    # override
    def check_status_api(self):
        global_status = False
        authorized_trading_pairs = []

        try:
            # test ping
            self.client.ping()
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

        except Exception as e:
            logging.error("TradingApiBinance.check_status_api() - Can't check status: " + str(e))
            print(e)

        return global_status, authorized_trading_pairs

    # override
    # TODO : parameter = tradingpair directly
    def get_price_ticker(self, base_asset, quote_asset, key):
        prices = self.client.get_all_tickers()
        prices_dict = {value["symbol"]: value["price"] for value in prices}
        return float(prices_dict[base_asset + quote_asset])

    # override
    def get_buy_price(self, base_asset, quote_asset, key):
        buy_limit_price = 0
        depth = self.client.get_order_book(symbol=base_asset + quote_asset)
        if 'asks' in depth:
            ask_price = float(depth['asks'][0][0])  # get first ask price in order book
            buy_limit_price = ask_price + (ask_price * self.param_pct_order_placed)
        else:
            raise Exception('Error while getting price in get_buy_price() for trading_pair:' + base_asset + quote_asset)
        return buy_limit_price

    # override
    def get_sell_price(self, base_asset, quote_asset, key):
        sell_limit_price = 0
        depth = self.client.get_order_book(symbol=base_asset + quote_asset)
        if 'bids' in depth:
            bid_price = float(depth['bids'][0][0])  # get first bid price in order book
            sell_limit_price = bid_price - (bid_price * self.param_pct_order_placed)
        else:
            raise Exception('Error while getting price in get_sell_price() for trading_pair:' + base_asset + quote_asset)
        return sell_limit_price

    # override
    def get_available_amount_crypto(self, symbol):
        balance = 0
        infos_balance = self.client.get_asset_balance(asset=symbol)
        if 'free' in infos_balance:
            balance = float(balance['free'])
        else:
            raise Exception('Error while getting balance in get_available_amount_crypto() for symbol:' + symbol)
        return balance

    # override
    def create_order(self, base_asset, quote_asset, side, quantity_from, key):  # ex: USDT, ETH, 1000, BUY
        order = {}
        try:
            # TODO : Use stopPrice for stop loss genre -3-4% ?
            if side == ORDER_BUY:
                limit_price = self.get_buy_price(base_asset, quote_asset, key)
                order = self.client.order_limit_buy(
                    symbol=base_asset + quote_asset,
                    quantity=quantity_from,
                    price=self.format_amount_order(limit_price))
            else:
                limit_price = self.get_sell_price(base_asset, quote_asset, key)
                order = self.client.order_limit_sell(
                    symbol=base_asset + quote_asset,
                    quantity=quantity_from,
                    price=self.format_amount_order(limit_price))
            logging.warning("TradingApiBinance.create_order() - Order placed " + str(order))

            # Save order into DB
            dbconn = DbConnection()
            dbconn.exexute_query(self.__create_query_order(order))
        except Exception as e:
            msg = "TradingApiBinance.create_order() - Error while creating order on tradingPair: {}, side: {}, qty:{}"
            logging.error(msg.format(base_asset + quote_asset, side, quantity_from))
            logging.error(str(e))

        # TODO : Store in database
        # RESULT of order:
        # {'symbol': 'VETUSDT',
        # 'orderId': 9358183,
        # 'clientOrderId': 'ILNyxOioi7cPBDGkQSKtbH',
        # 'transactTime': 1545235888618,
        # 'price': '0.00550000',
        # 'origQty': '5000.00000000',
        # 'executedQty': '0.00000000',
        # 'cummulativeQuoteQty': '0.00000000',
        # 'status': 'NEW',
        # 'timeInForce': 'GTC',
        # 'type': 'LIMIT',
        # 'side': 'SELL',
        # 'fills': []}
        return order['orderId']

    # TODO: Ajouter timestamp auto dans la table
    def __create_query_order(self, order):
        insertquery = 'INSERT INTO public.orders (orderId, symbol, clientOrderId, transactTime, price, origQty,' \
                      'executedQty, cummulativeQuoteQty, status, timeInForce, typeorder, side, fills)'
        insertquery += ' VALUES('
        insertquery += str(order['orderId']) + ', '
        insertquery += "'" + order['symbol'] + "', "
        insertquery += "'" + order['clientOrderId'] + "', "
        insertquery += str(order['transactTime']) + ', '
        insertquery += str(order['price']) + ', '
        insertquery += str(order['origQty']) + ', '
        insertquery += str(order['executedQty']) + ', '
        insertquery += str(order['cummulativeQuoteQty']) + ', '
        insertquery += "'" + order['status'] + "', "
        insertquery += "'" + order['timeInForce'] + "', "
        insertquery += "'" + order['type'] + "', "
        insertquery += "'" + order['side'] + "', "
        insertquery += "'" + str(order['fills']) + "')"
        return insertquery


    # override
    def get_order(self, id_order, trading_pair):
        order = self.client.get_order(
            symbol=trading_pair,
            orderId=id_order)

        # Match with object AlgOrder (?)
        # {'symbol': 'VETUSDT',
        #  'origClientOrderId': 'ILNyxOioi7cPBDGkQSKtbH',
        #  'orderId': 9358183,
        #  'clientOrderId': '4ZPYz4mDfcTg6Ho0O1QhoA',
        #  'price': '0.00550000',
        #  'origQty': '5000.00000000',
        #  'executedQty': '0.00000000',
        #  'cummulativeQuoteQty': '0.00000000',
        #  'status': 'CANCELED',
        #  'timeInForce': 'GTC',
        #  'type': 'LIMIT',
        #  'side': 'SELL'}

        return 'todo'

    # override
    def get_orders(self):
        # Not useful for the moment (only for backtesting)
        return 'N/A'

    # override
    def cancel_open_orders(self):
        # TODO : Logging ce qu'on cancel, partiellement executé, etc.
        orders = self.client.get_open_orders()
        for order in orders:
            result = self.client.cancel_order(
                symbol=order['symbol'],
                orderId=order['orderId'])

    def format_amount_order(self, amount):
        return "{:0.0{}f}".format(amount, self.precision)