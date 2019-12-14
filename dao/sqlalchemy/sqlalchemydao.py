from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dao.sqlalchemy.pump import Pump
from singleton import Singleton
from system_config import Config, DBUSER, DBHOST, DBPASSWORD, DBNAME, DBPORT
import datetime

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"

STOP_LOSS_END = "ENDED, STOP LOSS HIT"
CLOSED = "CLOSED"
RUNNING = "RUNNING"


@Singleton
class SQLAlchemyDao:

    """ This class contains the logic that takes care of interaction with the database """

    def __init__(self):
        config = Config()
        self._engine = create_engine(DB_URI.format(
            user=config.config[DBUSER],
            password=config.config[DBPASSWORD],
            host=config.config[DBHOST],
            port=config.config[DBPORT],
            db=config.config[DBNAME]
        ))
        self.Session = sessionmaker(bind=self._engine)

    def get_all_running_pumps(self):
        session = self.Session()
        return session.query(Pump).filter_by(status=RUNNING).all()

    def save_pump(self, **kwargs):
        pump = Pump.new(**kwargs)
        session = self.Session()
        session.add(pump)
        session.commit()
        return pump

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
        