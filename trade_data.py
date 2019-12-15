from trade_client import TradeClient
from ticker_symbol_configuration import TickerSymbolConfiguration
import pandas as pd
import datetime


class TradeData:

    TIME = "time"
    PENULTIMATE = 2
    TICKER_SYMBOL = "ticker_symbol"
    VALUE = "value"
    PRICE = "price"
    VOLUME = "volume"

    @classmethod
    def get_data_for_all_symbols(cls):  
        df = pd.DataFrame()
        for data in TradeClient.get_trade_data_all_symbols():
            ticker_symbol = TickerSymbolConfiguration().get_adjusted_trade_data_ticker_symbol(data)
            if not TickerSymbolConfiguration().exists_in_configuration(ticker_symbol):
                continue
            row = pd.DataFrame({
                cls.TIME: datetime.datetime.now(),
                cls.TICKER_SYMBOL: {cls.VALUE: ticker_symbol},
                cls.PRICE: {cls.VALUE: float(data[TradeClient.PRICE])},
                cls.VOLUME: {cls.VALUE: float(data[TradeClient.VOLUME])}})
            row = row.set_index([cls.TIME])
            df = df.append(row)
        return df

    @classmethod
    def get_current_trade_data(cls, data, ticker_symbol, what):
        return data[data[cls.TICKER_SYMBOL] == ticker_symbol].tail(1)[what].values[0]

    @classmethod
    def get_penultimate_trade_data(cls, data, ticker_symbol, what):
        return cls.get_current_minus_n_trade_data(
            data, ticker_symbol, what, cls.PENULTIMATE)

    @classmethod
    def get_current_minus_n_trade_data(cls, data, ticker_symbol, what, n):
        return data[data[cls.TICKER_SYMBOL] == ticker_symbol].tail(n + 1).head(1)[what].values[0]

    @classmethod
    def get_number_of_rows(cls, data, ticker_symbol):
        return len(data[data[cls.TICKER_SYMBOL] == ticker_symbol])
