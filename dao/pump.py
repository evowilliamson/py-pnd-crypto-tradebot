from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Float


class Pump(declarative_base()):
    """ This dao class represents the pump entity in the database """

    __tablename__ = 'pump'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol = Column(String(255))
    start_time = Column(DateTime)
    start_price = Column(Float)
    amount_btc = Column(Float)
    initial_pump_price_pct = Column(Float)
    initial_pump_volume_pct = Column(Float)
    stop_loss = Column(Float)
    profit_pct = Column(Float)
    end_time = Column(DateTime)
    end_price = Column(Float)

    # def __init__(self, __id, description, component, start_time, end_time, emails, owner, validated):
    #     self._id = __id
    #     self._description = description
    #     self._component = component
    #     self._start_time = start_time
    #     self._end_time = end_time
    #     self._emails = emails
    #     self._owner = owner
    #     self._validated = validated




