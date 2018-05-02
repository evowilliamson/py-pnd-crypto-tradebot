class OrderResponse:

    def __init__(self, ticker_symbol, price, quantity_filled):
        self._ticker_symbol = ticker_symbol
        self._price = price
        self._quantity_filled = quantity_filled
