from devices.BaseScope import BaseScope, BaseChannel, BaseVertical
from devices.BaseScope import pyvisa
import unittest
from unittest.mock import call, patch, MagicMock
from devices.siglent.sds.Scopes import SiglentScope
import tests.utils as utils
import numpy as np
import matplotlib.pyplot as plt
from devices.siglent.sds.Channel import SDSWaveFormPreamble
from devices.siglent.sds.util import TIMEBASE_HASHMAP, guessSine, sine_function


"""In de documentatie van unittest staat de volgende opmerking:
Note
The order in which the various tests will be run is determined by sorting the test method names 
with respect to the built-in ordering for strings. 
"""


#nrOfPeriods = 2
pream = SDSWaveFormPreamble(None)
fs = 1.0e6
Amp = 1
offset = 0
AantalPer = 2
noiseAmp =1
noiseMean = 0
noiseSigma = 2

DESCRIPTOR_NAME:str = "WAVEDESC"
descr_bytes = np.frombuffer( DESCRIPTOR_NAME.encode(), dtype=np.dtype('B'))
pream.nrOfSamples = 7000
pream.probeAtt  = 1.0
pream.vdiv      = 0.5
pream.yoff      = 0.0
pream.timeDiv   = 1.0e-4
pream.trigDelay = pream.timeDiv
pream.xincr     = 1/fs

def qbside_effect(command, datatype,  is_big_endian, container):
    if command == "C1:WaveForm? DESC":
        buffer = utils.createSDSPreambleStruct(preamble=pream)
        return buffer
    elif command == "C1:WF? DAT2":  
        return utils.genFakeSineWave(nrOfSamples = pream.nrOfSamples, A = Amp, 
                                     nrOfPer = AantalPer,offset = offset, noise=(noiseAmp, noiseMean, noiseSigma), preamble=pream)
    else:
        print("unkown side effect!!") 


def query_side_effect(command):
    if command == "*IDN?":
        return "Siglent Technologies,SDS1202X-E,SDS1EBAC0L0098,7.6.1.15"
    #elif command == "C1:WaveForm? DESC":
    #    buffer = utils.createSDSPreambleStruct()
    #    return str(buffer)
    else:
        return "UNKNOWN COMMAND"

class TestSDSCase(unittest.TestCase):
    
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
 
    def testCaptureTDS(self):
        print("testCaptureTDS")
        verticaal: BaseVertical = self.scope.vertical
        
        thechan: BaseChannel = verticaal.chan(1)
        thechan.capture()
        trace = thechan.WF
        y = trace.rawYdata
        x = trace.rawXdata
        #prams, covar = guessSine(x,y)
        #A_fit, B_fit= prams
        A_fit = 50
        B_fit = 0.0018
        C_fit = 0
        D_fit = 0
        y_fit = sine_function(x, A_fit, B_fit, C_fit, D_fit)
        #y_fit = sine_function(x, A_fit, B_fit)
        
        plt.plot(x, y, x,y_fit)
        #plt.figure(2)
        #y = trace.scaledYdata
        #x = trace.scaledXdata
        #plt.plot(x,y)
        plt.show()
        
        print(f"Fitted parameters: A={A_fit}, B={B_fit}")

    def testNewSDS(self):
        print("##testNewSDS##")
        verticaal = self.scope.vertical
        
        thechan = verticaal.chan(1)
        print(thechan)
        print(verticaal.nrOfChan)
        self.assertTrue(self.scope.vertical.nrOfChan == 2)
        self.assertFalse(self.scope.vertical.chan(1) == None)
        self.assertFalse(self.scope.vertical.chan(2) == None)
        self.assertFalse(self.scope.visaInstr == None)
        self.assertTrue(self.scope.__module__==SiglentScope.__module__)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestSDSCase('testNewSDS'))
    suite.addTest(TestSDSCase('testCaptureTDS'))
    return suite


