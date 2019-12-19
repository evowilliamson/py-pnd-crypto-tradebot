""" Module that contains a class that manages the communication with the crypto exchange
"""

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
        """ Retrieves trading information from the exchange for all ticker symbols
        
        Returns:
            list(dict()): a list of dictionaries. Every dictionary contains trading information
                pertaining to a certain ticker symbol
        """

        return cls.trade_client.get_ticker()

    @classmethod
    def get_trade_data(cls, ticker_symbol_in_market):
        """ Retrieves trading information from the exchange for the specified ticker symbol
        
        Args:
            ticker_symbol_in_market: The ticker symbol (ETH for example)

        Returns:
            dict(): A dictionary that contains trade data pertaining to the ticker symbol 
                as of now
        """

        return cls.trade_client.get_ticker(symbol=ticker_symbol_in_market)

    @classmethod
    def get_symbols(cls):
        """ Get ticker symbols from the exchange

        Returns:
            list(dict): a list of, for each ticker symbol, related information, per dict

        """

        return cls.trade_client.get_exchange_info()[TradeClient.SYMBOLS]

    @classmethod
    def get_client(cls):
        return TradeClient.trade_client

TradeClient()