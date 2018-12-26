class AlgOrderFake:
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

class AlgOrderBinance:
    # init from object retrieved from binance API
    def __init__(self, order):
        self.origClientOrderId = order['origClientOrderId']
        self.orderId = order['orderId']
        self.clientOrderId = order['clientOrderId']
        self.price = order['price']
        self.origQty = order['origQty']
        self.executedQty = order['executedQty']
        self.cummulativeQuoteQty = order['cummulativeQuoteQty']
        self.status = order['status']
        self.timeInForce = order['timeInForce']
        self.type = order['type']
        self.side = order['side']
        if 'fills' in order:
            self.fills = order['fills']

