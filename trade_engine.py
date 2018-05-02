from singleton import Singleton
import time
import datetime
import pandas as pd
import numpy as np
from trade import TradeDirection
import threading
from dao.dao import Dao
from system_config import Config, BTC_PUMP_QUANTITY

SYMBOL = "symbol"
SYMBOLS = SYMBOL + "s"
LAST_PRICE = "lastPrice"
CURRENT_VOLUME = "quoteVolume"
BTC = "BTC"
USDT = "USDT"
BTCUSD = BTC + USDT

TIME = "time"
TICKER_SYMBOL = "ticker_symbol"
PRICE = "price"
VOLUME = "volume"
VALUE = "value"
PENULTIMATE = 2
INTERVAL = "interval"
PUMP = "pump"

ROWS_PER_COLUMN = 10

INTERVAL_CHANGE_MESSAGE = "{0}: Change {1}: price: {2}, volume {3}"
STEP_CHANGE_MESSAGE = "{0}: step change: step start price: {1}, current price: {2}"

PRICE_PERCENTAGE_CHANGE_PUMP = 0.005
VOLUME_PERCENTAGE_CHANGE_PUMP = 0.005
PRICE_PERCENTAGE_CHANGE_STEP = 0.05
VOLUME_MEAN_PERCENTAGE_CHANGE_STEP = 0.05
STEP_SIZE = 5
NUMBER_OF_COLUMNS = 3
FIRST_ROW = 1

SLEEP_TIME = 30
CANDLE_STICKS_PER_MINUTE = 60 / SLEEP_TIME

INTERVALS = [1*SLEEP_TIME, 2*SLEEP_TIME, 5*SLEEP_TIME, 10*SLEEP_TIME, 20*SLEEP_TIME,
             60*SLEEP_TIME, 120*SLEEP_TIME, 240*SLEEP_TIME, 480*SLEEP_TIME]

GAINERS = "gainers"
LOSERS = "losers"
LIST_MODES = [GAINERS, LOSERS]

PUMP_UPTICK_PRICE_PCT = 1.0

# PERCENTAGE_CHANGE_PRICE = {1*SLEEP_TIME: 0.625, 2*SLEEP_TIME: 1.25,
#                            5*SLEEP_TIME: 2.0, 15*SLEEP_TIME: 3.0, 30*SLEEP_TIME: 5.0}
#
# PERCENTAGE_CHANGE_VOLUME = {1*SLEEP_TIME: 0.1, 2*SLEEP_TIME: 0.2,
#                             5*SLEEP_TIME: 0.1, 15*SLEEP_TIME: 0.1, 30*SLEEP_TIME: 0.1}

PERCENTAGE_CHANGE_PRICE = {1*SLEEP_TIME: 0.1, 2*SLEEP_TIME: 1.25, 5*SLEEP_TIME: 0.0,
                           10*SLEEP_TIME: 0.0, 20*SLEEP_TIME: 0.0, 60*SLEEP_TIME: 0.0,
                           120*SLEEP_TIME: 0.0, 240 * SLEEP_TIME: 0.0, 480 * SLEEP_TIME: 0.0}

PERCENTAGE_CHANGE_VOLUME = {1*SLEEP_TIME: 0.05, 2*SLEEP_TIME: 0.5, 5*SLEEP_TIME: 0.0,
                            10*SLEEP_TIME: 0.0, 20*SLEEP_TIME: 0.0, 60*SLEEP_TIME: 0.0,
                            120*SLEEP_TIME: 0.0, 240 * SLEEP_TIME: 0.0, 480 * SLEEP_TIME: 0.0}

INTERVAL_TO_COLUMN_NO = {1*SLEEP_TIME: 1, 2*SLEEP_TIME: 2, 5*SLEEP_TIME: 3,
                         10*SLEEP_TIME: 1, 20*SLEEP_TIME: 2, 60*SLEEP_TIME: 3,
                         120*SLEEP_TIME: 1, 240 * SLEEP_TIME: 2, 480 * SLEEP_TIME: 3}


