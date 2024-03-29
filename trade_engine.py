from singleton import Singleton
import time
import datetime
import pandas as pd
import threading
from system_config import Config, BTC_PUMP_QUANTITY
from pumper import Pumper
from ticker_symbol_configuration import TickerSymbolConfiguration
from trade_client import TradeClient
from trade_data import TradeData


@Singleton
class TradeEngine:

    TIME = "time"
    VALUE = "value"
    INTERVAL = "interval"
    PUMP = "pump"
    GAINERS = "gainers"
    LOSERS = "losers"

    ROWS_PER_COLUMN = 10
    STEP_SIZE = 5
    NUMBER_OF_COLUMNS = 1
    FIRST_ROW = 1
    SLEEP_TIME = 20
    CANDLE_STICKS_PER_MINUTE = 60 / SLEEP_TIME

    INTERVALS = [1*SLEEP_TIME, 2*SLEEP_TIME, 5*SLEEP_TIME, 
                10*SLEEP_TIME, 20*SLEEP_TIME, 60*SLEEP_TIME, 
                120*SLEEP_TIME, 240*SLEEP_TIME, 480*SLEEP_TIME]

    PERCENTAGE_CHANGE_PRICE = {1*SLEEP_TIME: 0.1, 2*SLEEP_TIME: 1.0, 
                               5*SLEEP_TIME: 0.0, 10*SLEEP_TIME: 0.0, 
                               20*SLEEP_TIME: 0.0, 60*SLEEP_TIME: 0.0,
                               120*SLEEP_TIME: 0.0, 240 * SLEEP_TIME: 0.0, 
                               480 * SLEEP_TIME: 0.0}

    PERCENTAGE_CHANGE_VOLUME = {1*SLEEP_TIME: 0.1, 2*SLEEP_TIME: 0.2, 
                                5*SLEEP_TIME: 0.0, 10*SLEEP_TIME: 0.0, 
                                20*SLEEP_TIME: 0.0, 60*SLEEP_TIME: 0.0,
                                120*SLEEP_TIME: 0.0, 240 * SLEEP_TIME: 0.0, 
                                480 * SLEEP_TIME: 0.0}

    INTERVAL_TO_COLUMN_NO = {1*SLEEP_TIME: 1, 2*SLEEP_TIME: 1, 
                             5*SLEEP_TIME: 1, 10*SLEEP_TIME: 1, 
                             20*SLEEP_TIME: 1, 60*SLEEP_TIME: 1,
                             120*SLEEP_TIME: 1, 240*SLEEP_TIME: 1, 
                             480*SLEEP_TIME: 1}

    def __init__(self):
        self._thread = threading.Thread(target=self.run)
        self._ticker_symbols = TickerSymbolConfiguration().ticker_symbols
        self._historical_trade_data = pd.DataFrame()
        self._changes = pd.DataFrame()
        self._list_mode = self.GAINERS
        self._trades = []
        self.cross_check_ticker_symbols()
        self._pumpers = Pumper.reconstruct_running_pumps(self)
        self._ignore = False
        self._thread.start()

    def run(self):
        while True:
            self._historical_trade_data = \
                self.historical_trade_data.append(TradeData.get_data_for_all_symbols())
            for ticker_symbol in self._ticker_symbols:
                for i in self.INTERVALS:
                    self.check_change_interval(ticker_symbol, i)
            self.report_changes()
            self._changes = pd.DataFrame()
            time.sleep(self.SLEEP_TIME)
            print("Number of pumpers: {0}".format(len(self.pumpers)))

    def join(self):
        self._thread.join()

    def check_change_interval(self, ticker_symbol, interval):
        candle_sticks = int(interval / self.SLEEP_TIME)
        if TradeData.get_number_of_rows(self.historical_trade_data, ticker_symbol) < candle_sticks + 1:
            return

        first_pump_price = TradeData.get_current_trade_data(
            self.historical_trade_data, ticker_symbol, TradeData.PRICE)
        initial_price = TradeData.get_current_minus_n_trade_data(
            self.historical_trade_data, ticker_symbol, TradeData.PRICE, candle_sticks)
        first_pump_volume = TradeData.get_current_trade_data(
            self.historical_trade_data, ticker_symbol, TradeData.VOLUME)
        initial_volume = TradeData.get_current_minus_n_trade_data(
            self.historical_trade_data, ticker_symbol, TradeData.VOLUME, candle_sticks)

        pump = False
        if first_pump_price > (initial_price * ((self.PERCENTAGE_CHANGE_PRICE[interval] + 100) / 100)) and \
           first_pump_volume > (initial_volume * ((self.PERCENTAGE_CHANGE_VOLUME[interval] + 100) / 100)) and \
                (interval == self.SLEEP_TIME or interval == self.SLEEP_TIME*2):
            pump = True
            self.create_new_pump(ticker_symbol=ticker_symbol,
                                 initial_price=initial_price,
                                 first_pump_price=first_pump_price,
                                 initial_volume=initial_volume,
                                 first_pump_volume=first_pump_volume,
                                 quantity=self.get_target_quantity(
                                                Config().config[BTC_PUMP_QUANTITY],
                                                first_pump_price))

        self.add_change_interval(interval, first_pump_price, first_pump_volume, initial_price, initial_volume, pump,
                                 ticker_symbol)

    def add_change_interval(self, interval, last_price, last_volume, previous_price, previous_volume, pump,
                            ticker_symbol):
        change = pd.DataFrame({
            self.TIME: datetime.datetime.now(),
            TradeClient.TICKER_SYMBOL: {self.VALUE: ticker_symbol},
            self.INTERVAL: {self.VALUE: interval},
            TradeData.PRICE: {self.VALUE: self.get_percentage(previous_price, last_price)},
            TradeData.VOLUME: {self.VALUE: self.get_percentage(previous_volume, last_volume)},
            self.PUMP: {self.VALUE: pump}})
        change = change.set_index([self.TIME])
        self._changes = self._changes.append(change)

    def create_new_pump(self, ticker_symbol, initial_price,
                        first_pump_price, initial_volume, first_pump_volume, quantity):

        self._ignore = True
        for pump in self._pumpers:
            if pump.ticker_symbol == ticker_symbol:
                print("ticker symbol {0} already pumping".format(ticker_symbol))
                return
        self._pumpers.append(Pumper(self, ticker_symbol=ticker_symbol, initial_price=initial_price,
                                    first_pump_price=first_pump_price, initial_volume=initial_volume,
                                    first_pump_volume=first_pump_volume, quantity=quantity))

    def report_changes(self):

        if len(self._changes) == 0:
            return

        pumps = self._changes[self._changes[self.PUMP]]
        if not pumps.empty:
            print("Pump detected !!!! ")

        sort_order = False if self._list_mode == self.GAINERS else True
        self._changes = self._changes.sort_values(by=[self.INTERVAL, TradeData.PRICE],
                                                  ascending=[True, sort_order])
        line = ""
        for block in range(0, len(self.INTERVALS)):
            for row_no in range(1, self.ROWS_PER_COLUMN):
                self.print_row(line, row_no, self.INTERVALS[block:(block + 1)])

    def print_row(self, line, row_no, intervals):
        header_line = ""
        for interval in intervals:
            if row_no == self.FIRST_ROW:
                header_line += "{0} min. Ticker  Price     Volumne     Pump         ".format(
                        str(float(interval) / 60.0), self.ROWS_PER_COLUMN)
            row = self.get_row_for_interval(interval, row_no)
            if not row.empty:
                line += "{0: <17}{1: >+3.3f}    {2: >+2.3f}      {3: <6}      " \
                        .format(row[TradeClient.TICKER_SYMBOL], row[TradeData.PRICE], 
                                row[TradeData.VOLUME], "***" if row[self.PUMP] else "")
            if self.INTERVAL_TO_COLUMN_NO[interval] == self.NUMBER_OF_COLUMNS:
                if row_no == self.FIRST_ROW:
                    print(header_line)
                    print("-------------------------------------------------------")
                    header_line = ""
                print(line)
                line = ""

    def get_row_for_interval(self, interval, row_no):
        top = self._changes[self._changes[self.INTERVAL] == interval].head(self.ROWS_PER_COLUMN)
        if row_no > len(top):
            return pd.Series([])
        return top.iloc[row_no - 1]

    @staticmethod
    def get_percentage(start, end):
        return start and ((end - start) / start) * 100.0

    def cross_check_ticker_symbols(self):
        symbols = TradeClient.get_symbols()
        for info in symbols:
            ticker_symbol = TickerSymbolConfiguration().get_adjusted_trade_data_ticker_symbol(info)
            if not TickerSymbolConfiguration().exists_in_configuration(ticker_symbol):
                print("Ticker symbol {0} found in trade data is not a configured ticker symbol".format(ticker_symbol))

        temp_ticker_symbols = []
        for ticker_symbol in self._ticker_symbols:
            if not self.exists_ticker_symbol_in_trade_data(ticker_symbol, symbols):
                print("Ticker symbol {0} found in configuration is not present in trade data as a ticker symbol".
                      format(ticker_symbol))
            else:
                temp_ticker_symbols.append(ticker_symbol)
        self._ticker_symbols = temp_ticker_symbols

    @staticmethod
    def get_target_quantity(btc_quantity, last_price):
        return float(btc_quantity) / last_price

    @staticmethod
    def exists_ticker_symbol_in_trade_data(ticker_symbol, ticker_symbols_trade_data):
        for info in ticker_symbols_trade_data:
            if TickerSymbolConfiguration().get_adjusted_trade_data_ticker_symbol(info) == ticker_symbol:
                return True
        return False

    @property
    def historical_trade_data(self):
        return self._historical_trade_data

    @property
    def pumpers(self):
        return self._pumpers
