from abc import ABC, abstractmethod

ORDER_BUY = 'buy'
ORDER_SELL = 'sell'


class TradingApi(ABC):
    @abstractmethod
    def __init__(self, param_pct_order_placed, stop_loss_pct):
        pass

    @abstractmethod
    def is_fake_api(self):
        pass

    @abstractmethod
    def check_status_api(self):
        pass

    @abstractmethod
    def check_predictions_time_vs_server_time(self, dict_dates):
        pass

    @abstractmethod
    def get_price_ticker(self, base_asset, quote_asset, key):
        pass

    @abstractmethod
    def get_buy_price(self, base_asset, quote_asset, key):
        pass

    @abstractmethod
    def get_sell_price(self, base_asset, quote_asset, key):
        pass

    @abstractmethod
    def get_available_amount_crypto(self, symbol):
        pass

    @abstractmethod
    def create_order(self, base_asset, quote_asset, side, quantity_from, key):
        pass

    @abstractmethod
    def get_order(self, id_order, trading_pair):
        pass

    @abstractmethod
    def get_orders(self):
        pass

    @abstractmethod
    def cancel_open_orders(self):
        pass

    def get_portfolio_value(self, trading_pairs, cash_asset, key):
        total_value = 0
        for trading_pair, value in trading_pairs.items():
            amount = self.get_available_amount_crypto(value.base_asset)
            current_price = self.get_price_ticker(value.base_asset, value.quote_asset, key)
            total_value = total_value + (amount * current_price)
        total_value = total_value + self.get_available_amount_crypto(cash_asset)
        return total_value

    @staticmethod
    def get_from_to(base_asset, quote_asset, side):
        from_crypto = quote_asset
        to_crypto = base_asset
        if side == ORDER_SELL:
            from_crypto = base_asset
            to_crypto = quote_asset
        return from_crypto, to_crypto