@Singleton
class TradeEngine():

    def __init__(self, trade_client, order_client):
        self._trade_client = trade_client
        self._order_client = order_client
        self._thread = threading.Thread(target=self.do_run)
        self._thread.start()
        self._ticker_symbols = self.load_ticker_symbols()
        self._history = pd.DataFrame()
        self._changes = pd.DataFrame()
        self._trade_client = trade_client
        self.cross_check_ticker_symbols()
        self._list_mode = GAINERS
        self._trades = []
        self._pumps = Dao.instance().get_all_running_pumps()

    def do_run(self):
        while True:
            self.add_latest_info()
            for ticker_symbol in self._ticker_symbols:
                for i in INTERVALS:
                    self.check_change_interval(ticker_symbol, i)
            self.report_changes()
            self._changes = pd.DataFrame()
            time.sleep(SLEEP_TIME)

    def check_pumps(self):
        for pump in self._pumps:
            if self.get_last(ticker_symbol=pump.ticker_symbol, what=PRICE) < pump.stop_loss:
                print("Ticker symbol {0}, just tell through stop loss {1}, "
                      "perceived loss in btc value = {2}, usd value = {3}".format(
                        pump.ticker_symbol,
                        pump.stop_loss,
                        (pump.start_price - pump.start_price) * float(pump.quantity),
                        ((pump.start_price - pump.start_price) * float(pump.quantity)) * self.get_last(BTC, PRICE)))

    def join(self):
        self._thread.join()

    def change_list_mode(self, list_mode):
        self._list_mode = list_mode

    def check_change_interval(self, ticker_symbol, interval):

        candle_sticks = int(interval / SLEEP_TIME)
        if len(self._history[self._history[TICKER_SYMBOL] == ticker_symbol]) < \
                        candle_sticks + 1:
            return

        last_price = self.get_last(ticker_symbol, PRICE)
        previous_price = self.get_last_minus_n(ticker_symbol, PRICE, candle_sticks)
        last_volume = self.get_last(ticker_symbol, VOLUME)
        previous_volume = self.get_last_minus_n(ticker_symbol, VOLUME, candle_sticks)

        pump = False
        if last_price > (previous_price * ((PERCENTAGE_CHANGE_PRICE[interval] + 100) / 100)) and \
           last_volume > (previous_volume * ((PERCENTAGE_CHANGE_VOLUME[interval] + 100) / 100)) and \
                (interval == SLEEP_TIME or interval == SLEEP_TIME*2):
            self.create_new_pump(ticker_symbol, previous_price, last_price,
                                 self.get_target_quantity(
                                     Config.instance().config[BTC_PUMP_QUANTITY],
                                     last_price),
                                 previous_volume, last_volume)

        change = pd.DataFrame({
            TIME: datetime.datetime.now(),
            TICKER_SYMBOL: {VALUE: ticker_symbol},
            INTERVAL: {VALUE: interval},
            PRICE: {VALUE: self.get_percentage(previous_price, last_price)},
            VOLUME: {VALUE: self.get_percentage(previous_volume, last_volume)},
            PUMP: {VALUE: pump}})
        change = change.set_index([TIME])
        self._changes = self._changes.append(change)
        return pump

    def create_new_pump(self, ticker_symbol, previous_price, last_price, quantity, previous_volume, last_volume):

        for pump in self._pumps:
            if pump.ticker_symbol == ticker_symbol:
                print("ticker symbol {0} already pumping".format(ticker_symbol))
                return
        self._order_client.create_order(ticker_symbol=ticker_symbol,
                                        price=last_price,
                                        quantity=quantity)
        Dao.instance().save_pump(ticker_symbol=ticker_symbol, start_price=last_price,
                                 initial_pump_price_pct=self.get_percentage(previous_price, last_price),
                                 initial_pump_volume_pct=self.get_percentage(previous_volume, last_volume),
                                 stop_loss=100.0)

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
        self._changes = self._changes.sort_values(by=[INTERVAL, PRICE],
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
                        .format(row[TICKER_SYMBOL], row[PRICE], row[VOLUME], "***" if row[PUMP] else "")
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

    def check_n_step_change(self, ticker_symbol):
        """
        This method checks whether there is a step-wise price increase. Over n-periods, a check is made
        to see whether there is an ever-increasing pattern, where the volume of n-periods is at least greater
        than the average volumne of the (t-now - square(n) periods) until the (t-now - n periods)
        """

        if len(self._history[self._history[TICKER_SYMBOL] == ticker_symbol]) < np.square(STEP_SIZE):
            return None

        historical_volume_mean = \
            self._history[self._history[TICKER_SYMBOL] == ticker_symbol] \
                .tail(np.square(STEP_SIZE)).head(np.square(STEP_SIZE)-STEP_SIZE)[VOLUME].mean()

        start_price = self._history[self._history[TICKER_SYMBOL] == ticker_symbol] \
                          .tail(STEP_SIZE+1).head(1)[PRICE].values[0]
        for i in reversed(range(STEP_SIZE, 0, -1)):
            price = self.\
                    _history[self._history[TICKER_SYMBOL] == ticker_symbol].tail(STEP_SIZE-i+1).head(1)[PRICE].values[0]
            if price < (start_price * ((PRICE_PERCENTAGE_CHANGE_STEP + 100) / 100)):
                return None
            start_price = price
            volume = self._history[self._history[TICKER_SYMBOL] == ticker_symbol].tail(STEP_SIZE-i+1) \
                                       .head(1)[VOLUME].values[0]
            if volume < (historical_volume_mean * ((VOLUME_MEAN_PERCENTAGE_CHANGE_STEP + 100) / 100)):
                return None

        print(str(datetime.datetime.now()))
        print(STEP_CHANGE_MESSAGE.format(ticker_symbol, start_price, self.
                    _history[self._history[TICKER_SYMBOL] == ticker_symbol].tail(1)[PRICE].values[0]))

        return TradeDirection.UP

    def cross_check_ticker_symbols(self):
        symbols = self._trade_client.get_exchange_info()[SYMBOLS]
        for info in symbols:
            ticker_symbol = self.get_adjusted_trade_data_ticker_symbol(info)
            if not self.exists_ticker_symbol_in_configuration(ticker_symbol):
                print("Ticker symbol {0} found in trade data is not a configured ticker symbol".format(ticker_symbol))

        temp_ticker_symbols = []
        for ticker_symbol in self._ticker_symbols:
            if not self.exists_ticker_symbol_in_trade_data(ticker_symbol, symbols):
                print("Ticker symbol {0} found in configuration is not present in trade data as a ticker symbol".
                      format(ticker_symbol))
            else:
                temp_ticker_symbols.append(ticker_symbol)
        self._ticker_symbols = temp_ticker_symbols

    def add_latest_info(self):
        for info in self._trade_client.get_ticker():
            ticker_symbol = self.get_adjusted_trade_data_ticker_symbol(info)
            if not self.exists_ticker_symbol_in_configuration(ticker_symbol):
                continue
            if self.consider_ticket(ticker_symbol):
                row = pd.DataFrame({
                    TIME: datetime.datetime.now(),
                    TICKER_SYMBOL: {VALUE: ticker_symbol},
                    PRICE: {VALUE: float(info[LAST_PRICE])},
                    VOLUME: {VALUE: float(info[CURRENT_VOLUME])}})
                row = row.set_index([TIME])
                self._history = self._history.append(row)

    def consider_ticket(self, _ticker_symbol):
        for ticker_symbol in self._ticker_symbols:
            if ticker_symbol == _ticker_symbol:
                return True
        return False

    def exists_ticker_symbol_in_configuration(self, ticker_symbol):
        for _ticker_symbol in self._ticker_symbols:
            if _ticker_symbol == ticker_symbol:
                return True
        return False

    def get_last(self, ticker_symbol, what):
        return self._history[self._history[TICKER_SYMBOL] == ticker_symbol].tail(1)[what].values[0]

    def get_penultimate(self, ticker_symbol, what):
        return self.get_last_minus_n(ticker_symbol, what, PENULTIMATE)

    def get_last_minus_n(self, ticker_symbol, what, n):
        return self._history[self._history[TICKER_SYMBOL] == ticker_symbol].tail(n+1).head(1)[what].values[0]

    @staticmethod
    def get_target_quantity(btc_quantity, last_price):
        return float(btc_quantity) / last_price

    @classmethod
    def exists_ticker_symbol_in_trade_data(cls, ticker_symbol, ticker_symbols_trade_data):
        for info in ticker_symbols_trade_data:
            if cls.get_adjusted_trade_data_ticker_symbol(info) == ticker_symbol:
                return True
        return False

    @classmethod
    def get_adjusted_trade_data_ticker_symbol(cls, info):
        if info[SYMBOL] == BTCUSD:
            _ticker_symbol = info[SYMBOL].replace(USDT, "")
        else:
            _ticker_symbol = info[SYMBOL].replace(BTC, "")
        return _ticker_symbol

    @classmethod
    def load_ticker_symbols(cls):

        return [ticker.strip() for ticker in [
            'BTC',
            'ETH',
            'XRP',
            'BCC',
            'EOS',
            'LTC',
            'ADA',
            'XLM',
            'IOTA',
            'NEO',
            'TRX',
            'XMR',
            'DASH',
            'XEM',
            'ETC',
            'VEN',
            'OMG',
            'QTUM',
            'BNB',
            'ICX',
            'BTG',
            'LSK',
            'ZEC',
            'XVG',
            'BCN',
            'STEEM',
            'NANO',
            'BTM',
            'BTCP',
            'SC',
            'PPT',
            'WAN',
            'BCD',
            'BTS',
            'ZIL',
            'DOGE',
            'MKR',
            'STRAT',
            'ONT',
            'AE',
            'DCR',
            'ZRX',
            'WAVES',
            'DGD',
            'XIN',
            'RHOC',
            'SNT',
            'AION',
            'REP',
            'HSR',
            'GNT',
            'LRC',
            'IOST',
            'WTC',
            'BAT',
            'DGB',
            'KMD',
            'ARDR',
            'ARK',
            'KNC',
            'MITH',
            'KCS',
            'CENNZ',
            'MONA',
            'PIVX',
            'SUB',
            'DRGN',
            'SYS',
            'DCN',
            'ELF',
            'CNX',
            'GAS',
            'QASH',
            'ETHOS',
            'STORM',
            'NPXS',
            'FCT',
            'NAS',
            'CTXC',
            'VERI',
            'BNT',
            'RDD',
            'WAX',
            'ELA',
            'GXS',
            'FUN',
            'SALT',
            'XZC',
            'NXT',
            'POWR',
            'KIN',
            'ENG',
            'MCO',
            'GTO',
            'R',
            'NCASH',
            'GBYTE',
            'ETN',
            'MAID'
        ]]

    @property
    def tickers_symbols(self):
        return self._ticker_symbols

    @property
    def trade_history(self):
        return self._history
