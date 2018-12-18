class AlgOrder:
    def __init__(self, id_order, base_asset, quote_asset, side, quantity_base, quantity_quote, price, fees, fees_quote_asset):
        self.id_order = id_order
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.side = side
        self.quantity_base = quantity_base
        self.quantity_quote = quantity_quote
        self.price = price
        self.fees = fees
        self.fees_quote_asset = fees_quote_asset