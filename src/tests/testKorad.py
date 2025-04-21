from devices.BaseSupply import BaseSupply, BaseSupplyChannel
from devices.Korad.KoradSupply import Korad3305P, KoradChannel
import unittest
from unittest.mock import call, patch, MagicMock

#assert: if true, then nothing. If false, assertion
#blog : https://www.toptal.com/python/an-introduction-to-mocking-in-python

class TestKoradSupply(unittest.TestCase):

    theSupply = None
    
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)
        self.mysupply = list()


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
        mysupply = BaseSupply(None)
        TestKoradSupply.theSupply = mysupply
        
        print("RMMock")
        print(RMMock.mock_calls)
        print("mydev")
        print(mydev.mock_calls)
        self.assertTrue(mysupply.__module__==Korad3305P.__module__)
        
    @patch('pyvisa.ResourceManager')
    def testNrOfChanKorad(self, RMMock: MagicMock):
        
        supply = TestKoradSupply.theSupply

        aantalKan = supply.nrOfChan
        self.assertTrue(aantalKan==2)

    @patch('pyvisa.ResourceManager')
    def testKoradChanObject(self, RMMock: MagicMock):
        
        supply = TestKoradSupply.theSupply

        aantalKan = supply.nrOfChan
        chanNr = 1
        #chan1= TestKoradSupply.theSupply.chan(chanNr)
        chan2 = supply.chan(2)
        #self.assertTrue(chan1.__module__==KoradChannel.__module__)

