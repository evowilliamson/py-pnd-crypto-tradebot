from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Float


class Pump(declarative_base()):
    """ This dao class represents the pump entity in the database """

    __tablename__ = 'pump'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol = Column(String(255))
    start_time = Column(DateTime)
    quantity = Column(Float)
    start_price = Column(Float)
    initial_pump_price_pct = Column(Float)
    initial_pump_volume_pct = Column(Float)
    stop_loss = Column(Float)
    profit_pct = Column(Float)
    end_time = Column(DateTime)
    end_price = Column(Float)
    status = Column(String(50))

    def update_stop_loss(self, profit_pct, end_price, end_time, status):
        self.profit_pct = profit_pct
        self.end_price = end_price
        self.end_time = end_time
        self.status = status



