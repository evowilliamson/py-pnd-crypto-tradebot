from singleton import Singleton
import time
import datetime
from enum import Enum

SYMBOL = "symbol"
CURRENT_PRICE = "lastPrice"
CURRENT_VOLUME = "quoteVolume"
BTC = "BTC"
USDT = "USDT"
BTCUSD = BTC + USDT

TradeDirection = Enum(["UP", "DOWN"])

PRICE_PERCENTAGE_CHANGE_PND = 0.5
VOLUME_PERCENTAGE_CHANGE_PND = 0.1

SLEEP_TIME = 60

@Singleton
class TradeEngine:

    def __init__(self):
        self._ticker_symbols = self.load_ticker_symbols()
        self._history = self.initialize_history()
        self._trade_client = None

    def initialize_history(self):

        history = {}
        for ticker_symbol in self._ticker_symbols:
            history[ticker_symbol] = []
        return history

    def trade(self, trade_client):
        self._trade_client = trade_client

        while True:
            self.add_latest_info()
            for ticker_symbol in self._ticker_symbols:
                signal = self.change_signal(ticker_symbol)
                if signal:
                    self.trade_ticker_symbol(signal)
            time.sleep(SLEEP_TIME)

    def change_signal(self, ticker_symbol):
        return TradeDirection.UP

    def check_sudden_pnd(self, ticker_symbol):

        if len(self._history[ticker_symbol]) < 2:
            return False

        current_price = float(self._history[ticker_symbol][-1][CURRENT_PRICE])
        previous_price = float(self._history[ticker_symbol][-2][CURRENT_PRICE])
        current_volume = float(self._history[ticker_symbol][-1][CURRENT_VOLUME])
        previous_volume = float(self._history[ticker_symbol][-2][CURRENT_VOLUME])

        if (current_price > (previous_price * ((PRICE_PERCENTAGE_CHANGE_PND + 100) / 100)) and
                (float(current_volume) > (float(previous_volume) * ((VOLUME_PERCENTAGE_CHANGE_PND + 100) / 100)))):
            print(str(datetime.datetime.now()) + "**** UP!")
            print("Last: " + str(last))
            print("Now: " + str(now))
        elif (float(now_price) < (float(last_price) * ((100 - PRICE_PERCENTAGE_CHANGE) / 100)) and
                  (float(now_quoteVolume) > (float(last_quoteVolume) * ((VOLUME_PERCENTAGE_CHANGE + 100) / 100)))):
            print(str(datetime.datetime.now()) + "**** DOWN!")
            print("Last: " + str(last))
            print("Now: " + str(now))

    def trade_ticker_symbol(self, ticker_symbol):
        return True

    def add_latest_info(self):
        for info in self._trade_client.get_ticker():
            if info["symbol"] == BTCUSD:
                ticker_symbol = info["symbol"].replace(USDT, "")
            else:
                ticker_symbol = info["symbol"].replace(BTC, "")
            if self.consider_ticket(ticker_symbol):
                self._history[ticker_symbol].append(info)

    def consider_ticket(self, _ticker_symbol):
        for ticker_symbol in self._ticker_symbols:
            if ticker_symbol == _ticker_symbol:
                return True
        return False

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
            'MIOTA',
            'NEO',
            'TRX',
            'XMR',
            'DASH',
            'XEM',
            'USDT',
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


