from threading import RLock
from singleton import Singleton
from system_config import Config
import datetime

CLOSED = "CLOSED"

@Singleton
class PythonDao(object):

    def __init__(self):
        config = Config()
        self._pumps = {}

    def get_pump(self, pump_id):
        return self._pumps[pump_id]

    def save_pump(self, pump):
        lock = RLock()
        lock.acquire()
        pump_id = max(self._pumps, default=0, key=int) + 1
        pump["id"] = pump_id
        pump["start_time"] = datetime.datetime.now()
        self._pumps[pump_id] = pump
        lock.release()
        return pump

    def close_pump(self, data_pump):
        lock = RLock()
        lock.acquire()        
        persisted_data_pump = self._pumps[data_pump["id"]]
        persisted_data_pump["end_price"] = data_pump["end_price"]
        persisted_data_pump["end_time"] = datetime.datetime.now()
        persisted_data_pump["profit_pct"] = data_pump["profit_pct"]
        persisted_data_pump["status"] = CLOSED
        lock.release()
        
    def update_stop_loss(self, data_pump):
        lock = RLock()
        lock.acquire()        
        persisted_data_pump = self._pumps[data_pump["id"]]
        persisted_data_pump["stop_loss"] = data_pump["stop_loss"]
        lock.release()

    def delete_pumps(self):
        lock = RLock()
        lock.acquire()        
        self._pumps = {}
        lock.release()

    def get_all_running_pumps(self):
        return self._pumps.values()
