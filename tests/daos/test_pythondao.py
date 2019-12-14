import unittest
from dao.pythondao.pythondao import PythonDao
import datetime

class TestPythonDao(unittest.TestCase):

    def setUp(self):
        self.dao = PythonDao()
        self.dao.delete_pumps()

    def test_save_get_pump(self):
        pump = {"column1": 100, "column2": "dog"}
        pump_persisted = self.dao.save_pump(pump)
        self.assertEqual(pump_persisted["id"], 1)
        retrieved_pump = self.dao.get_pump(pump_persisted["id"])
        self.assertDictEqual(pump_persisted, retrieved_pump)
        self.assertTrue(pump_persisted["column1"] == retrieved_pump["column1"])
        self.assertTrue(pump_persisted["column2"] == retrieved_pump["column2"])
        
    def test_get_all_running_pumps(self):
        pumpsdef = {}
        pumpsdef[1] = {"column1": 100, "column2": "dog"}
        pumpsdef[2] = {"column1": 200, "column2": "cat"}
        pumpsdef[3] = {"column1": 300, "column2": "fish"}
        self.dao.save_pump(pumpsdef[1])
        self.dao.save_pump(pumpsdef[2])
        self.dao.save_pump(pumpsdef[3])
        self.assertTrue(len(self.dao.get_all_running_pumps()) == len(pumpsdef))
        
    def test_update_stop_loss(self):
        pump = {"column1": 100, "column2": "dog", "stop_loss": 100}
        pump_persisted = self.dao.save_pump(pump)
        new_stop_loss = 200
        pump["stop_loss"] = new_stop_loss
        self.assertTrue(self.dao.get_pump(pump_persisted["id"])["stop_loss"] == new_stop_loss)

    def test_close_pump(self):
        pump = {
            "end_price": 100, "end_time": datetime.datetime.now(),
            "profit_pct": 2.2, "status": "OPEN"}
        pump_persisted = self.dao.save_pump(pump)
        pump_persisted["end_price"] = 300
        time_now1 = datetime.datetime.now()
        pump_persisted["end_time"] = time_now1
        pump_persisted["profit_pct"] = 2
        self.dao.close_pump(pump)
        time_now2 = datetime.datetime.now()
        retrieved_pump =  self.dao.get_pump(pump_persisted["id"])
        self.assertTrue(pump_persisted["end_time"] > 
            time_now1 and pump_persisted["end_time"] < time_now2)
        self.assertTrue(pump_persisted["profit_pct"] == 2)
        self.assertTrue(pump_persisted["end_price"] == 300)
        self.assertTrue(pump_persisted["status"] == "CLOSED")

    def test_delete_pumps(self):
        pump = {"column1": 100, "column2": "dog", "stop_loss": 100}
        pump_persisted = self.dao.save_pump(pump)
        self.dao.delete_pumps()
        self.assertTrue(len(self.dao.get_all_running_pumps()) == 0)