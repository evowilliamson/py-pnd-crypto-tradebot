from singleton import Singleton
from dummy_client import DummyClient
import json

frequency = 2500
duration = 1000


@Singleton
class System:

    def __init__(self, *args):
        self._order_client = DummyClient.instance()

    @property
    def trade_client(self):
        return self._client

    @property
    def order_client(self):
        return self._order_client

