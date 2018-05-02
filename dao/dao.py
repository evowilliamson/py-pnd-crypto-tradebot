from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from dao.pump import Pump
from singleton import Singleton
from system_config import Config, DBUSER, DBHOST, DBPASSWORD, DBNAME, DBPORT

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"

STOP_LOSS_END = "ENDED, STOP LOSS HIT"

@Singleton
class Dao:
    """ This class contains the logic that takes care of interaction with the database """

    def __init__(self):
        config = Config.instance()
        self._engine = create_engine(DB_URI.format(
            user=config.config[DBUSER],
            password=config.config[DBPASSWORD],
            host=config.config[DBHOST],
            port=config.config[DBPORT],
            db=config.config[DBNAME]
        ))
        self.Session = sessionmaker(bind=self._engine)
        self._session = self.Session()

    def get_all_running_pumps(self):
        return self._session.query(Pump).filter_by(end_time=None).all()

    def save_pump(self, ticker_symbol, start_price, quantity,
                  initial_pump_price_pct, initial_pump_volume_pct, stop_loss):
        pump_orm = Pump(ticker_symbol=ticker_symbol, start_time=datetime.datetime.now(),
                        start_price=float(str(start_price)), quantity=float(str(quantity)),
                        initial_pump_price_pct=float(str(initial_pump_price_pct)),
                        initial_pump_volume_pct=float(str(initial_pump_volume_pct)),
                        stop_loss=float(str(stop_loss)))
        self._session.add(pump_orm)
        self._session.commit()

    def update_pump_stop_loss(self, pump_orm, pump):
        pump_orm.update_stop_loss(pump.profit_pct, pump.end_price, pump.end_time, pump.status)
        self._session.commit()


