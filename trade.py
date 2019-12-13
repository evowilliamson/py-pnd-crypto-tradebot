from enum import Enum
from system import System
import decimal

TradeDirection = Enum("TradeDirection", "UP DOWN")
TradeStrategy = Enum("TradeStrategy", "PND STEP")
TradeType = Enum("TradeType", "MARKET STOP_LOSS_LIMIT")
SIDE = Enum("Side", "BUY SELL")

MARKET_LIMIT_THRESHOLD_PCT = 5.0
USD_QUANTITY = 50.0
BTC = "BTC"
PND_PRICE_PCT = 1
PND_STOP_PCT = 0.5
PRICE = "price"


class Trade:

    def __init__(self, trade_engine, trade_direction, ticker_symbol,
                 trade_strategy, previous_price, last_price):
        self._trade_direction = trade_direction
        self._trade_strategy = trade_strategy
        self._ticker_symbol = ticker_symbol
        self._previous_price = previous_price
        self._last_price = last_price
        self._client = System().trade_client
        self._trade_engine = trade_engine
        self.trade()

    def trade(self):
        _quantity = self.get_btc_quantity_for_trade(self._ticker_symbol)
        (price_, stop_price) = self.determine_quote_price()
        trade_type = self.determine_trade_type()
        if self._ticker_symbol == "BTC":
            symbol_ = "BTCUSDT"
        else:
            symbol_ = self._ticker_symbol + "BTC"
        response = self._client.create_test_order(
            symbol=symbol_, side=SIDE.BUY.name, type="MARKET", quantity=_quantity)
        a = 100
        # self._client.order_limit_buy(
        #     symbol=self._ticker_symbol, side=BTC, type=trade_type, quantity=_quantity,
        #     price=__price, stopPrice=__stop_price)

            # price = decimal.Decimal(str(price_)))


        # :param symbol: required
        # :type symbol: str
        # :param side: required
        # :type side: str
        # :param type: required
        # :type type: str
        # :param timeInForce: required if limit order
        # :type timeInForce: str
        # :param quantity: required
        # :type quantity: decimal
        # :param price: required
        # :type price: str
        # :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        # :type newClientOrderId: str
        # :param icebergQty: Used with iceberg orders
        # :type icebergQty: decimal
        # :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        # :type newOrderRespType: str

    def determine_trade_type(self):
        if self._trade_strategy == TradeStrategy.PND:
            # trade_type = TradeType.MARKET \
            #     if self._percentage_changed >= MARKET_LIMIT_THRESHOLD_PCT else TradeType.STOP_LOSS_LIMIT
            trade_type = TradeType.STOP_LOSS_LIMIT
            print("Strategy is PND, trade type = {}".format(trade_type))
        elif self._trade_strategy == TradeStrategy.STEP:
            trade_type = TradeType.STOP_LOSS_LIMIT
            print("Strategy is STEP")
        return trade_type

    def get_btc_quantity_for_trade(self, ticker_symbol):
        quantity = USD_QUANTITY / self._trade_engine.get_current_trade_data(BTC, PRICE)
        print("Ticker symbol {0} btc quantity to buy: {1}".format(ticker_symbol, str(quantity)))
        return quantity

    def determine_quote_price(self):
        pct = ((self._last_price - self._previous_price) / self._previous_price) * 100.0
        return self._last_price, self._last_price * ((100.0 + pct)/100.0)












