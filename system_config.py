import json
import os
from singleton import Singleton

ROOT = os.path.dirname(os.path.realpath(__file__))
CONFIG_DIR = "config"
CONFIG_JSON = "config.json"

DBUSER = "dbuser"
DBPASSWORD = "dbpassword"
DBHOST = "dbhost"
DBNAME = "dbname"
DBPORT = "dbport"

BTC_PUMP_QUANTITY = "btc_pump_quantity"


@Singleton
class Config:
    """ Class that represents the configurations in this application."""

    def __init__(self):
        """ Default constructor """
        self._config = self.load()

    def load(self):
        with open(os.path.join(ROOT, CONFIG_DIR, CONFIG_JSON)) as f:
            config = json.load(f)
        return config

    @property
    def config(self):
        return self._config
