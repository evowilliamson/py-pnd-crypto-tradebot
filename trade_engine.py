from singleton import Singleton
import time
import datetime
from enum import Enum
import pandas as pd
import numpy as np
from system import System

SYMBOL = "symbol"
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

TradeDirection = Enum("TradeDirection", "UP DOWN")

PRICE_PERCENTAGE_CHANGE_PND = 0.5
VOLUME_PERCENTAGE_CHANGE_PND = 0.1

SLEEP_TIME = 15

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
                signal = self.change_signal(ticker_symbol)
                if signal:
                    self.trade_ticker_symbol(signal)
            time.sleep(SLEEP_TIME)

    def change_signal(self, ticker_symbol):
        trade_direction = self.check_sudden_change(ticker_symbol)
        if trade_direction:
            System.instance().beep()
            return trade_direction
        trade_direction = self.check_n_step_change(ticker_symbol, 2)
        if trade_direction:
            return trade_direction

    def check_sudden_change(self, ticker_symbol):

        if len(self._history) < 2:
            return False

        ticker_symbol_data_current = self._history[self._history[TICKER_SYMBOL] == ticker_symbol][-1:]
        ticker_symbol_data_previous = self._history[self._history[TICKER_SYMBOL] == ticker_symbol][-2:]
        current_price = ticker_symbol_data_current[PRICE].values[0]
        previous_price = ticker_symbol_data_previous[PRICE].values[0]
        current_volume = ticker_symbol_data_current[VOLUME].values[0]
        previous_volume = ticker_symbol_data_previous[VOLUME].values[0]

        if current_price > (previous_price * ((PRICE_PERCENTAGE_CHANGE_PND + 100) / 100)) and \
           current_volume > (previous_volume * ((VOLUME_PERCENTAGE_CHANGE_PND + 100) / 100)):
            print(SUDDEN_CHANGE_MESSAGE.format(ticker_symbol, TradeDirection.UP, previous_price, current_price,
                                               previous_volume, current_volume))
            self.print_current_and_previous_info(ticker_symbol, TradeDirection.UP)
            return TradeDirection.UP
        elif current_price < (previous_price * ((100 - PRICE_PERCENTAGE_CHANGE_PND) / 100)) and \
             current_volume > (previous_volume * ((VOLUME_PERCENTAGE_CHANGE_PND + 100) / 100)):
            print(SUDDEN_CHANGE_MESSAGE.format(ticker_symbol, TradeDirection.DOWN, previous_price, current_price,
                                               previous_volume, current_volume))
            return TradeDirection.DOWN
        else:
            return None

    def check_n_step_change(self, ticker_symbol, n):
        """
        This method checks whether there is a step-wise price increase. Over n-periods, a check is made
        to see whether there is an ever-increasing pattern, where the volume of n-periods is at least greater
        than the average volumne of the (t-now - square(n) periods) until the (t-now - n periods)
        """
        if True:
            return None

        if len(self._history) < np.square(n):
            return None

        a = self._history[VOLUME][-np.square(n):].average()

        return TradeDirection.UP


    def trade_ticker_symbol(self, ticker_symbol):
        return True

    def cross_check_ticker_symbols(self):
        ticker_symbol_trade_data = self._trade_client.get_ticker()
        for info in ticker_symbol_trade_data:
            ticker_symbol = self.get_adjusted_trade_data_ticker_symbol(info)
            if not self.exists_ticker_symbol_in_configuration(ticker_symbol):
                print("Ticker symbol {0} found in trade data is not a configured ticker symbol".format(ticker_symbol))

        temp_ticker_symbols = []
        for ticker_symbol in self._ticker_symbols:
            if not self.exists_ticker_symbol_in_trade_data(ticker_symbol, ticker_symbol_trade_data):
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
        print(str(datetime.datetime.now()) + "**** " + trade_direction)
        print("Last: " + str(self._history[ticker_symbol][-2]))
        print("Now: " + str(self._history[ticker_symbol][-1]))

    def exists_ticker_symbol_in_configuration(self, ticker_symbol):
        for _ticker_symbol in self._ticker_symbols:
            if _ticker_symbol == ticker_symbol:
                return True
        return False

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

