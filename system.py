from singleton import Singleton
from binance.client import Client
import json

BINANCE_KEY = "binance_key"
BINANCE_SECRET = "binance_secret"

frequency = 2500
duration = 1000


@Singleton
class System:

    def __init__(self):
        self._config = self.read_config()
        self._client = Client(self._config[BINANCE_KEY], self._config[BINANCE_SECRET])

    @classmethod
    def read_config(cls):
        return json.load(open('/home/ivo/trade_bot/config.json'))

    @property
    def trade_client(self):
        return self._client

