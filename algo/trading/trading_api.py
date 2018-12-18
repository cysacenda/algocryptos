ORDER_BUY = 'buy'
ORDER_SELL = 'sell'

from abc import ABC, abstractmethod

class TradingApi(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def check_status_api(self):
        pass

    @abstractmethod
    def get_price(self, base_asset, quote_asset, key):
        pass

    @abstractmethod
    def get_available_amount_crypto(self, symbol):
        pass

    @abstractmethod
    def get_portfolio_value(self, trading_pairs, cash_asset, key):
        # reprendre code get_portfolio_value fake ?
        pass

    @abstractmethod
    def create_order(self, base_asset, quote_asset, side, quantity_from, key):
        pass

    @abstractmethod
    def get_order(self, id_order):
        pass

    @abstractmethod
    def get_orders(self):
        pass

    @abstractmethod
    def cancel_open_orders(self):
        pass

    def get_from_to(self, base_asset, quote_asset, side):
        from_crypto = quote_asset
        to_crypto = base_asset
        if side == ORDER_SELL:
            from_crypto = base_asset
            to_crypto = quote_asset
        return from_crypto, to_crypto