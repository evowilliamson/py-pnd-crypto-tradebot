import unittest
from trade_client import TradeClient
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException

class TestTradeClient(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        self.assertIsInstance(TradeClient.get_client(), BinanceClient)

    def test_get_trade_data_all_symbols(self):
        list = TradeClient.get_trade_data_all_symbols()
        self.assertTrue(len(list) > 100)

    def test_get_trade_data_found(self):
        ticker = TradeClient.get_trade_data("ETHBTC")
        self.assertTrue(ticker["symbol"] == "ETHBTC")

    def test_get_trade_data_not_found(self):
        with self.assertRaises(BinanceAPIException) as e:
            TradeClient.get_trade_data("XXXBTC")
      
    def test_get_symbols(self):
        self.assertTrue(len(TradeClient.get_symbols()) > 100)
