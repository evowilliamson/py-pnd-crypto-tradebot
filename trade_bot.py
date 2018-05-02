from system import System
from trade_engine import TradeEngine
from command_center import CommandCenter


trade_client = System.instance().trade_client
trade_engine = TradeEngine.instance(trade_client)
command_center = CommandCenter(trade_engine)

command_center.join()
trade_engine.join()


