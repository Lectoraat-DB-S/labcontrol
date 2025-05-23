from devices.BaseScope import BaseScope
from devices.BaseScope import pyvisa
import unittest
from unittest.mock import call, patch, MagicMock
from devices.siglent.sds.Scopes import SiglentScope

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
        cls.mockdev.query.return_value= "Siglent Technologies,SDS1202X-E,SDS1EBAC0L0098,7.6.1.15"
        cls.MockListResources.return_value = ["INSTR::SDS1202XE::USB"]
        # 2) Maak de instrument-instantie aan
        cls.scope:BaseScope = BaseScope.getDevice()
    
    @classmethod
    def tearDownClass(cls):
        # Stop alle patchers
        cls.patcher1.stop()
        cls.patcher2.stop()

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