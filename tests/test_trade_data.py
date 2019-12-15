import unittest

class TestTradeData(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        pass

    def test_get_trade_data_all_symbols(self):
        list = self.client.get_trade_data_all_symbols()
        print("\nNumber of tickers: {0}".format(len(list)))
        self.assertTrue(len(list) > 100)

 