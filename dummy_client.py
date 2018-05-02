from order_response import OrderResponse
from singleton import Singleton


@Singleton
class DummyClient:

    def create_order(self, ticker_symbol, price, quantity):
        return OrderResponse(ticker_symbol, price, quantity)
