from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from singleton import Singleton
from system_config import Config, DBUSER, DBHOST, DBPASSWORD, DBNAME, DBPORT
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Float
import datetime

DB_URI_MYSQL = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"
DB_URI_SQLITE = "sqlite:///pnd.db"

STOP_LOSS_END = "ENDED, STOP LOSS HIT"
CLOSED = "CLOSED"
RUNNING = "RUNNING"

Base = declarative_base()

class Pump(Base):
    """ This dao class represents the pump entity in the database """

    __tablename__ = 'pump'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol = Column(String(255))
    start_time = Column(DateTime)
    quantity = Column(Float)
    initial_price = Column(Float)
    first_pump_price = Column(Float)
    buy_price = Column(Float)
    initial_volume = Column(Float)
    first_pump_volume = Column(Float)
    stop_loss = Column(Float)
    end_time = Column(DateTime)
    end_price = Column(Float)
    profit_pct = Column(Float)
    status = Column(String(50))

    def update(self, end_price, end_time, profit_pct, status, stop_loss):
        self.end_price = end_price
        self.end_time = end_time
        self.profit_pct = profit_pct
        self.status = status
        self.stop_loss = stop_loss

    @staticmethod
    def new(ticker_symbol, initial_price, first_pump_price, buy_price, initial_volume,
            first_pump_volume, quantity, stop_loss, status):
        return Pump(ticker_symbol=ticker_symbol,
                    initial_price=initial_price,
                    first_pump_price=first_pump_price,
                    buy_price=buy_price,
                    initial_volume=initial_volume,
                    first_pump_volume=first_pump_volume,
                    quantity=quantity,
                    stop_loss=stop_loss,
                    start_time=datetime.datetime.now(),
                    status=status)

class PumpDetails(Base):
    """ This dao class represents the pump history entity in the database """

    __tablename__ = 'pump_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pump_id = Column(Integer)
    timestamp = Column(DateTime)
    price = Column(Float)
    volume = Column(Float)

    @staticmethod
    def new(pump_id, price, volume):
        return PumpDetails(
                    pump_id=pump_id,
                    timestamp=datetime.datetime.now(),
                    price=price,
                    volume=volume)


@Singleton
class Dao:
    """ This class contains the logic that takes care of interaction with the database """

    def __init__(self):
        config = Config()
        # Mysql
        # self._engine = create_engine(DB_URI_MYSQL.format(
        #     user=config.config[DBUSER],
        #     password=config.config[DBPASSWORD],
        #     host=config.config[DBHOST],
        #     port=config.config[DBPORT],
        #     db=config.config[DBNAME]
        # ))
        self._engine = create_engine(DB_URI_SQLITE)  
        Base.metadata.create_all(self._engine)              
        self.Session = sessionmaker(bind=self._engine)

    def get_all_running_pumps(self):
        session = self.Session()
        return session.query(Pump).filter_by(status=RUNNING).all()

    def save_pump(self, data_pump):
        session = self.Session()
        session.add(data_pump)
        session.commit()

    def save_pump_details(self, pump_id, price, volume):
        session = self.Session()
        session.add(PumpDetails.new(pump_id, price, volume))
        session.commit()

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

