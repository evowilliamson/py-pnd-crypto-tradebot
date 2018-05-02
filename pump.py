import datetime


class Pump:

    def __init__(
            self, ticker_symbol, start_price, initial_pump_price_pct, initial_pump_volume_pct ,
            amount_btc, stop_loss):
        self._ticker_symbol = ticker_symbol
        self._start_time = datetime.datetime.now()
        self._start_price = start_price
        self._initial_pump_price_pct = initial_pump_price_pct
        self._initial_pump_volume_pct = initial_pump_volume_pct
        self._amount_btc = amount_btc
        self._stop_loss = stop_loss

    @property
    def id(self):
        return self._id

    @property
    def ticker_symbol(self):
        return self._ticker_symbol

    @property
    def start_time(self):
        return self._start_time

    @property
    def start_price(self):
        return self._start_price

    @property
    def initial_pump_price_pct(self):
        return self._initial_pump_price_pct

    @property
    def initial_pump_volume_pct(self):
        return self._initial_pump_volume_pct

    @property
    def end_time(self):
        return self._end_time

    @property
    def end_price(self):
        return self._end_price

    @property
    def stop_loss(self):
        return self._stop_loss

    @property
    def amount_btc(self):
        return self._amount_btc
