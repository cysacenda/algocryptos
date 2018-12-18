from trading.trading_api import ORDER_BUY, ORDER_SELL

class TradingModule:
    def __init__(self, trading_api, param_bet_size, param_min_bet_size, trading_pairs, cash_asset, thresholds, trace):
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

        self.nb_periods_to_hold_position = 24  # 1d => TODO : sell must be done if pct_change model touched / check close price
        self.param_bet_size = param_bet_size
        self.param_min_bet_size = param_min_bet_size

        self.init_var()

    def init_var(self):
        for trading_pair, value in self.trading_pairs.items():
            self.x_buy[trading_pair] = []
            self.y_buy[trading_pair] = []
            self.x_sell[trading_pair] = []
            self.y_sell[trading_pair] = []

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
            cash_amount_to_use = self.trading_api.get_available_amount_crypto(self.cash_asset) * self.param_bet_size
            what_to_buy[self.trading_pairs[max_trading_pair]] = cash_amount_to_use

        return what_to_buy

    # Change bet size regarding proba ?
    def __buy(self, key, trading_pair, amount):
        id_order = self.trading_api.create_order(trading_pair.base_asset, trading_pair.quote_asset, ORDER_BUY, amount,
                                                 key)
        order = self.trading_api.get_order(id_order)

        # TODO : System that ensure that order is executed, may modify order, etc.

        # trace
        if self.trace:
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
                # if crypto currently in portfolio
                crypto_amount = self.trading_api.get_available_amount_crypto(value.base_asset)
                if crypto_amount > 0:
                    what_to_sell[value] = crypto_amount
        return what_to_sell

    def __sell(self, key, trading_pair, crypto_amount):  # from_crypto, to_crypto
        id_order = self.trading_api.create_order(trading_pair.base_asset, trading_pair.quote_asset, ORDER_SELL,
                                                 crypto_amount, key)
        order = self.trading_api.get_order(id_order)

        if self.trace:
            print(
                '[SELL] ORDER PLACED (' + str(key) + '): ' + str(order.quantity_base) + ' ' + order.base_asset + ' for '
                + str(order.quantity_quote) + '$ (close_price = ' + str(round(order.price, 2))
                + '$ / fees = ' + str(round(order.fees_quote_asset, 2)) + ')')

        self.x_sell[trading_pair.name].append(key)
        self.y_sell[trading_pair.name].append(order.price)

    def do_sell_all(self, key):
        for trading_pair, value in self.trading_pairs.items():
            amount_available = self.trading_api.get_available_amount_crypto(value.base_asset)
            if amount_available > 0:
                self.__sell(key, value, amount_available)

    # check & perform actions that need to be done (buy / sell) at a specific date
    def do_update(self, key, signals):
        # cancel open orders (buy + sell ?)
        self.trading_api.cancel_open_orders()

        # check api status
        status, authorized_trading_pairs = self.trading_api.check_status_api()

        if status:
            # sell
            for trading_pair, amount in self.__what_to_sell(key, signals).items():
                self.__sell(key, trading_pair, amount)
                # buy
            for trading_pair, amount in self.__what_to_buy(key, signals).items():
                self.__buy(key, trading_pair, amount)

            self.amount_x.append(key)
            self.amount_y.append(self.trading_api.get_portfolio_value(self.trading_pairs, self.cash_asset, key))
        else:
            # TODO : Error
            print('Error')

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