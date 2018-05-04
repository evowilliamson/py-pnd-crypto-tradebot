from system import System
from trade_engine import TradeEngine
from command_center import CommandCenter


order_client = System.instance().order_client
trade_engine = TradeEngine.instance(order_client)
command_center = CommandCenter(trade_engine)

command_center.join()
trade_engine.join()


