from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Float
import datetime


class Pump(declarative_base()):
    """ This dao class represents the pump entity in the database """

    __tablename__ = 'pump'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol = Column(String(255))
    start_time = Column(DateTime)
    quantity = Column(Float)
    initial_price = Column(Float)
    first_pump_price = Column(Float)
    initial_volume = Column(Float)
    first_pump_volume = Column(Float)
    stop_loss = Column(Float)
    end_time = Column(DateTime)
    end_price = Column(Float)
    profit_pct = Column(Float)
    status = Column(String(50))

    def update(self, end_price, end_time, profit_pct, status):
        self.end_price = end_price
        self.end_time = end_time
        self.profit_pct = profit_pct
        self.status = status

    @staticmethod
    def new(ticker_symbol, initial_price, first_pump_price, initial_volume,
            first_pump_volume, quantity, stop_loss, status):
        return Pump(ticker_symbol=ticker_symbol,
                    initial_price=initial_price,
                    first_pump_price=first_pump_price,
                    initial_volume=initial_volume,
                    first_pump_volume=first_pump_volume,
                    quantity=quantity,
                    stop_loss=stop_loss,
                    start_time=datetime.datetime.now(),
                    status=status)

