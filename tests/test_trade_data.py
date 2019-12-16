""" Module that contains unit tests for the trade_data.py module

Test cases are self explanatory

"""

import unittest
from unittest.mock import patch
from trade_data import TradeData
from trade_client import TradeClient
import trade_client
from ticker_symbol_configuration import TickerSymbolConfiguration

ETH = "ETH"
LTC = "LTC"
XXX = "XXX"

@patch("trade_client.TradeClient.get_trade_data_all_symbols")
class TestTradeData(unittest.TestCase):

    def setUp(self):
        self.price = 200
        self.volume = 100
        pass

    def test_get_trade_data_all_symbols_found(self, mock_function):

        self._set_return_value(mock_function, ETH)
        data = TradeData.get_data_for_all_symbols()
        self.assertTrue(TradeData.get_current_trade_data(data, ETH, TradeData.PRICE), self.price)
        self.assertTrue(TradeData.get_current_trade_data(data, ETH, TradeData.VOLUME), self.volume)
        
    def test_get_trade_data_all_symbols_not_found(self, mock_function):
        self._set_return_value(mock_function, XXX)
        self.assertIsNone(TradeData.get_current_trade_data(
            TradeData.get_data_for_all_symbols(), XXX, TradeData.PRICE), self.price)

    def test_get_number_of_rows_not_empty(self, mock_function):
        self._set_return_value(mock_function, ETH)
        data = TradeData.get_data_for_all_symbols()
        data = data.append(TradeData.get_data_for_all_symbols())
        self.assertTrue(TradeData.get_number_of_rows(data, ETH) == 2)
        
    def test_get_number_of_rows_empty(self, mock_function):
        self._set_return_value(mock_function, ETH)
        self.assertTrue(TradeData.get_number_of_rows(TradeData.get_data_for_all_symbols(), LTC) == 0)

    def test_get_penultimate_trade_data(self, mock_function):
        self._set_return_value(mock_function, ETH)
        self.price = 1000
        self.volume = 2000
        data = TradeData.get_data_for_all_symbols()
        self.price = 2000
        self.volume = 4000
        data = data.append(TradeData.get_data_for_all_symbols())
        penultimate_price = self.price
        penultimate_volume = self.volume
        self.price = 20000
        self.volume = 40000
        data = data.append(TradeData.get_data_for_all_symbols())
        self.assertTrue(TradeData.get_penultimate_trade_data(data, ETH, TradeData.VOLUME), 
            penultimate_volume)
        self.assertTrue(TradeData.get_penultimate_trade_data(data, ETH, TradeData.PRICE), 
            penultimate_price)

    def test_get_penultimate_trade_data(self, mock_function):
        self._set_return_value(mock_function, ETH)
        self.price = 1000
        self.volume = 2000
        data = TradeData.get_data_for_all_symbols()
        self.price = 2000
        self.volume = 4000
        data = data.append(TradeData.get_data_for_all_symbols())
        n_price = self.price
        n_volume = self.volume
        self.price = 20000
        self.volume = 40000
        data = data.append(TradeData.get_data_for_all_symbols())
        self.price = 100000
        self.volume = 2000000
        data = data.append(TradeData.get_data_for_all_symbols())
        self.assertTrue(TradeData.get_current_minus_n_trade_data(data, ETH, TradeData.VOLUME, 3), 
            n_volume)
        self.assertTrue(TradeData.get_current_minus_n_trade_data(data, ETH, TradeData.PRICE, 3), 
            n_price)

    def _set_return_value(self, _mock_function, ticker):
        """ This private method sets the return value of the mock function that is called repeatedly
        for every test method

        Args:
            mock_function(MagicMock): the mock function
            ticker_symbol(str): the ticker to be acted upon
        """

        _mock_function.return_value = [{TradeClient().VOLUME: self.volume, 
            TradeClient().PRICE: self.price, 
            TickerSymbolConfiguration().SYMBOL: ticker}]