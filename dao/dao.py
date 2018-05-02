from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from dao.pump import Pump
from singleton import Singleton
from system_config import Config

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"
DBUSER = "dbuser"
DBPASSWORD = "dbpassword"
DBHOST = "dbhost"
DBNAME = "dbname"
DBPORT = "dbport"


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

    def save_new_pump(self, pump):
        pump_orm = Pump(ticker_symbol=pump.ticker_symbol, start_time=datetime.datetime.now(),
                        start_price=float(str(pump.start_price)),
                        initial_pump_price_pct=float(str(pump.initial_pump_price_pct)),
                        initial_pump_volume_pct=float(str(pump.initial_pump_volume_pct)),
                        amount_btc=float(str(pump.amount_btc)), stop_loss=float(str(pump.stop_loss)))
        self._session.add(pump_orm)
        self._session.commit()

    def save_running_pump(self, pump):
        pump_orm = Pump(ticker_symbol=pump.ticker_symbol, start_time=datetime.datetime.now(),
                        start_price=float(pump.start_price), amount_btc=float(pump.amount_btc),
                        stop_loss=float(pump.stop_loss), profit_pct=float(pump.profit_pct))
        self._session.add(pump_orm)
        self._session.commit()


