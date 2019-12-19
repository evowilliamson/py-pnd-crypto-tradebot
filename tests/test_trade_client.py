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
        self.assertTrue(len(TradeClient.get_trade_data_all_symbols()) > 100)

    def test_get_trade_data_found(self):
        self.assertTrue(TradeClient.get_trade_data("ETHBTC")["symbol"] == "ETHBTC")

    def test_get_trade_data_not_found(self):
        with self.assertRaises(BinanceAPIException) as e:
            TradeClient.get_trade_data("XXXBTC")
      
    def test_get_symbols(self):
        self.assertTrue(len(TradeClient.get_symbols()) > 100)
