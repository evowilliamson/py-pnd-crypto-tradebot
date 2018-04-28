from singleton import Singleton
import time
import datetime
import pandas as pd
import numpy as np
from trade import TradeDirection
from trade import TradeStrategy
from trade import Trade

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

SUDDEN_CHANGE_MESSAGE = "{0}: Sudden change {1}: previous price: {2}, current price: {3}, " \
                        "previous volume {4}, current volume {5}"
STEP_CHANGE_MESSAGE = "{0}: step change: step start price: {1}, current price: {2}"

PRICE_PERCENTAGE_CHANGE_PND = 0.3
VOLUME_PERCENTAGE_CHANGE_PND = 0.1
PRICE_PERCENTAGE_CHANGE_STEP = 0.05
VOLUME_MEAN_PERCENTAGE_CHANGE_STEP = 0.05
STEP_SIZE = 5

SLEEP_TIME = 25


@Singleton
class TradeEngine:

    def __init__(self):
        self._ticker_symbols = self.load_ticker_symbols()
        self._history = pd.DataFrame()
        self._trade_client = None

    def trade(self, trade_client):
        self._trade_client = trade_client
        self.cross_check_ticker_symbols()
        while True:
            self.add_latest_info()
            for ticker_symbol in self._ticker_symbols:
                trade_strategy, trade_direction, previous_price, last_price = self.detect_change(ticker_symbol)
                if trade_direction:
                    print("Changed detected for : {0}".format(ticker_symbol))
                    trade = Trade(self, trade_direction, ticker_symbol, trade_strategy,
                                  previous_price, last_price)
                    a = 100
            time.sleep(SLEEP_TIME)

    def detect_change(self, ticker_symbol):
        trade_direction, previous_price, last_price = self.check_sudden_change(ticker_symbol)
        if trade_direction:
            print("PND for ticker sybmbol : {0} with trade direction {1}".format(ticker_symbol, str(trade_direction)))
            return TradeStrategy.PND, trade_direction, previous_price, last_price
        trade_direction = self.check_n_step_change(ticker_symbol)
        if trade_direction:
            print("Step increase for ticker sybmbol : {0}".format(ticker_symbol))
            return TradeStrategy.STEP, trade_direction, None, None
        return None, None, None, None

    def check_sudden_change(self, ticker_symbol):

        if len(self._history[self._history[TICKER_SYMBOL] == ticker_symbol]) < 2:
            return None, None, None

        last_price = self.get_last(ticker_symbol, PRICE)
        previous_price = self.get_penultimate(ticker_symbol, PRICE)
        last_volume = self.get_last(ticker_symbol, VOLUME)
        previous_volume = self.get_penultimate(ticker_symbol, VOLUME)

        if last_price > (previous_price * ((PRICE_PERCENTAGE_CHANGE_PND + 100) / 100)) and \
           last_volume > (previous_volume * ((VOLUME_PERCENTAGE_CHANGE_PND + 100) / 100)):
            print(SUDDEN_CHANGE_MESSAGE.format(ticker_symbol, TradeDirection.UP, previous_price, last_price,
                                               previous_volume, last_volume))
            self.print_current_and_previous_info(ticker_symbol, TradeDirection.UP)
            return TradeDirection.UP, previous_price, last_price
        elif last_price < (previous_price * ((100 - PRICE_PERCENTAGE_CHANGE_PND) / 100)) and \
             last_volume > (previous_volume * ((VOLUME_PERCENTAGE_CHANGE_PND + 100) / 100)):
            print(SUDDEN_CHANGE_MESSAGE.format(ticker_symbol, TradeDirection.DOWN, previous_price, last_price,
                                               previous_volume, last_volume))
            self.print_current_and_previous_info(ticker_symbol, TradeDirection.DOWN)
            return TradeDirection.DOWN, previous_price, last_price
        else:
            return None, None, None

    # def create_row(self, value):
    #
    #     row = pd.DataFrame({
    #         TIME: datetime.datetime.now(),
    #         TICKER_SYMBOL: {VALUE: "BTC"},
    #         PRICE: {VALUE: value},
    #         VOLUME: {VALUE: value}})
    #     row = row.set_index([TIME])
    #     self._history = self._history.append(row)

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

    def print_current_and_previous_info(self, ticker_symbol, trade_direction):
        print(str(datetime.datetime.now()) + "**** " + str(trade_direction))
        print("Previous: " + str(self.get_penultimate(ticker_symbol, PRICE)))
        print("Last: " + str(self.get_last(ticker_symbol, PRICE)))

    def exists_ticker_symbol_in_configuration(self, ticker_symbol):
        for _ticker_symbol in self._ticker_symbols:
            if _ticker_symbol == ticker_symbol:
                return True
        return False

    def get_last(self, ticker_symbol, what):
        return self._history[self._history[TICKER_SYMBOL] == ticker_symbol].tail(1)[what].values[0]

    def get_penultimate(self, ticker_symbol, what):
        return self._history[self._history[TICKER_SYMBOL] == ticker_symbol].tail(2).head(1)[what].values[0]

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
