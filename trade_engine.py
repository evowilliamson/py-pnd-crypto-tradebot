from singleton import Singleton
import time
import datetime
import pandas as pd
import threading
from system_config import Config, BTC_PUMP_QUANTITY
from pumper import Pumper
from ticker_symbol_configuration import TickerSymbolConfiguration
from trade_client import TradeClient, TICKER_SYMBOL
from trade_data import TradeData
import trade_data

TIME = "time"

VALUE = "value"
PENULTIMATE = 2
INTERVAL = "interval"
PUMP = "pump"

ROWS_PER_COLUMN = 10

INTERVAL_CHANGE_MESSAGE = "{0}: Change {1}: price: {2}, volume {3}"
STEP_CHANGE_MESSAGE = "{0}: step change: step start price: {1}, current price: {2}"

STEP_SIZE = 5
NUMBER_OF_COLUMNS = 3
FIRST_ROW = 1

SLEEP_TIME = 20
CANDLE_STICKS_PER_MINUTE = 60 / SLEEP_TIME

INTERVALS = [1*SLEEP_TIME, 2*SLEEP_TIME, 5*SLEEP_TIME, 10*SLEEP_TIME, 20*SLEEP_TIME,
             60*SLEEP_TIME, 120*SLEEP_TIME, 240*SLEEP_TIME, 480*SLEEP_TIME]

GAINERS = "gainers"
LOSERS = "losers"
LIST_MODES = [GAINERS, LOSERS]

PERCENTAGE_CHANGE_PRICE = {1*SLEEP_TIME: 0.5, 2*SLEEP_TIME: 1.0, 5*SLEEP_TIME: 0.0,
                           10*SLEEP_TIME: 0.0, 20*SLEEP_TIME: 0.0, 60*SLEEP_TIME: 0.0,
                           120*SLEEP_TIME: 0.0, 240 * SLEEP_TIME: 0.0, 480 * SLEEP_TIME: 0.0}

PERCENTAGE_CHANGE_VOLUME = {1*SLEEP_TIME: 0.1, 2*SLEEP_TIME: 0.2, 5*SLEEP_TIME: 0.0,
                            10*SLEEP_TIME: 0.0, 20*SLEEP_TIME: 0.0, 60*SLEEP_TIME: 0.0,
                            120*SLEEP_TIME: 0.0, 240 * SLEEP_TIME: 0.0, 480 * SLEEP_TIME: 0.0}

INTERVAL_TO_COLUMN_NO = {1*SLEEP_TIME: 1, 2*SLEEP_TIME: 2, 5*SLEEP_TIME: 3,
                         10*SLEEP_TIME: 1, 20*SLEEP_TIME: 2, 60*SLEEP_TIME: 3,
                         120*SLEEP_TIME: 1, 240 * SLEEP_TIME: 2, 480 * SLEEP_TIME: 3}


