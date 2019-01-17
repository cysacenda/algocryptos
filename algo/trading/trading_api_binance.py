from commons.config import Config
from trading.trading_api import TradingApi, ORDER_BUY
from binance.client import Client
from binance.enums import *
from commons.dbaccess import DbConnection
from trading.alg_order import AlgOrderBinance
from commons.slack import slack
import logging
from trading.utils_trading import localize_utc_date
from datetime import timedelta


class TradingApiBinance(TradingApi):

    # override
    def __init__(self, param_pct_order_placed):
        conf = Config()
        self.param_pct_order_placed = param_pct_order_placed
        self.API_KEY = conf.get_config('binance', 'api_key')
        self.API_SECRET = conf.get_config('binance', 'api_secret')
        self.MAX_DIFF_DATE_HOUR = int(conf.get_config('trading_module_params', 'max_diff_date_hour'))
        self.client = Client(self.API_KEY, self.API_SECRET)  # lib python-binance
        self.precision = int(conf.get_config('binance', 'api_amount_precision'))

    # override
    def is_fake_api(self):
        return False

    # override
    def check_status_api(self):
        authorized_trading_pairs = []

        # test ping
        try:
            self.client.ping()
        except Exception as e:
            msg = "Error while trying to ping Binance API : " + str(e)
            logging.error(msg)
            slack.post_message_to_alert_error_trading(msg)
            return False, authorized_trading_pairs

        # Check system status
        try:
            status = self.client.get_system_status()
            if (status['msg'] == 'normal') and (status['status'] == 0):
                # Check account status
                status_client = self.client.get_account_status()
                if (status_client['msg'] == 'Normal') and (status_client['success']):
                    # Check account status related to trading
                    info_client = self.client.get_account()
                    if not info_client['canTrade']:
                        return False, authorized_trading_pairs
        except Exception as e:
            msg = "Error while trying to get system status from Binance API : " + str(e)
            logging.error(msg)
            slack.post_message_to_alert_error_trading(msg)
            return False, authorized_trading_pairs

        # Exchange info to verify which tradingpairs are tradable
        try:
            exchange_info = self.client.get_exchange_info()
            for symbol in exchange_info['symbols']:
                authorized_trading_pairs.append(symbol['symbol'])
        except Exception as e:
            msg = "Error while getting exchange info from binance : " + str(e)
            logging.error(msg)
            slack.post_message_to_alert_error_trading(msg)
            return False, authorized_trading_pairs

        return True, authorized_trading_pairs

    # override
    # allows to be sure that there is not to much time between predictions time and now
    def check_predictions_time_vs_server_time(self, dict_dates):
        tradable_trading_pairs = []

        # Get server time
        server_time = self.client.get_server_time()['serverTime']
        server_time_localized = localize_utc_date(server_time)

        logging.warning('server_time:' + str(server_time))
        logging.warning('server_time_localized:' + str(server_time_localized))

        for trading_pair, last_date in dict_dates.items():
            logging.warning('trading_pair diff (' + trading_pair + ')' + str(server_time_localized - last_date))
            if (server_time_localized - last_date) < timedelta(hours=self.MAX_DIFF_DATE_HOUR):
                tradable_trading_pairs.append(trading_pair)
            else:
                msg = 'Difference between server time (' + str(server_time_localized) + ') / prediction time (' + str(last_date) + ') too big for trading pair: *' + trading_pair + '*'
                logging.error(msg)
                slack.post_message_to_alert_error_trading(msg)

        return tradable_trading_pairs

    # override
    # TODO V2 : parameter = tradingpair directly
    # WARNING : can raise uncatched errors
    def get_price_ticker(self, base_asset, quote_asset, key):
        prices = self.client.get_all_tickers()
        prices_dict = {value["symbol"]: value["price"] for value in prices}
        return float(prices_dict[base_asset + quote_asset])

    # override
    # WARNING : can raise uncatched errors
    def get_buy_price(self, base_asset, quote_asset, key):
        buy_limit_price = 0
        depth = self.client.get_order_book(symbol=base_asset + quote_asset)
        if 'asks' in depth:
            ask_price = float(depth['asks'][0][0])  # get first ask price in order book
            buy_limit_price = ask_price + (ask_price * self.param_pct_order_placed)
        else:
            msg = 'Error while getting price for trading_pair:' + base_asset + quote_asset
            slack.post_message_to_alert_error_trading(msg)
            raise Exception(msg)
        return buy_limit_price

    # override
    def get_sell_price(self, base_asset, quote_asset, key):
        sell_limit_price = 0
        depth = self.client.get_order_book(symbol=base_asset + quote_asset)
        if 'bids' in depth:
            bid_price = float(depth['bids'][0][0])  # get first bid price in order book
            sell_limit_price = bid_price - (bid_price * self.param_pct_order_placed)
        else:
            msg = 'Error while getting price for trading_pair:' + base_asset + quote_asset
            slack.post_message_to_alert_error_trading(msg)
            raise Exception(msg)
        return sell_limit_price

    # override
    def get_available_amount_crypto(self, symbol):
        balance = 0
        infos_balance = self.client.get_asset_balance(asset=symbol)
        if 'free' in infos_balance:
            balance = float(infos_balance['free'])
        else:
            msg = 'Error while getting balance for symbol:' + symbol
            slack.post_message_to_alert_error_trading(msg)
            raise Exception(msg)
        return balance

    # override
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
    def create_order(self, base_asset, quote_asset, side, quantity_from, key):  # ex: USDT, ETH, 1000, BUY
        order = {}
        try:
            # TODO V2 : Use stopPrice for stop loss genre -3-4% ?
            if side == ORDER_BUY:
                limit_price = self.get_buy_price(base_asset, quote_asset, key)
                # order = self.client.order_limit_buy(
                #     symbol=base_asset + quote_asset,
                #     quantity=quantity_from,
                #     price=self.format_amount_order(limit_price))
                # TODO [SIMULATION] : To be replaced with real order !
                order = self.client.create_test_order(
                    symbol=base_asset + quote_asset,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity_from,
                    price=self.format_amount_order(limit_price))
            else:
                limit_price = self.get_sell_price(base_asset, quote_asset, key)
                # order = self.client.order_limit_sell(
                #     symbol=base_asset + quote_asset,
                #     quantity=quantity_from,
                #     price=self.format_amount_order(limit_price))
                # TODO [SIMULATION] : To be replaced with real order !
                order = self.client.create_test_order(
                    symbol=base_asset + quote_asset,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity_from,
                    price=self.format_amount_order(limit_price))
            msg = 'Order placed (' + str(side) + ') on trading_pair: ' + base_asset + quote_asset + ' - Qty: ' + str(quantity_from) + ' - limit: ' + str(limit_price) + ' - order: ' + str(order)
            logging.warning(msg)
            slack.post_message_to_alert_actions_trading(msg)

            # Save order into DB
            dbconn = DbConnection()
            dbconn.exexute_query(TradingApiBinance.__create_query_order(order))
        except Exception as e:
            msg = "Error while creating order on tradingPair: {}, side: {}, qty:{}"
            logging.error(msg.format(base_asset + quote_asset, side, quantity_from))
            logging.error(str(e))
            slack.post_message_to_alert_error_trading(msg.format(base_asset + quote_asset, side, quantity_from) + '\n' + str(e))
            raise Exception(msg + str(e))

        return order['orderId']

    @staticmethod
    def __create_query_order(order):
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
    def get_order(self, id_order, trading_pair):
        order = self.client.get_order(
            symbol=trading_pair,
            orderId=id_order)
        return AlgOrderBinance(order)

    # override
    def get_orders(self):
        # Useless her, only for backtesting
        return 'N/A'

    # override
    def cancel_open_orders(self):
        orders = self.client.get_open_orders()
        logging.warning("Open orders to be cancelled " + str(orders))
        for order in orders:
            try:
                result = self.client.cancel_order(
                    symbol=order['symbol'],
                    orderId=order['orderId'])
                msg = 'Order cancelled: ' + str(result)
                logging.warning(msg)
                slack.post_message_to_alert_actions_trading(msg)
            except Exception as e:
                msg = "Order cannot be cancelled " + str(e)
                logging.error(msg)
                slack.post_message_to_alert_error_trading(msg)

    def format_amount_order(self, amount):
        return "{:0.0{}f}".format(amount, self.precision)
