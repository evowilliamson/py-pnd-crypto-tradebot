import unittest
from unittest.mock import patch
from trade_data import TradeData
from trade_client import TradeClient
import trade_client
from ticker_symbol_configuration import TickerSymbolConfiguration

ETH = "ETH"

class TestTradeData(unittest.TestCase):

    def setUp(self):
        pass

    @patch("trade_client.TradeClient.get_trade_data_all_symbols")
    def test_get_trade_data_all_symbols(self, mock_function):
        price = 200
        volume = 100
        mock_function.return_value = [{TradeClient().VOLUME: volume, 
            TradeClient().PRICE: price, 
            TickerSymbolConfiguration().SYMBOL: ETH}]
        data = TradeData.get_data_for_all_symbols()
        self.assertTrue(TradeData.get_current_trade_data(data, ETH, TradeData.PRICE), price)
        self.assertTrue(TradeData.get_current_trade_data(data, ETH, TradeData.VOLUME), volume)
        


 