from trading.trading_api import ORDER_BUY, ORDER_SELL
import logging
from commons.slack import slack


class TradingModule:
    def __init__(self, trading_api, param_bet_size, param_min_bet_size, param_pct_order_placed,
                 param_nb_periods_to_hold_position, trading_pairs, cash_asset, thresholds, trace):

        logging.warning("TradingModule - START")

        self.x_buy = {}
        self.y_buy = {}
        self.x_sell = {}
        self.y_sell = {}
        self.amount_x = []
        self.amount_y = []

        self.trading_api = trading_api
        self.trading_pairs = trading_pairs
        self.cash_asset = cash_asset
        self.thresholds = thresholds
        self.trace = trace

        self.param_nb_periods_to_hold_position = param_nb_periods_to_hold_position
        self.param_min_bet_size = param_min_bet_size
        self.param_pct_order_placed = param_pct_order_placed
        # TODO : V2 - Faire en fonction de la valeur du portefeuille
        self.param_bet_size = param_bet_size

        self.init_var()

        logging.warning("TradingModule - END")

    def init_var(self):
        for trading_pair, value in self.trading_pairs.items():
            self.x_buy[trading_pair] = []
            self.y_buy[trading_pair] = []
            self.x_sell[trading_pair] = []
            self.y_sell[trading_pair] = []

    def is_simulation(self):
        return self.trading_api.is_simulation()

    def __can_buy(self):
        return self.trading_api.get_available_amount_crypto(self.cash_asset) >= self.param_min_bet_size

    def __what_to_buy(self, current_date, signals):
        what_to_buy = {}
        max_prob = 0
        max_trading_pair = ''
        if self.__can_buy():
            for trading_pair, trading_pair_probs in signals.items():
                last_prob = trading_pair_probs.tail(1).signal_prob[0]
                if last_prob > max_prob:
                    max_prob = last_prob
                    max_trading_pair = trading_pair

        # max proba identified and > threshold for the trading pair
        if (max_trading_pair != '') and (max_prob > self.thresholds[max_trading_pair]):
            amount_cash_available = self.trading_api.get_available_amount_crypto(self.cash_asset)
            if amount_cash_available > self.param_min_bet_size:
                cash_amount_to_use = amount_cash_available * self.param_bet_size
                what_to_buy[self.trading_pairs[max_trading_pair]] = cash_amount_to_use

        return what_to_buy

    # TODO : V2 - Change bet size regarding proba ?
    def __buy(self, key, trading_pair, amount):
        id_order = self.trading_api.create_order(trading_pair.base_asset, trading_pair.quote_asset, ORDER_BUY, amount,
                                                 key)
        order = self.trading_api.get_order(id_order, trading_pair.name)

        # trace
        if self.trace and self.is_simulation():
            print(
                '[BUY] ORDER PLACED (' + str(key) + '): ' + str(order.quantity_base) + ' ' + order.base_asset + ' for '
                + str(order.quantity_quote) + '$ (close_price = ' + str(round(order.price, 2))
                + '$ / fees = ' + str(round(order.fees_quote_asset, 2)) + ')')

        self.x_buy[trading_pair.name].append(key)
        self.y_buy[trading_pair.name].append(order.price)

    def __what_to_sell(self, current_date, signals):
        what_to_sell = {}
        for trading_pair, value in self.trading_pairs.items():
            if signals[trading_pair].signal_prob.max() < self.thresholds[trading_pair]:
                # if crypto currently in portfolio and value > min_bet_value
                crypto_amount = self.trading_api.get_available_amount_crypto(value.base_asset)
                crypto_amount_cash_value = self.trading_api.get_price_ticker(value.base_asset, value.quote_asset) * crypto_amount
                if (crypto_amount > 0) and (crypto_amount_cash_value > self.param_min_bet_size):
                    what_to_sell[value] = crypto_amount
        return what_to_sell

    def __sell(self, key, trading_pair, crypto_amount):
        id_order = self.trading_api.create_order(trading_pair.base_asset, trading_pair.quote_asset, ORDER_SELL,
                                                 crypto_amount, key)
        order = self.trading_api.get_order(id_order, trading_pair.name)

        if self.trace and self.is_simulation():
            print(
                '[SELL] ORDER PLACED (' + str(key) + '): ' + str(order.quantity_base) + ' ' + order.base_asset + ' for '
                + str(order.quantity_quote) + '$ (close_price = ' + str(round(order.price, 2))
                + '$ / fees = ' + str(round(order.fees_quote_asset, 2)) + ')')

        self.x_sell[trading_pair.name].append(key)
        self.y_sell[trading_pair.name].append(order.price)

    def do_sell_all(self, key):
        for trading_pair, value in self.trading_pairs.items():
            amount_available = self.trading_api.get_available_amount_crypto(value.base_asset)
            crypto_amount_cash_value = self.trading_api.get_price_ticker(value.base_asset,
                                                                         value.quote_asset) * amount_available
            if (amount_available > 0) and (crypto_amount_cash_value > self.param_min_bet_size):
                self.__sell(key, value, amount_available)

    # check & perform actions that need to be done (buy / sell) at a specific date
    def do_update(self, key, signals, dict_dates):
        self.do_logging_warning("Start")

        # cancel open orders
        self.trading_api.cancel_open_orders()

        # check api status
        status, authorized_trading_pairs = self.trading_api.check_status_api()

        # check dates prediction vs server time (can sell if data not up to date, but not buy
        tradable_trading_pairs = self.trading_api.check_predictions_time_vs_server_time(dict_dates)

        if status:
            # sell
            for trading_pair, amount in self.__what_to_sell(key, signals).items():
                if (trading_pair.name in authorized_trading_pairs) or self.is_simulation():
                    self.__sell(key, trading_pair, amount)
                else:
                    msg = 'Error: TradingPair not authorized for trading: ' + trading_pair.name
                    logging.error(msg)
                    slack.post_message_to_alert_error_trading(msg)
            for trading_pair, amount in self.__what_to_buy(key, signals).items():
                if ((trading_pair.name in authorized_trading_pairs)
                        and (trading_pair.name in tradable_trading_pairs)) or self.is_simulation():
                    self.__buy(key, trading_pair, amount)
                else:
                    msg = ''
                    if trading_pair.name not in authorized_trading_pairs:
                        msg += 'Error: TradingPair not authorized for trading: ' + trading_pair.name + ' / '
                    if trading_pair.name not in tradable_trading_pairs:
                        msg += "Error: TradingPair can't be traded because of last prediction date vs server time: " + trading_pair.name
                    logging.error(msg)
                    slack.post_message_to_alert_error_trading(msg)

            self.amount_x.append(key)
            self.amount_y.append(self.trading_api.get_portfolio_value(self.trading_pairs, self.cash_asset, key))

        # Post portfolio value to Slack
        if not self.is_simulation():
            portfolio_amount = self.trading_api.get_portfolio_value(self.trading_pairs, self.cash_asset, key)
            slack.post_message_to_alert_portfolio('Portfolio value: ' + str(portfolio_amount) + ' ' + self.cash_asset)

        self.do_logging_warning("End")

    def get_available_amount_crypto(self, symbol):
        return self.trading_api.get_available_amount_crypto(symbol)

    def get_all_fees_paid(self):
        fees = 0
        for key, order in self.trading_api.get_orders().items():
            fees = fees + order.fees_quote_asset
        return fees

    def get_nb_transactions_done(self):
        return len(self.trading_api.get_orders())

    def get_signals(self):
        return self.x_buy, self.y_buy, self.x_sell, self.y_sell, self.amount_x, self.amount_y

    # logging warning only when not simulation
    def do_logging_warning(self, message):
        if not self.is_simulation():
            logging.warning(message)
