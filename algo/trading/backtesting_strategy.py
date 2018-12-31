from datetime import timedelta
import pandas as pd
import numpy as np
from trading.trading_api_fake import TradingApiFake
from trading.trading_module import TradingModule
from commons.config import Config


class BacktestingStrategy:
    def __init__(self, model, model_term, init_date, end_date, X_tests, close_price, target, thresholds, trading_pairs,
                 cash_asset, trace=True):
        conf = Config()

        self.param_init_amount_cash = float(conf.get_config('backtesting_stragegy_params', 'init_amount_cash'))  # $
        self.param_fees = float(conf.get_config('backtesting_stragegy_params', 'fees'))  # $
        self.param_bet_size = float(conf.get_config('backtesting_stragegy_params', 'bet_size'))  # %
        self.param_min_bet_size = float(conf.get_config('backtesting_stragegy_params', 'min_bet_size'))  # $
        self.param_pct_order_placed = float(conf.get_config('backtesting_stragegy_params', 'pct_order_placed'))  # 1% up/down
        self.param_nb_periods_to_hold_position = int(conf.get_config('backtesting_stragegy_params', 'pct_order_placed'))  # 1d
        self.signals = {}
        self.all_signals = {}

        self.model = model
        self.model_term = model_term
        self.init_date = init_date
        self.end_date = end_date - timedelta(hours=1)  # to avoid getting a price unknown at the end of simulation
        self.X_tests = X_tests
        self.close_price = close_price
        self.target = target
        self.thresholds = thresholds
        self.trading_pairs = trading_pairs
        self.cash_asset = cash_asset
        self.trace = trace

        self.__calcul_signals()

        # set init positions
        init_positions = {self.cash_asset: self.param_init_amount_cash}
        for key, value in trading_pairs.items():
            init_positions[value.base_asset] = 0.0

        # trading API (fake one for simulation)
        trading_api = TradingApiFake(self.param_pct_order_placed)
        trading_api.init_from_backtesting_strategy(init_positions, self.param_fees, self.close_price)

        # trading module
        self.trading_module = TradingModule(trading_api, self.param_bet_size, self.param_min_bet_size,
                                            self.param_pct_order_placed, self.param_nb_periods_to_hold_position,
                                            self.trading_pairs,  self.cash_asset, self.thresholds, self.trace)

    def __calcul_signals(self):
        conf = Config()
        proba_min = float(conf.get_config('trading_module_params', 'proba_min'))  # %

        for trading_pair, value in self.trading_pairs.items():
            predicted_proba = self.model.predict_proba(self.X_tests[trading_pair].values)
            probs = predicted_proba[:, 1]
            df_probs = pd.DataFrame(probs)
            df_probs.index = self.X_tests[trading_pair].index
            df_probs.columns = ['signal_prob']
            self.signals[trading_pair] = df_probs

            # all signals
            signal = df_probs.signal_prob > proba_min
            self.all_signals[trading_pair] = df_probs[signal]

    def override_signals(self, signals):
        self.signals = signals

    def get_signals(self):
        return self.trading_module.get_signals()

    def get_signals_for_date(self, current_date):
        signals_for_date = {}
        date_before = current_date - timedelta(hours=self.model_term)
        for trading_pair, value in self.trading_pairs.items():
            signals_for_date[trading_pair] = self.signals[trading_pair].truncate(before=date_before, after=current_date)
        return signals_for_date

    def calcul_pct_change(self):
        pct_changes = {}
        total = 0
        for trading_pair, value in self.trading_pairs.items():
            market_price_begin = self.close_price[trading_pair].head(1)[0]  # .values[0]
            market_price_end = self.close_price[trading_pair].tail(1)[0]  # .values[0]
            pct_change_market = round((market_price_end - market_price_begin) / market_price_begin * 100, 2)
            pct_changes[trading_pair] = pct_change_market
            total = total + pct_change_market
        return pct_changes, round(total / len(pct_changes), 2)

    def do_backtest(self):
        current_date = self.init_date
        while current_date < self.end_date:
            signals = self.get_signals_for_date(current_date)
            self.trading_module.do_update(current_date, signals)
            current_date = current_date + timedelta(hours=1)
        self.trading_module.do_sell_all(current_date)

        # Results
        simulation_time = round((self.end_date - self.init_date).days)  # Avec les dates !
        final_amount = round(self.trading_module.get_available_amount_crypto(self.cash_asset), 2)
        all_fees_paid = round(self.trading_module.get_all_fees_paid(), 2)
        pct_change_portfolio = round((final_amount - self.param_init_amount_cash) / self.param_init_amount_cash * 100,
                                     2)
        pct_changes_market_per_crypto, pct_changes_market_average = self.calcul_pct_change()
        nb_trades = self.trading_module.get_nb_transactions_done()

        if self.trace:
            print('\n')
            print('Simulation time: ' + str(simulation_time) + ' days')
            print('Start amount: ' + str(self.param_init_amount_cash) + '$')
            print('Final amount: ' + str(final_amount) + '$')
            print('Number of transactions: ' + str(nb_trades))
            print('Fees: ' + str(all_fees_paid) + '$')
            print('Pourcentage change portfolio: ' + str(pct_change_portfolio) + '%')
            for trading_pair, value in pct_changes_market_per_crypto.items():
                print('Pourcentage change market ' + self.trading_pairs[trading_pair].base_asset + ' : ' + str(
                    value) + '%')
            print('Pourcentage change market average : ' + str(pct_changes_market_average) + '%')

        return simulation_time, final_amount, all_fees_paid, pct_change_portfolio, pct_changes_market_average, nb_trades

    def show_graphs(self):
        # here to avoid problem when started in batch mode
        from matplotlib import pyplot as plt
        x_buy, y_buy, x_sell, y_sell, amount_x, amount_y = self.get_signals()

        # buy / sell per crypto
        for trading_pair, value in self.trading_pairs.items():
            plt.figure(figsize=(20, 10))
            plt.plot(self.close_price[trading_pair])
            plt.plot(x_buy[trading_pair], y_buy[trading_pair], '^', markersize=10, color='g')
            plt.plot(x_sell[trading_pair], y_sell[trading_pair], 'v', markersize=10, color='r')
            plt.plot(self.all_signals[trading_pair].index.get_level_values(0).values,
                     np.zeros(len(self.all_signals[trading_pair])), '|', markersize=10, color='k')
            plt.xlabel('time')
            plt.ylabel('close_price ' + value.base_asset)
            plt.show()

        # portfolio value
        plt.figure(figsize=(20, 10))
        plt.plot(amount_x, amount_y, color='y')
        plt.xlabel('time')
        plt.ylabel('portfolio_value')
        plt.show()
