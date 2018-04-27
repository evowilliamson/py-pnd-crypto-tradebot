from system import System
from trade_engine import TradeEngine

while True:
    TradeEngine.instance().trade(System.instance().trade_client)



