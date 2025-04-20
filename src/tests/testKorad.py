from devices.BaseSupply import BaseSupply, BaseSupplyChannel
from devices.Korad.KoradSupply import Korad3305P
import unittest
from unittest.mock import call, patch, MagicMock

#assert: if true, then nothing. If false, assertion
#blog : https://www.toptal.com/python/an-introduction-to-mocking-in-python

class TestKoradSupply(unittest.TestCase):
    
    def __init__(self, methodName = "runKoradTest"):
        super().__init__(methodName)
        self.myrm = None
        self.mysupply = self.testCreateNewKorad()

    @patch('pyvisa.ResourceManager')
    def testCreateNewKorad(self, RMMock: MagicMock):
        RMMock.mock_calls 
        self.myrm = RMMock.return_value
        self.myrm.list_resources.return_value = ["ASRL1::INSTR"]
        mydev = self.myrm.open_resource.return_value
        self.myrm.open_resource.return_value.resource_info.alias =str("COM10")
        
        mydev.return_value = ["Serial INSTR"]
        mydev.query.return_value = "KORAD KA3305P"
        expected = call.query("*IDN?").call_list()
        supply = BaseSupply(None)
        print("RMMock")
        print(RMMock.mock_calls)
        print("mydev")
        print(mydev.mock_calls)
        self.assertTrue(supply.__module__==Korad3305P.__module__)
        self.mysupply = supply
        

