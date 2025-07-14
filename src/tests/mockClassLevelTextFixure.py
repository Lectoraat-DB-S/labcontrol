#Voorbeeld generereed door chatgpt.
import unittest
from unittest.mock import patch

class TestInstrument(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1) Patch pyvisa-functies één keer
        cls.patcher_open = patch('pyvisa.ResourceManager.open_resource')
        cls.mock_open = cls.patcher_open.start()
        cls.mock_open.return_value = 'GEMOCKT_DEVICE'
        # 2) Maak de instrument-instantie aan
        cls.instrument = YourInstrumentClass()  # init roept open_resource() intern aan

    @classmethod
    def tearDownClass(cls):
        # Stop alle patchers
        cls.patcher_open.stop()

    def test_feature_one(self):
        # Hergebruik de in setUpClass gemaakte instantie
        result = self.instrument.feature_one()
        self.assertEqual(result, expected_value)

    def test_feature_two(self):
        # Wéér dezelfde instrument-instantie
        result = self.instrument.feature_two()
        self.assertTrue(result)