@Singleton
class TradeEngine:

    def __init__(self, order_client):
        self._order_client = order_client
        self._thread = threading.Thread(target=self.run)
        self._ticker_symbols = TickerSymbolConfiguration.instance().load_from_configuration()
        self._historical_trade_data = pd.DataFrame()
        self._changes = pd.DataFrame()
        self._list_mode = GAINERS
        self._trades = []
        self.cross_check_ticker_symbols()
        self._pumpers = Pumper.reconstruct_running_pumps(self)
        self._ignore = False
        self._thread.start()

    def run(self):
        while True:
            self._historical_trade_data = self.historical_trade_data.append(TradeData.get_data_for_all_symbol())
            for ticker_symbol in self._ticker_symbols:
                for i in INTERVALS:
                    self.check_change_interval(ticker_symbol, i)
            # if not self._ignore:
            self.report_changes()
            self._changes = pd.DataFrame()
            time.sleep(SLEEP_TIME)
            # self._ignore = True
            print("Number of pumpers: {0}".format(len(self.pumpers)))

    def join(self):
        self._thread.join()

    def change_list_mode(self, list_mode):
        self._list_mode = list_mode

    def check_change_interval(self, ticker_symbol, interval):
        candle_sticks = int(interval / SLEEP_TIME)
        if TradeData.get_number_of_rows(self.historical_trade_data, ticker_symbol) < candle_sticks + 1:
            return

        first_pump_price = TradeData.get_current_trade_data(
            self.historical_trade_data, ticker_symbol, trade_data.PRICE)
        initial_price = TradeData.get_current_minus_n_trade_data(
            self.historical_trade_data, ticker_symbol, trade_data.PRICE, candle_sticks)
        first_pump_volume = TradeData.get_current_trade_data(
            self.historical_trade_data, ticker_symbol, trade_data.VOLUME)
        initial_volume = TradeData.get_current_minus_n_trade_data(
            self.historical_trade_data, ticker_symbol, trade_data.VOLUME, candle_sticks)

        pump = False
        if first_pump_price > (initial_price * ((PERCENTAGE_CHANGE_PRICE[interval] + 100) / 100)) and \
           first_pump_volume > (initial_volume * ((PERCENTAGE_CHANGE_VOLUME[interval] + 100) / 100)) and \
                (interval == SLEEP_TIME or interval == SLEEP_TIME*2):
            pump = True
            self.create_new_pump(ticker_symbol=ticker_symbol,
                                 initial_price=initial_price,
                                 first_pump_price=first_pump_price,
                                 initial_volume=initial_volume,
                                 first_pump_volume=first_pump_volume,
                                 quantity=self.get_target_quantity(
                                                Config.instance().config[BTC_PUMP_QUANTITY],
                                                first_pump_price))

        self.add_change_interval(interval, first_pump_price, first_pump_volume, initial_price, initial_volume, pump,
                                 ticker_symbol)

    def add_change_interval(self, interval, last_price, last_volume, previous_price, previous_volume, pump,
                            ticker_symbol):
        change = pd.DataFrame({
            TIME: datetime.datetime.now(),
            TICKER_SYMBOL: {VALUE: ticker_symbol},
            INTERVAL: {VALUE: interval},
            trade_data.PRICE: {VALUE: self.get_percentage(previous_price, last_price)},
            trade_data.VOLUME: {VALUE: self.get_percentage(previous_volume, last_volume)},
            PUMP: {VALUE: pump}})
        change = change.set_index([TIME])
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

        pumps = self._changes[self._changes[PUMP]]
        if not pumps.empty:
            for interval in range(1, 1000):
                print("*************************************************************************************")
                print("")
                print("*************************************************************************************")
                print("")
            print("*************************************************************************************")
            print("Pump detected !!!! ")
            print("*************************************************************************************")

        sort_order = False if self._list_mode == GAINERS else True
        self._changes = self._changes.sort_values(by=[INTERVAL, trade_data.PRICE],
                                                  ascending=[True, sort_order])
        line = ""
        for block in range(0, int(len(INTERVALS)/NUMBER_OF_COLUMNS)):
            for row_no in range(1, ROWS_PER_COLUMN):
                self.print_row(line, row_no, INTERVALS[block * NUMBER_OF_COLUMNS:(block + 1) * NUMBER_OF_COLUMNS])

    def print_row(self, line, row_no, intervals):
        header_line = ""
        for interval in intervals:
            if row_no == FIRST_ROW:
                header_line += "{0} min. Ticker  Price     Volumne     Pump         ".format(
                        str(float(interval) / 60.0), ROWS_PER_COLUMN)
            row = self.get_row_for_interval(interval, row_no)
            if not row.empty:
                line += "{0: <17}{1: >+3.3f}    {2: >+2.3f}      {3: <6}      " \
                        .format(row[TICKER_SYMBOL], row[trade_data.PRICE], row[trade_data.VOLUME],
                                "***" if row[PUMP] else "")
            if INTERVAL_TO_COLUMN_NO[interval] == NUMBER_OF_COLUMNS:
                if row_no == FIRST_ROW:
                    print("")
                    print(header_line)
                    print("---------------------------------------------------------------------------------------"
                          "-----------------------------------------------------------")
                    header_line = ""
                print(line)
                line = ""

    def get_row_for_interval(self, interval, row_no):
        top = self._changes[self._changes[INTERVAL] == interval].head(ROWS_PER_COLUMN)
        if row_no > len(top):
            return pd.Series([])
        return top.iloc[row_no - 1]

    @staticmethod
    def get_percentage(start, end):
        return ((end - start) / start) * 100.0

    # def check_n_step_change(self, ticker_symbol):
    #     """
    #     This method checks whether there is a step-wise price increase. Over n-periods, a check is made
    #     to see whether there is an ever-increasing pattern, where the volume of n-periods is at least greater
    #     than the average volumne of the (t-now - square(n) periods) until the (t-now - n periods)
    #     """
    #
    #     if TradeData.get_number_of_rows(self.trade_data, ticker_symbol) < np.square(STEP_SIZE):
    #         return None
    #
    #     historical_volume_mean = \
    #         self.trade_data[self.trade_data[TICKER_SYMBOL] == ticker_symbol] \
    #             .tail(np.square(STEP_SIZE)).head(np.square(STEP_SIZE)-STEP_SIZE)[VOLUME].mean()
    #
    #     start_price = self.trade_data[self.trade_data[TICKER_SYMBOL] == ticker_symbol] \
    #                       .tail(STEP_SIZE+1).head(1)[PRICE].values[0]
    #     for i in reversed(range(STEP_SIZE, 0, -1)):
    #         price = self.\
    #                 _trade_data[self.trade_data[TICKER_SYMBOL] == ticker_symbol].tail
    # (STEP_SIZE - i + 1).head(1)[PRICE].values[0]
    #         if price < (start_price * ((PRICE_PERCENTAGE_CHANGE_STEP + 100) / 100)):
    #             return None
    #         start_price = price
    #         volume = self.trade_data[self.trade_data[TICKER_SYMBOL] == ticker_symbol].tail(STEP_SIZE - i + 1) \
    #                                    .head(1)[VOLUME].values[0]
    #         if volume < (historical_volume_mean * ((VOLUME_MEAN_PERCENTAGE_CHANGE_STEP + 100) / 100)):
    #             return None
    #
    #     print(str(datetime.datetime.now()))
    #     print(STEP_CHANGE_MESSAGE.format(ticker_symbol, start_price, self.
    #                                      _trade_data[self.trade_data[TICKER_SYMBOL] ==
    # ticker_symbol].tail(1)[PRICE].values[0]))
    #
    #     return TradeDirection.UP

    def cross_check_ticker_symbols(self):
        symbols = TradeClient.instance().get_symbols()
        for info in symbols:
            ticker_symbol = TickerSymbolConfiguration.instance().get_adjusted_trade_data_ticker_symbol(info)
            if not TickerSymbolConfiguration.instance().exists_in_configuration(ticker_symbol):
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

    @classmethod
    def exists_ticker_symbol_in_trade_data(cls, ticker_symbol, ticker_symbols_trade_data):
        for info in ticker_symbols_trade_data:
            if TickerSymbolConfiguration.instance().get_adjusted_trade_data_ticker_symbol(info) == ticker_symbol:
                return True
        return False

    @property
    def historical_trade_data(self):
        return self._historical_trade_data

    @property
    def pumpers(self):
        return self._pumpers
