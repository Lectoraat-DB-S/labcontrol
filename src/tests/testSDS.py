from devices.BaseScope import BaseScope
from devices.BaseScope import pyvisa
import unittest
from unittest.mock import call, patch, MagicMock
from devices.siglent.sds.Scopes import SiglentScope


class TestSDSCreate(unittest.TestCase):
    
    
    def __init__(self, methodName = "runSDSTests"):
        super().__init__(methodName)
        self.myrm = None
        self.mydev = None
        self.expected = None
    
    @patch.object(pyvisa.ResourceManager, "list_resources")
    @patch.object(pyvisa.ResourceManager, "open_resource")
    def testNetEffeAnders(self, mock_open_resource, mock_list_resource):
        mockdev = mock_open_resource.return_value
        mockdev.return_value = ["USBINSTR"]
        mockdev.query.return_value= "Siglent Technologies,SDS1202X-E,SDS1EBAC0L0098,7.6.1.15"
        mock_list_resource.return_value=["INSTR::SDS1202XE::USB"]
        scope = BaseScope()
        vert =scope.vertical
        print(vert.nrOfChan)



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