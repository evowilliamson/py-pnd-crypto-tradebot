from trade_client import TradeClient
import trade_data
import trade_client
from ticker_symbol_configuration import TickerSymbolConfiguration
import pandas as pd
import datetime

TIME = "time"
PENULTIMATE = 2
TICKER_SYMBOL = "ticker_symbol"
VALUE = "value"
PRICE = "price"
VOLUME = "volume"


class TradeData:

    @staticmethod
    def get_data_for_all_symbol():
        df = pd.DataFrame()
        for data in TradeClient().get_trade_data_all_symbols():
            ticker_symbol = TickerSymbolConfiguration().get_adjusted_trade_data_ticker_symbol(data)
            if not TickerSymbolConfiguration().exists_in_configuration(ticker_symbol):
                continue
            row = pd.DataFrame({
                TIME: datetime.datetime.now(),
                TICKER_SYMBOL: {VALUE: ticker_symbol},
                trade_data.PRICE: {VALUE: float(data[trade_client.PRICE])},
                trade_data.VOLUME: {VALUE: float(data[trade_client.VOLUME])}})
            row = row.set_index([TIME])
            df = df.append(row)
        return df

    @staticmethod
    def get_current_trade_data(data, ticker_symbol, what):
        return data[data[TICKER_SYMBOL] == ticker_symbol].tail(1)[what].values[0]

    @staticmethod
    def get_penultimate_trade_data(data, ticker_symbol, what):
        return TradeData.get_current_minus_n_trade_data(data, ticker_symbol, what, PENULTIMATE)

    @staticmethod
    def get_current_minus_n_trade_data(data, ticker_symbol, what, n):
        return data[data[TICKER_SYMBOL] == ticker_symbol].tail(n + 1).head(1)[what].values[0]

    @staticmethod
    def get_number_of_rows(data, ticker_symbol):
        return len(data[data[TICKER_SYMBOL] == ticker_symbol])
