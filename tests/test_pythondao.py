import unittest
from dao.pythondao.pythondao import PythonDao

class TestPythonDao(unittest.TestCase):

    def setUp(self):
        self.dao = PythonDao()
        self.dao.delete_pumps()

    def test_save(self):
        pump = {"column1": 100, "column2": "dog"}
        pump_persisted = self.dao.save_pump(pump)
        self.assertEqual(pump_persisted["id"], 1)
        retrieved_pump = self.dao.get_pump(pump_persisted["id"])
        self.assertDictEqual(pump_persisted, retrieved_pump)
