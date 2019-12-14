from threading import RLock
from singleton import Singleton
from system_config import Config

@Singleton
class PythonDao(object):

    def __init__(self):
        config = Config()
        self._pumps = {}

    def new_pump(self, **kwargs):
        pass

    def save_pump(self, **kwargs):
        pump = **kwargs
        lock = RLock()
        lock.acquire()
        pump_id = max(self._pumps, default=0, key=int) + 1
        pump["id"] = pump_id
        self._pumps[pump_id] = pump
        lock.release()
        return pump
"""
    def close_pump(self, data_pump):
        session = self.Session()
        persisted_data_pump = session.query(Pump).filter_by(id=data_pump.id).one()
        persisted_data_pump.update(
            end_price=data_pump.end_price,
            end_time=datetime.datetime.now(),
            profit_pct=data_pump.profit_pct,
            status=CLOSED,
            stop_loss=persisted_data_pump.stop_loss)
        session.commit()

    def update_stop_loss(self, data_pump):
        session = self.Session()
        persisted_data_pump = session.query(Pump).filter_by(id=data_pump.id).one()
        persisted_data_pump.update(
            end_price=persisted_data_pump.end_price,
            end_time=persisted_data_pump.end_time,
            profit_pct=persisted_data_pump.profit_pct,
            status=persisted_data_pump.status,
            stop_loss=data_pump.stop_loss)
        session.commit()
        """