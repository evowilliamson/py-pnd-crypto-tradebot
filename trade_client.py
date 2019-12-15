from binance.client import Client
import json


class TradeClient:

    BINANCE_KEY = "binance_key"
    BINANCE_SECRET = "binance_secret"
    TICKER_SYMBOL = "ticker_symbol"
    SYMBOLS = "symbols"
    PRICE = "lastPrice"
    VOLUME = "quoteVolume"

    def __init__(self):
        #cryptoairdrop001@protonmail.com
        TradeClient.config = json.load(open('config/binance.config.json'))
        TradeClient.trade_client = Client(
            TradeClient.config[TradeClient.BINANCE_KEY], 
            TradeClient.config[TradeClient.BINANCE_SECRET])

    @classmethod
    def get_trade_data_all_symbols(cls):
        return cls.trade_client.get_ticker()

    @classmethod
    def get_trade_data(cls, ticker_symbol_in_market):
        return cls.trade_client.get_ticker(symbol=ticker_symbol_in_market)

    @classmethod
    def get_symbols(cls):
        return cls.trade_client.get_exchange_info()[TradeClient.SYMBOLS]

    @classmethod
    def get_client(cls):
        return TradeClient.trade_client

TradeClient()