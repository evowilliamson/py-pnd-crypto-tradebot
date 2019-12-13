from singleton import Singleton
from binance.client import Client
import json

BINANCE_KEY = "binance_key"
BINANCE_SECRET = "binance_secret"
TICKER_SYMBOL = "ticker_symbol"
SYMBOLS = "symbols"

PRICE = "lastPrice"
VOLUME = "quoteVolume"


@Singleton
class TradeClient:

    def __init__(self):
        self._config = self.read_binance_keys()
        self._client = Client(self._config[BINANCE_KEY], self._config[BINANCE_SECRET])

    def read_binance_keys(self):
        #cryptoairdrop001@protonmail.com
        return json.load(open('config/binance.config.json'))

    def get_trade_data_all_symbols(self):
        temp = self.client.get_ticker()
        return temp

    def get_trade_data(self, ticker_symbol_in_market):
        return self.client.get_ticker(symbol=ticker_symbol_in_market)

    def get_symbols(self):
        return self.client.get_exchange_info()[SYMBOLS]

    @property
    def client(self):
        return self._client
