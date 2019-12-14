from trade_engine import TradeEngine
from command_center import CommandCenter


trade_engine = TradeEngine()
command_center = CommandCenter(trade_engine)

command_center.join()
trade_engine.join()
