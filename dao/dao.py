from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dao.pump import Pump
from singleton import Singleton
from system_config import Config, DBUSER, DBHOST, DBPASSWORD, DBNAME, DBPORT
from dao.pump_history import PumpDetails

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"

STOP_LOSS_END = "ENDED, STOP LOSS HIT"
CLOSED = "CLOSED"
RUNNING = "RUNNING"


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

    def save_pump(self, data_pump):
        self._session.add(data_pump)
        self._session.commit()

    def save_pump_details(self, pump_id, price, volume):
        self._session.add(PumpDetails.new(pump_id, price, volume))
        self._session.commit()

    def close_pump(self, data_pump):
        data_pump.status = CLOSED
        data_pump.update()
        self._session.commit()




