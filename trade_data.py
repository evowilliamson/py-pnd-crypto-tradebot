from trade_client import TradeClient,CURRENT_VOLUME, LAST_PRICE
from ticker_symbol_configuration import TickerSymbolConfiguration
import pandas as pd
import datetime
from singleton import Singleton

TIME = "time"
PRICE = "price"
VOLUME = "volume"
PENULTIMATE = 2
TICKER_SYMBOL = "ticker_symbol"
VALUE = "value"


@Singleton
class TradeData:

    @staticmethod
    def get_data_for_all_symbol():
        trade_data = pd.DataFrame()
        for data in TradeClient.instance().get_trade_data_all_symbols():
            ticker_symbol = TickerSymbolConfiguration.instance().get_adjusted_trade_data_ticker_symbol(data)
            if not TickerSymbolConfiguration.instance().exists_in_configuration(ticker_symbol):
                continue
            if TickerSymbolConfiguration.instance().consider_ticket(ticker_symbol):
                row = pd.DataFrame({
                    TIME: datetime.datetime.now(),
                    TICKER_SYMBOL: {VALUE: ticker_symbol},
                    PRICE: {VALUE: float(data[LAST_PRICE])},
                    VOLUME: {VALUE: float(data[CURRENT_VOLUME])}})
                row = row.set_index([TIME])
                trade_data = trade_data.append(row)
        return trade_data

    @staticmethod
    def get_current_trade_data(trade_data, ticker_symbol, what):
        return trade_data[trade_data[TICKER_SYMBOL] == ticker_symbol].tail(1)[what].values[0]

    @staticmethod
    def get_penultimate_trade_data(trade_data, ticker_symbol, what):
        return TradeData.get_current_minus_n_trade_data(trade_data, ticker_symbol, what, PENULTIMATE)

    @staticmethod
    def get_current_minus_n_trade_data(trade_data, ticker_symbol, what, n):
        return trade_data[trade_data[TICKER_SYMBOL] == ticker_symbol].tail(n + 1).head(1)[what].values[0]

    @staticmethod
    def get_number_of_rows(trade_data, ticker_symbol):
        return len(trade_data[trade_data[TICKER_SYMBOL] == ticker_symbol])
