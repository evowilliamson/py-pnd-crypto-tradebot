from system import System
from trade_engine import TradeEngine
from command_center import CommandCenter

trade_engine = TradeEngine.instance()
command_center = CommandCenter(trade_engine)

command_center.join()
trade_engine.join()


