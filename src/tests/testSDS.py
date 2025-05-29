from devices.BaseScope import BaseScope
from devices.BaseScope import pyvisa
import unittest
from unittest.mock import call, patch, MagicMock
from devices.siglent.sds.Scopes import SiglentScope
import tests.utils as utils
import numpy as np


def qbside_effect(command, datatype,  is_big_endian, container):
    if command == "C1:WaveForm? DESC":
        buffer = utils.createSDSPreambleStruct()
        return buffer 


def query_side_effect(command):
    if command == "*IDN?":
        return "Siglent Technologies,SDS1202X-E,SDS1EBAC0L0098,7.6.1.15"
    elif command == "C1:WF? DAT2":  
        return utils.genFakeSineWave()
    #elif command == "C1:WaveForm? DESC":
    #    buffer = utils.createSDSPreambleStruct()
    #    return str(buffer)
    else:
        return "UNKNOWN COMMAND"

class TestSDSCreate(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # 1) Patch pyvisa-functies één keer
        
        
        cls.patcher1 = patch.object(pyvisa.ResourceManager, "list_resources")
        cls.patcher2 = patch.object(pyvisa.ResourceManager, "open_resource")
        
        cls.MockListResources = cls.patcher1.start()
        cls.MockOpenResource = cls.patcher2.start()
        cls.mockdev = cls.MockOpenResource.return_value

        cls.mockdev.return_value = ["USBINSTR"]
        cls.mockdev.query_binary_values = qbside_effect
        cls.mockdev.query.side_effect = query_side_effect
        cls.MockListResources.return_value = ["INSTR::SDS1202XE::USB"]
        # 2) Maak de instrument-instantie aan
        cls.scope:BaseScope = BaseScope.getDevice()
    
    @classmethod
    def tearDownClass(cls):
        pass
        # Stop alle patchers
        #cls.patcher1.stop()
        #cls.patcher2.stop()

    def __init__(self, methodName = "runSDSTests"):
        super().__init__(methodName)
        self.myrm = None
        self.mydev = None
        self.expected = None

    def testNewSDS(self):
        verticaal = self.scope.vertical
        
        thechan = verticaal.chan(1)
        print(thechan)
        print(verticaal.nrOfChan)
        self.assertTrue(self.scope.vertical.nrOfChan == 2)
        self.assertFalse(self.scope.vertical.chan(1) == None)
        self.assertFalse(self.scope.vertical.chan(2) == None)
        self.assertFalse(self.scope.visaInstr == None)
        self.assertTrue(self.scope.__module__==SiglentScope.__module__)

    def testCaptureTDS(self):
        
        verticaal = self.scope.vertical
        
        thechan = verticaal.chan(1)
        thechan.capture()
        trace = thechan.WF
        y = trace.rawYdata
        #plt.plot(y)
        #plt.show()
    

"""
def testTheSDS():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    scope = SiglentScope()
    print(scope.CH1.getMean())
    
    print(scope.CH1.getPKPK())
    scope.CH1.capture()
    waveformTrace = scope.CH1.getTrace()
    timeAx = scope.CH1.getTimeAxis()
    plt.plot(timeAx, waveformTrace)
    plt.show()

"""