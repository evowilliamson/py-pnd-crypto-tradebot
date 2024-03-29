import threading
from dao.sqlalchemy.sqlalchemydao import RUNNING
from dao.dao_selector import dao
import time
from ticker_symbol_configuration import TickerSymbolConfiguration
from trade_client import TradeClient
import datetime

class Pumper:

    def __init__(self, trade_engine, data_pump=None, ticker_symbol=None, initial_price=None, first_pump_price=None,
                 initial_volume=None, first_pump_volume=None, quantity=None):
        self._trade_engine = trade_engine
        if data_pump is None:
            self._data_pump = dao().save_pump({
                                "ticker_symbol": ticker_symbol,
                                "initial_price": float(str(initial_price)),
                                "first_pump_price": float(str(first_pump_price)),
                                "buy_price": float(str(first_pump_price*1.01)),
                                "initial_volume": float(str(initial_volume)),
                                "first_pump_volume": float(str(first_pump_volume)),
                                "quantity": float(str(quantity)),
                                "stop_loss": float(str(initial_price*0.9925)),
                                "status": RUNNING})
            print("new pumper for ticker symbol {0}, bought at {1}".format(ticker_symbol, str(first_pump_price*1.01)))
        else:
            print("loaded pumper for ticker symbol {0} from db".format(ticker_symbol))
            self._data_pump = data_pump
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def run(self):
        while True:
            data = self.get_trade_data()
            if not data:
                print("Error: cannot find ticker symbol in pumper")
            if self.check_stop_loss(data):
                self.close(data)
                return
            self.adjust_stop_loss(data)
            time.sleep(5)

    def get_trade_data(self):
        data = TradeClient().get_trade_data(
                TickerSymbolConfiguration().get_ticker_symbol_in_market(self.ticker_symbol))
        __ticker_symbol = TickerSymbolConfiguration().get_adjusted_trade_data_ticker_symbol(data)
        if not TickerSymbolConfiguration().exists_in_configuration(__ticker_symbol):
            print("ticker symbol {0} from trade data does not exist in conf. Error in pumper".format(__ticker_symbol))
            return None
        return data

    @staticmethod
    def reconstruct_running_pumps(trade_engine):
        return [Pumper(trade_engine=trade_engine, data_pump=data_pump) 
            for data_pump in dao().get_all_running_pumps()]

    def check_stop_loss(self, data):
        current_price = float(data[TradeClient().PRICE])
        if current_price < self._data_pump["stop_loss"]:
            print("Ticker symbol {0}, just tell through stop loss {1}, "
                  "perceived loss in btc value = {2}".format(
                        self._data_pump["ticker_symbol"],
                        self._data_pump["stop_loss"],
                        (current_price - self._data_pump["initial_price"]) * float(self._data_pump["quantity"])))
            return True
        else:
            return False
    def adjust_stop_loss(self, data):
        current_price = float(data[TradeClient().PRICE])
        old_stop_loss = self._data_pump["stop_loss"]
        if self._data_pump["start_time"] + datetime.timedelta(minutes=1) < datetime.datetime.now():
            self._data_pump["stop_loss"] = max(self._data_pump["stop_loss"], current_price * 0.95)
            if old_stop_loss < self._data_pump["stop_loss"]:
                print("Stop loss of ticker symbol {} adjusted to {}".
                      format(self.ticker_symbol, self._data_pump["stop_loss"]))
                dao().update_stop_loss(self._data_pump)

    def close(self, data):
        print("Closing pump {0}".format(self._data_pump["ticker_symbol"]))
        self._data_pump["end_price"] = float(data[TradeClient().PRICE])
        self._data_pump["profit_pct"] = \
            ((self._data_pump["end_price"] - self._data_pump["initial_price"]) / 
              self._data_pump["initial_price"]) * 100.0
        dao().close_pump(self._data_pump)
        self.pumpers.remove(self)

    def join(self):
        self._thread.join()

    @property
    def ticker_symbol(self):
        return self._data_pump["ticker_symbol"]

    @property
    def pump_id(self):
        return self._data_pump["id"]

    @property
    def trade_engine(self):
        return self._trade_engine

    @property
    def pumpers(self):
        return self.trade_engine.pumpers
