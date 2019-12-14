import unittest
from trade_client import TradeClient
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException

class TestTradeClient(unittest.TestCase):

    def setUp(self):
        self.client = TradeClient()
        pass

    def test_init(self):
        self.assertIsInstance(self.client.client, BinanceClient)

    def test_get_trade_data_all_symbols(self):
        list = self.client.get_trade_data_all_symbols()
        print("\nNumber of tickers: {0}".format(len(list)))
        self.assertTrue(len(list) > 100)

    def test_get_trade_data_found(self):
        ticker = self.client.get_trade_data("ETHBTC")
        self.assertTrue(ticker["symbol"] == "ETHBTC")

    def test_get_trade_data_not_found(self):
        with self.assertRaises(BinanceAPIException) as e:
            self.client.get_trade_data("XXXBTC")
      
    def test_get_symbols(self):
        self.assertTrue(len(self.client.get_symbols()) > 100)
