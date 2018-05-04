import threading
from dao.dao import Dao
from dao.pump import Pump
import time
from ticker_symbol_configuration import TickerSymbolConfiguration, BTC
from trade_client import TradeClient, LAST_PRICE

PRICE = "price"
VOLUME = "volume"


class Pumper:

    def __init__(self, trade_data, data_pump=None, __ticker_symbol=None, initial_price=None, first_pump_price=None,
                 initial_volume=None, first_pump_volume=None, quantity=None):
        self.trade_data = trade_data
        if data_pump:
            self._data_pump = data_pump
        else:
            self._data_pump = Pump.new(ticker_symbol=__ticker_symbol, initial_price=initial_price,
                                       first_pump_price=first_pump_price, initial_volume=initial_volume,
                                       first_pump_volume=first_pump_volume, quantity=quantity,
                                       stop_loss=100.0)
            Dao.instance().save_pump(self._data_pump)
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def run(self):
        # self._order_client.create_order(ticker_symbol= self._ticker_symbol,
        #                                 price=self._initial_price,
        #                                 quantity=self._quantity)
        while True:
            data = self.get_trade_data()
            if not data:
                print("Error: cannot find ticker symbol in pumper")
            else:
                self.store_historical_ticker_data(data)
            if self.check_stop_loss(data):
                self.close(data)
                return
            time.sleep(5)

    def get_trade_data(self):
        for data in TradeClient.instance().client.get_trade_data(self.ticker_symbol):
            __ticker_symbol = TickerSymbolConfiguration.instance().get_adjusted_trade_data_ticker_symbol(data)
            if not TickerSymbolConfiguration.instance().exists_in_configuration(__ticker_symbol):
                continue
            if TickerSymbolConfiguration.instance().consider_ticket(__ticker_symbol):
                Dao.instance().save_pump_history(self.pump_id, float(data[LAST_PRICE]), float(data[VOLUME]))
                return data
        return None

    def store_historical_ticker_data(self, data):
        Dao.instance().save_pump_history(self.pump_id, float(data[LAST_PRICE]), float(data[VOLUME]))

    @staticmethod
    def reconstruct_running_pumps():
        return [Pumper(pump) for pump in Dao.instance().get_all_running_pumps()]

    def check_stop_loss(self, data):
        current_price = data()[PRICE]
        if current_price < self._data_pump.stop_loss:
            print("Ticker symbol {0}, just tell through stop loss {1}, "
                  "perceived loss in btc value = {2}, usd value = {3}".format(
                        self._data_pump.ticker_symbols,
                        self._data_pump.stop_loss,
                        (current_price - self._data_pump.start_price) * float(self._data_pump.quantity),
                        ((current_price - self._data_pump.start_price) * float(self._data_pump.quantity))
                        * self._data_pump.get_last(BTC, PRICE)))
            return True
        else:
            return False

    def close(self, data):
        self._data_pump.end_price = data[PRICE]
        self._data_pump.profit_pct = \
            ((self._data_pump.end_price - self._data_pump.start_price) / self._data_pump.start_price) * 100.0
        Dao.instance().close_pump(self._data_pump)

    def join(self):
        self._thread.join()

    @property
    def ticker_symbol(self):
        return self._data_pump.ticker_symbols

    @property
    def pump_id(self):
        return self._data_pump.id
