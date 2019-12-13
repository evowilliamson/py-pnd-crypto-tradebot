from singleton import Singleton
import json

frequency = 2500
duration = 1000


@Singleton
class System:

    @property
    def trade_client(self):
        return self._client


