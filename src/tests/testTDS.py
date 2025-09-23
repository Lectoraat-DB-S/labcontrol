from devices.tektronix.scope.TekScopes import TekScope
from devices.tektronix.scope.Channel import TekChannel, TekWaveForm, TekWaveFormPreamble
from devices.BaseScope import BaseScope
import unittest
from unittest.mock import call, patch, MagicMock
import pyvisa
import numpy as np
import math
import matplotlib.pyplot as plt
import tests.tdsUtils as tdsUtils



#assert: if true, then nothing. If false, assertion
#blog : https://www.toptal.com/python/an-introduction-to-mocking-in-python

def fake_preamble():
    """Hieronder een output van de scoop na aanzetten en autoscale
2;16;BIN;RP;MSB;2500;"Ch1, DC coupling, 5.0E-1 V/div, 5.0E-5 s/div,
 2500 points, Sample mode";Y;2.0E-7;0;-2.5E-4;"s";7.8125E-5;0.0E0;3.2768E4;"Volts"
 
 Nogmaals maar dan met de fmt:
BYT_Nr <NR1> = 2;       0
BIT_Nr = 16;            1
ENCdg = BIN;            2
BN_Fmt = RP;            3
BYT_Or = MSB;           4
NR_Pt  = 2500;          5
WFID = "Ch1, DC coupling, 5.0E-1 V/div, 5.0E-5 s/div, 2500 points, 
Sample mode";
;PT_FMT  = Y;           7
;XINcr = 2.0E-7;        8
 PT_Off = 0;            9
 XZERo = -2.5E-4;       10
 XUNit = "s";           11
 YMUlt = 7.8125E-5;     12
 YZEro = 0.0E0;         13
 YOFF = 3.2768E4        14
 YUNit = "Volts"        15
        


 """
    
myPreamble = None
class FakeWaveFormPreamble(TekWaveFormPreamble):

    def __init__(self, aantal, stepTime, vdiv):
        super.__init__()

        self.nrOfBytePerTransfer   = 1
        self.nrOfBitsPerTransfer   = 8
        self.encodingFormatStr     = "BIN"
        self.binEncodingFormatStr  = "bla"
        self.binFirstByteStr       = "MSD"
        self.nrOfSamples           = aantal
        self.vertMode              = "Y" #Y, XY, or FFT.
        self.xincr                 = stepTime
        self.xzero                 = 0
        self.xUnitStr              = "s"
        self.ymult                 = vdiv
        self.yzero                 = 0
        self.yoff                  = 0
        self.yUnitStr              = "Volts"
        self.couplingstr           = None
        self.timeDiv               = stepTime
        self.acqModeStr            = None
        self.sourceChanStr         = None
        self.vdiv                  = vdiv
        self.chanPreamblestr = "Ch1, DC coupling, 1.0E0 V/div, 5.0E-4 s/div, 2500 points, Sample mode"
    def getWFMPREString(self):
        wfpre_str = f"{self.nrOfBytePerTransfer};{self.nrOfBitsPerTransfer};\
            {self.encodingFormatStr};\
            {self.binEncodingFormatStr};\
            {self.binFirstByteStr};\
            {self.nrOfSamples};\
            {str(self.chanPreamblestr)};\
            {self.vertMode};\
            {self.xincr}; \
            {0};\
            {self.xzero};\
            {self.xUnitStr};\
            {self.ymult};\
            {self.yzero};\
            {self.yoff};\
            {self.yUnitStr};"
        return wfpre_str
                    
def setFakeTekWaveFormPreamble(aantal,stepTime, vdiv):
    p = TekWaveFormPreamble(None)
    
                    
    return p



def query_side_effect(command):
    if command == "*IDN?":
        return "TEKTRONIX,TDS"
    elif command == "MEAS:VOLT?":
        return "3.3"
    elif command == "curve?":
        return tdsUtils.genFakeSineWave()
    elif command == "WFMPRE?":
        return tdsUtils.createTDSPreamble()
    else:
        return "UNKNOWN COMMAND"
    

class TestTDSCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1) Patch pyvisa-functies één keer
        starttime = 0
        endtime = 2e-3
        aantal_stappen = 2500
        f=200
        timestep=(starttime-endtime)/aantal_stappen
        cls.myfakeSin = tdsUtils.genFakeSineWave(starttime, endtime, aantal_stappen, f)
        cls.myfakePreamble:FakeWaveFormPreamble = setFakeTekWaveFormPreamble(aantal=aantal_stappen, stepTime=timestep, vdiv=1 )
        
        
        cls.patcher1 = patch.object(pyvisa.ResourceManager, "list_resources")
        cls.patcher2 = patch.object(pyvisa.ResourceManager, "open_resource")
        
        cls.MockListResources = cls.patcher1.start()
        cls.MockOpenResource = cls.patcher2.start()
        cls.mockdev = cls.MockOpenResource.return_value

        cls.mockdev.return_value = ["USBINSTR"]
        #query: het antwoord moet gaan afhangen van de paramters. Dus de call moet worden afgevangen.
        # Wijs de functie toe als side_effect van de mock query methode
        cls.mockdev.query.side_effect = query_side_effect   
        #cls.mockdev.query_binary_values.side_effect = query_side_effect
        cls.mockdev.query_binary_values.return_value = tdsUtils.genFakeSineWave()   
        cls.MockListResources.return_value = ["INSTR::xxx::USB"]
        # 2) Maak de instrument-instantie aan
        cls.scope:BaseScope = BaseScope.getDevice()
    
    @classmethod
    def tearDownClass(cls):
        # Stop alle patchers
        cls.patcher1.stop()
        cls.patcher2.stop()

    def testNewTDS(self):
        
        verticaal = self.scope.vertical
        
        thechan = verticaal.chan(1)
        print(thechan)
        print(verticaal.nrOfChan)
        #self.assertTrue(self.scope.vertical.nrOfChan == 2)
        self.assertFalse(self.scope.vertical.chan(1) == None)
        self.assertFalse(self.scope.vertical.chan(2) == None)
        self.assertFalse(self.scope.visaInstr == None)
        self.assertFalse(thechan.visaInstr == None)
        self.assertTrue(self.scope.__module__==TekScope.__module__)

    def testCaptureTDS(self):
        preamblstr_toreturn = self.myfakePreamble.getWFMPREString()
        
        verticaal = self.scope.vertical
        
        thechan = verticaal.chan(1)
        thechan.capture()
        trace = thechan.WF
        y = trace.rawYdata
        plt.plot(y)
        plt.show()
    
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestTDSCase('testNewTDS'))
    suite.addTest(TestTDSCase('testCaptureTDS'))
    return suite

