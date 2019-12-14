from singleton import Singleton

SYMBOL = "symbol"
SYMBOLS = SYMBOL + "s"

BTC = "BTC"
USDT = "USDT"
BTCUSD = BTC + USDT


@Singleton
class TickerSymbolConfiguration:

    def __init__(self):
        self._ticker_symbols = [ticker.strip() for ticker in 
        [
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

    def get_adjusted_trade_data_ticker_symbol(self, info):
        if info[SYMBOL] == BTCUSD:
            ticker_symbol = info[SYMBOL].replace(USDT, "")
        else:
            ticker_symbol = info[SYMBOL].replace(BTC, "")
        return ticker_symbol

    def get_ticker_symbol_in_market(self, ticker_symbol):
        if ticker_symbol == BTC:
            return BTCUSD
        else:
            return ticker_symbol + BTC

    def exists_in_configuration(self, ticker_symbol):
        for _ticker_symbol in self.ticker_symbols:
            if _ticker_symbol == ticker_symbol:
                return True
        return False

    @property
    def ticker_symbols(self):
        return self._ticker_symbols
