from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Float
import datetime


class PumpHistory(declarative_base()):
    """ This dao class represents the pump history entity in the database """

    __tablename__ = 'pump_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pump_id = Column(Integer)
    timestamp = Column(DateTime)
    price = Column(Float)
    volume = Column(Float)

    @staticmethod
    def new(pump_id, price, volume):
        return PumpHistory(
                    pump_id=pump_id,
                    timestamp=datetime.datetime.now(),
                    price=price,
                    volume=volume)

