from singleton import Singleton
from system_config import Config

@Singleton
class PythonDao(object):

    def __init__(self):
        config = Config()

    def print_something(self):
        print("something")