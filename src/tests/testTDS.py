from devices.tektronix.scope.TekScopes import TekScope
from devices.tektronix.scope.Channel import TekChannel, TekWaveForm, TekWaveFormPreamble
from devices.BaseScope import BaseScope
import unittest
from unittest.mock import call, patch, MagicMock
import pyvisa
import numpy as np
import math
import matplotlib.pyplot as plt

#assert: if true, then nothing. If false, assertion
#blog : https://www.toptal.com/python/an-introduction-to-mocking-in-python

def fakesinewave(starttime = 0, endtime = 2e-3, aantal_stappen = 2500, f=200):
    tstep = np.linspace(starttime,endtime,aantal_stappen)
    y = np.sin(2.0*np.pi*(f)*tstep)
    y=y*127
    y=np.round(y)
    #plt.plot(y)
    #plt.show()
    return np.array(y, dtype=np.dtype('b'))

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
        self.sampleStepTime        = stepTime
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
        return fakesinewave()
    elif command == "WFMPRE?":
        return getWFMPREString(myPreamble)
    else:
        return "UNKNOWN COMMAND"
    

"""
# Gebruik je mock in code
print(mock_resource.query("*IDN?"))       # MyInstrument,Model123,Serial456,1.0
print(mock_resource.query("MEAS:VOLT?"))  # 3.3
print(mock_resource.query("MEAS:CURR?"))  # 0.12
print(mock_resource.query("FOO"))         # UNKNOWN COMMAND

"""


class TestTDSCreate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1) Patch pyvisa-functies één keer
        starttime = 0
        endtime = 2e-3
        aantal_stappen = 2500
        f=200
        timestep=(starttime-endtime)/aantal_stappen
        cls.myfakeSin = fakesinewave(starttime, endtime, aantal_stappen, f)
        cls.myfakePreamble = setFakeTekWaveFormPreamble(aantal=aantal_stappen, stepTime=timestep, vdiv=1 )
        
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
        cls.mockdev.query_binary_values.return_value = fakesinewave()   
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
        

        verticaal = self.scope.vertical
        
        thechan = verticaal.chan(1)
        thechan.capture()
        trace = thechan.WF
        y = trace.rawYdata
        plt.plot(y)
        plt.show()
        
        
""" 
class TestTekChannel(unittest.TestCase):
    #checken hoe je zo automatisch mogelijk kan testen met Python, dus autogeneratie van test-body-skeleton code.
    def testqueryNrOfSamples(self, chan: TekChannel):
        nrpoints = chan.getNrOfPoints()
        self.assertEqual(nrpoints,2500)       
        
   
    def TestsetAsSource(self, chan: TekChannel):
        #first set source than read backl mustbe same.
        #self.visaInstr.write(f"DATA:SOURCE {self._name}") #Sets the channel as data source    
        pass 

    def TestsetToDefault(self):
        #self.setEncoding(TekScopeEncodings.RIBinary)
        #self.setNrOfByteTransfer(2)
        pass
     
    def TestsetVisible(self, state:bool):
        if state:
            self.visaInstr.write(f"SELECT:{self._name} ON")
            self.isVisible = True
        else:
            self.visaInstr.write(f"SELECT:{self._name} OFF")
            self.isVisible = False
            
    def TestisVisible(self):
        return self.isVisible
                
    def setEncoding(self, encoding: TekScopeEncodings):
        if isinstance(encoding, TekScopeEncodings):
            if (encoding==encoding.RIBinary or encoding==encoding.ASCII or 
                encoding==encoding.RPBinary or
                encoding==encoding.SRIbinary or
                encoding==encoding.SRPbinary):
                
                self.visaInstr.write(f"DATa:ENCdg {encoding.value}")
                self.encoding = encoding
            else:
                self.log.addToLog("Unknown encoding type. switch to RIBinary format")
                self.visaInstr.write(f"DATa:ENCdg {encoding.RIBinary.value}")
            
    def setNrOfByteTransfer(self, nrOfBytes=1):
        if (nrOfBytes==1):
            self.visaInstr.write('wfmpre:byt_nr 1')
        elif (nrOfBytes==2):
            self.visaInstr.write('wfmpre:byt_nr 2')
        else:
            self.visaInstr.write('wfmpre:byt_nr 1')
            self.log.addToLog("ÏNVALID USER SETTING! Number of byte transfer set to one.")
                
    def getLastTrace(self):
        return self.WF
    
    def queryHorizontalSecDiv(self):
        SEC_DIV = float(self.visaInstr.query('HORIZONTAL:MAIN:SECDIV?')) #Requesting the horizontal scale in SEC/DIV
        return SEC_DIV   
    
    def setVertScale(self, scale):
        #TODO check validity of param
        self.visaInstr.write(f"{self._name}:SCALE {scale}") #Sets V/DIV CH1
  
    def setVoltsDiv(self, scale):
        #TODO check validity of param
        vertscalelist = [2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1, 2, 5]
        if scale in vertscalelist:
            self.visaInstr.write(f"{self._name}:SCALE {scale}") #Sets V/DIV CH1   
        else:   
            self.log.addToLog("invalid VDIV input, ignoring.....") 
    
    def setTimeDiv(self, time):
        self.visaInstr.write(f"HORizontal:MAIn:SCAle {time}")
    
    def setAsSource(self):
        self.visaInstr.write(f"DATA:SOURCE {self.name}") #Sets the channel as data source for transimitting data   
    
    def getNrOfPoints(self):
        #TODO:
        # correct handling of event code 2244
        return int(self.visaInstr.query(f"wfmpre:{self._name}:nr_pt?")) #For a channel version of this command:see programming guide page 231
          
    def capture(self):
        wfp = self.WFP
        trace = self.WF
        self.setAsSource()
        wfp.queryPreamble()
        trace.setWaveFormID(wfp)
        self.log.addToLog("start querying scope")
        bin_wave = self.visaInstr.query_binary_values('curve?', datatype='b', container=np.array)
        self.log.addToLog("scope query ended")
        
        
        trace.rawYdata = bin_wave
        trace.rawXdata = np.linspace(0, wfp.nrOfSamples-1, num=int(wfp.nrOfSamples),endpoint=False)
        total_time = wfp.sampleTime * wfp.nrOfSamples
        tstop = wfp.xzero + total_time
        scaled_time = np.linspace( wfp.xzero, tstop, num=int(wfp.nrOfSamples))
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        scaled_wave = (unscaled_wave - wfp.yoff) *  wfp.ymult  + wfp.yzero
        #put the data into internal 'struct'
        trace.scaledYdata = scaled_wave
        trace.scaledXdata = scaled_time
        
    
    ##### DATA TRANSFER RELATED METHODS ######
    def queryEncoding(self):
        return self.visaInstr.query("DATa:ENCdg?")
    
    def setBinEncoding(self):
        self._visaInstr.write('data:encdg RIBINARY')
    
    def queryWaveFormPreamble(self):
        #TODO add intern state for ascii or binary. Defines query or binary_query
        self.setAsSource()
        response = self.visaInstr.query('WFMPRE?')
        self.WFP.decode(response)
        
    def getImmedMeasParam(self):
        response = self.visaInstr.query("MEASUrement:IMMed?")
        return response
    
    def immedMeasType(self):
        return str(self.visaInstr.query(f"MEASUREMENT:IMMED:TYPE?"))

    def immedMeasType(self, measType):
        for hulp in TekChannel.IMMEDMEASTYPES:
            if measType == hulp or measType == hulp.upper() or measType == hulp.lower():
                self.visaInstr.write(f"MEASUREMENT:IMMED:TYPE {measType}")        
            
    def doImmedMeas(self, measType):
        self.immedMeasType(measType)
        self.visaInstr.write(f"MEASUREMENT:IMMED:SOURCE {self.name}")
        return self.visaInstr.query("MEASUrement:IMMed:VALue?")
        
    def getMean(self):
        response = self.doImmedMeas("MEAN")        
        return float(response)
    
    def getMax(self):
        response = self.doImmedMeas("MAXImum")        
        return float(response)
            
"""     
    
"""Interface van Basescope:

    def getDevice(cls, rm, urls, host):
        return None #Base class implementation: return None, because this class can't do shit.
    
        
    def __new__(cls, host=None):
        instance = super().__new__(cls) #to have Pylance detect the proper type of a variable, call this!

        
        #rm = visa.ResourceManager("@sim")
        rm = visa.ResourceManager()
        urls = rm.list_resources()
        host = None

        for scope in cls.scopeList:
            dev = scope.getDevice(rm, urls, host)
            if dev != None:
                return dev
        
        return instance     
        
    def __init__(self, dev=None):
        self.visaInstr : visa.Resource = dev
        self.horizontal = None
        self.vertical = None
        self.trigger = None
        self.utility = None
        self.host = None
 
    def visaInstr(self) -> visa.Resource: 
    """
    
"""Interface van BaseChannel
class BaseChannel(object):
    def __init__(self, visaInstr):
        self.visaInstr = visaInstr
        self.WF = BaseWaveForm()            # the waveform ojbect of this channel
        self.WFP = BaseWaveFormPreample(visaInstr) # the waveformpreamble object for this channel
        
        
    def capture(self):
        pass
"""

"""class TekScope(BaseScope):
    
    @classmethod
    def getDevice(cls, rm, urls, host):
        #rm.close()
        #rm2 = visa.ResourceManager("@sim")
        #urls = rm2.list_resources()
        urlPattern = "USB" 
        if host == None:
            for url in urls:
                if urlPattern in url:
                    mydev = rm.open_resource(url)
                    mydev.timeout = 10000  # ms
                    mydev.read_termination = '\n'
                    mydev.write_termination = '\n'
                    desc = mydev.query("*IDN?")
                    if desc.find("TEKTRONIX,TDS") > -1: #Tektronix device found via IDN.
                        if cls is TekScope:
                            cls.__init__(cls,mydev)
                            return cls
                        else:
                            return None        
        else:
            try:
                ip_addr = socket.gethostbyname(host)
                addr = 'TCPIP::'+str(ip_addr)+'::INSTR'
                mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                cls.__init__(cls,mydev)
                return cls
            except socket.gaierror:
                
                return None
        
        return None

    def __init__(self, dev):
        super().__init__(dev) #baseclass will store referentie to the device.
        self.horizontal:TekHorizontal = TekHorizontal(dev)
        self.vertical:TekVertical = TekVertical(2, dev)
        self.trigger:TekTrigger = TekTrigger(self.vertical,dev)
       
       
    def setToDefault(self):
        self.setBinEncoding()
        self.setNrOfByteTransfer(2)

    
    
    #FOR TEKTRONIX TDS series nrOfBytes is 1 or 2.
    def setNrOfByteTransfer(self, nrOfBytes=1):
        if (nrOfBytes==1):
            self._visaInstr.write('wfmpre:byt_nr 1')
        elif (nrOfBytes==2):
            self._visaInstr.write('wfmpre:byt_nr 2')
        else:
            self._visaInstr.write('wfmpre:byt_nr 1')
            self.log.addToLog("ÏNVALID USER SETTING! Number of byte transfer set to one.")
    
    def getNrOfPoints(self):
        #TODO:
        # correct handling of event code 2244
        return int(self._visaInstr.query('wfmpre:nr_pt?')) #For a channel version of this command:see programming guide page 231
            
       
    
    def setDataTransferWidth(self,width):
        #TODO: check validity of width param     
        self.visaInstr.write(f"DATA:WIDTH {width}")
        
    def time(self):
        return str(self.visaInstr.query("TIMe?"))
    
    def time(self, timeVal):
        self.visaInstr.write(f"TIMe {timeVal}")
        
    def setStartSampleNr(self, startNr):
        #TODO check if startNr is correct
        self.visaInstr.write(f"DATA:START {startNr}") #Sets start of sample data 
        self.visaInstr.write("DATA:STOP 2500") #Sets end of sample data
    
    def setStopSampleNr(self, stopNr):
        #TODO check if startNr is correct
        self.visaInstr.write(f"DATA:STOP {stopNr}") #Sets end of sample data
    """
    
"""Interface of TekChannel

class TekChannel(BaseChannel):
    IMMEDMEASTYPES =["CRMs","CURSORRms","DELay","FALL",
                        "FREQuency","MAXImum","MEAN","MINImum","NONe","NWIdth","PDUty","PERIod","PHAse", 
                        "PK2pk","PWIdth","RISe"]
    #def __init__(self, chan_no: int, scope=None):
        # 25/6/24: Got a partially imported or circular import error. A way to prevent the circular is explained here:
        # https://stackoverflow.com/questions/64807163/importerror-cannot-import-name-from-partially-initialized-module-m
        # But an better alternative is to change the structure so its purely hierarchical.
        
        #from tektronix.scope.TekScopes import TekScope
    def __init__(self, chan_no: int, visaInstr):
        super().__init__(visaInstr)
        self.name = f"CH{chan_no}"
        self.log = TekLog()
        #if scope != None:
        #    self._parentScope = scope
        self.WFP: TekWaveFormPreamble = TekWaveFormPreamble(visaInstr)
        self.WF: TekWaveForm = TekWaveForm()
        self.nrOfDivs = 5          # TODO: should be set during initialisation of the scope.
        self.isVisible = False     # Value will be only set during method setVisble.
        #self.setVisible(True)
        self.encoding = None
        
    def queryNrOfSamples(self):
        NR_PT =  int(self._visaInstr.query('WFMPRE:NR_PT?')) #Requesting the number of samples
        return NR_PT
        
   
    def setAsSource(self):
    
        #check if channel is valid 
        self.visaInstr.write(f"DATA:SOURCE {self._name}") #Sets the channel as data source     

    def setToDefault(self):
        self.setEncoding(TekScopeEncodings.RIBinary)
        self.setNrOfByteTransfer(2)
         
    def setVisible(self, state:bool):
        if state:
            self.visaInstr.write(f"SELECT:{self._name} ON")
            self.isVisible = True
        else:
            self.visaInstr.write(f"SELECT:{self._name} OFF")
            self.isVisible = False
            
    def isVisible(self):
        return self.isVisible
                
    def setEncoding(self, encoding: TekScopeEncodings):
        if isinstance(encoding, TekScopeEncodings):
            if (encoding==encoding.RIBinary or encoding==encoding.ASCII or 
                encoding==encoding.RPBinary or
                encoding==encoding.SRIbinary or
                encoding==encoding.SRPbinary):
                
                self.visaInstr.write(f"DATa:ENCdg {encoding.value}")
                self.encoding = encoding
            else:
                self.log.addToLog("Unknown encoding type. switch to RIBinary format")
                self.visaInstr.write(f"DATa:ENCdg {encoding.RIBinary.value}")
            
    def setNrOfByteTransfer(self, nrOfBytes=1):
        if (nrOfBytes==1):
            self.visaInstr.write('wfmpre:byt_nr 1')
        elif (nrOfBytes==2):
            self.visaInstr.write('wfmpre:byt_nr 2')
        else:
            self.visaInstr.write('wfmpre:byt_nr 1')
            self.log.addToLog("ÏNVALID USER SETTING! Number of byte transfer set to one.")
                
    def getLastTrace(self):
        return self.WF
    
    def queryHorizontalSecDiv(self):
        SEC_DIV = float(self.visaInstr.query('HORIZONTAL:MAIN:SECDIV?')) #Requesting the horizontal scale in SEC/DIV
        return SEC_DIV   
    
    def setVertScale(self, scale):
        #TODO check validity of param
        self.visaInstr.write(f"{self._name}:SCALE {scale}") #Sets V/DIV CH1
  
    def setVoltsDiv(self, scale):
        #TODO check validity of param
        vertscalelist = [2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1, 2, 5]
        if scale in vertscalelist:
            self.visaInstr.write(f"{self._name}:SCALE {scale}") #Sets V/DIV CH1   
        else:   
            self.log.addToLog("invalid VDIV input, ignoring.....") 
    
    def setTimeDiv(self, time):
        self.visaInstr.write(f"HORizontal:MAIn:SCAle {time}")
    
    def setAsSource(self):
        self.visaInstr.write(f"DATA:SOURCE {self.name}") #Sets the channel as data source for transimitting data   
    
    def getNrOfPoints(self):
        #TODO:
        # correct handling of event code 2244
        return int(self.visaInstr.query(f"wfmpre:{self._name}:nr_pt?")) #For a channel version of this command:see programming guide page 231
          
    def capture(self):
        wfp = self.WFP
        trace = self.WF
        self.setAsSource()
        wfp.queryPreamble()
        trace.setWaveFormID(wfp)
        self.log.addToLog("start querying scope")
        bin_wave = self.visaInstr.query_binary_values('curve?', datatype='b', container=np.array)
        self.log.addToLog("scope query ended")
        
        
        trace.rawYdata = bin_wave
        trace.rawXdata = np.linspace(0, wfp.nrOfSamples-1, num=int(wfp.nrOfSamples),endpoint=False)
        total_time = wfp.sampleTime * wfp.nrOfSamples
        tstop = wfp.xzero + total_time
        scaled_time = np.linspace( wfp.xzero, tstop, num=int(wfp.nrOfSamples))
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        scaled_wave = (unscaled_wave - wfp.yoff) *  wfp.ymult  + wfp.yzero
        #put the data into internal 'struct'
        trace.scaledYdata = scaled_wave
        trace.scaledXdata = scaled_time
        
    
    ##### DATA TRANSFER RELATED METHODS ######
    def queryEncoding(self):
        return self.visaInstr.query("DATa:ENCdg?")
    
    def setBinEncoding(self):
        self._visaInstr.write('data:encdg RIBINARY')
    
    def queryWaveFormPreamble(self):
        #TODO add intern state for ascii or binary. Defines query or binary_query
        self.setAsSource()
        response = self.visaInstr.query('WFMPRE?')
        self.WFP.decode(response)
        
    def getImmedMeasParam(self):
        response = self.visaInstr.query("MEASUrement:IMMed?")
        return response
    
    def immedMeasType(self):
        return str(self.visaInstr.query(f"MEASUREMENT:IMMED:TYPE?"))

    def immedMeasType(self, measType):
        for hulp in TekChannel.IMMEDMEASTYPES:
            if measType == hulp or measType == hulp.upper() or measType == hulp.lower():
                self.visaInstr.write(f"MEASUREMENT:IMMED:TYPE {measType}")        
            
    def doImmedMeas(self, measType):
        self.immedMeasType(measType)
        self.visaInstr.write(f"MEASUREMENT:IMMED:SOURCE {self.name}")
        return self.visaInstr.query("MEASUrement:IMMed:VALue?")
        
    def getMean(self):
        response = self.doImmedMeas("MEAN")        
        return float(response)
    
    def getMax(self):
        response = self.doImmedMeas("MAXImum")        
        return float(response)

    

class TekWaveFormPreamble(BaseWaveFormPreample):
    def __init__(self, visaInstruments):
        super().__init__(visaInstruments)
        ##### START OF TEKTRONIX TDS TYPICAL PARAMETERS DEFINITION ####### 
        self.nrOfBytePerTransfer   = None
        self.nrOfBitsPerTransfer   = None
        self.encodingFormatStr     = None
        self.binEncodingFormatStr  = None
        self.binFirstByteStr       = None
        self.nrOfSamples           = None
        self.vertMode              = None #Y, XY, or FFT.
        self.sampleTime            = None
        self.xincr                 = None
        self.xzero                 = None
        self.xUnitStr              = None
        self.ymult                 = None
        self.yzero                 = None
        self.yoff                  = None
        self.yUnitStr              = None
        self.couplingstr           = None
        self.timeDiv               = None
        self.acqModeStr            = None
        self.sourceChanStr         = None
        self.vdiv                  = None
        
        
    def decode(self, strToDecode):
        paramlist = strToDecode.split(';')

        self.nrOfBytePerTransfer    = int(paramlist[0])
        self.nrOfBitsPerTransfer    = int(paramlist[1])
        self.encodingFormatStr      = str(paramlist[2])
        self.binEncodingFormatStr   = str(paramlist[3])
        self.binFirstByteStr        = str(paramlist[4])
        self.nrOfSamples            = int(paramlist[5])
        self.vertMode               = str(paramlist[7])
        self.sampleTime             = float(paramlist[8])
        self.xincr                  = float(paramlist[8])
        self.xzero                  = float(paramlist[10])
        self.xUnitStr               = str(paramlist[11])
        self.ymult                  = float(paramlist[12])
        self.yzero                  = float(paramlist[13])
        self.yoff                    = float(paramlist[14])
        self.yUnitStr               = str(paramlist[15])
        self.decodeChanPreamble(paramlist[6])
        
    def queryPreamble(self):
        response = self.visaInstr.query("WFMPRE?")
        self.decode(response)
    
    def decodeChanPreamble(self, chanStrToDecode):
        #6th element in channellist of TDS
        channelParamList = chanStrToDecode.strip('"')
        channelParamList=channelParamList.strip("'")
        channelParamList=channelParamList.split(',')
        self.sourceChanStr = str(channelParamList[0])
        hulp = (channelParamList[1].strip()).split()
        self.couplingstr = str(hulp[0])
        hulp = (channelParamList[2].strip()).split()
        self.vdiv  = float(hulp[0])
        hulp = (channelParamList[3].strip()).split()
        self.timeDiv = float(hulp[0])
        hulp = (channelParamList[4].strip()).split()
        self.nrOfSamples = float(hulp[0])
        hulp = (channelParamList[5].strip())
        self.acqModeStr = str(hulp)

class TekWaveForm(BaseWaveForm):
    def __init__(self):
        super().__init__()
        
        ####TEKTRONIX TDS SPECIFIC WAVEFORM PARAMS ########
        self.rawYdata       = None #data without any conversion or scaling taken from scope
        self.rawXdata       = None #just an integer array
        self.scaledYdata    = None #data converted to correct scale e.g untis
        self.scaledXdata    = None #An integer array representing the fysical instants of the scaledYData.
        #Horizontal data settings of scope
        self.chanstr        = None
        self.couplingstr    = None
        self.timeDiv        = None # see TDS prog.guide table2-17: (horizontal)scale = (horizontal) secdev 
        self.vDiv           = None # probably the same as Ymult.
        self.xzero          = None # Horizontal Position value
        self.xUnitStr       = None # unit of X-as/xdata
        self.xincr          = None # multiplier for scaling time data, time between two sample points.
        self.nrOfSamples    = None # the number of points of trace.
        self.sampleTime     = None # same as XINCR, Ts = time between to samples.
        self.yzero          = None 
        self.ymult          = None # vertical step scaling factor. Needed to translate binary value of sample to real stuff.
        self.yoff           = None # vertical offset in V for calculating voltage
        self.yUnitStr       = None
        
    def setWaveFormID(self, wfp: TekWaveFormPreamble):
        self.chanstr = wfp.sourceChanStr
        self.couplingstr = wfp.couplingstr
        self.timeDiv = wfp.timeDiv
        self.vDiv = wfp.vdiv
        self.xzero          = wfp.xzero
        self.xUnitStr       = wfp.xUnitStr
        self.xincr          = wfp.xincr
        self.nrOfSamples    = wfp.nrOfSamples
        self.sampleTime     = wfp.sampleTime
        self.yzero          = wfp.yzero
        self.yoff           = wfp.yoff
        self.ymult          = wfp.ymult
        self.yUnitStr       = wfp.yUnitStr
         
    def dump(self):
        line = f"self.rawYdata    = {self.rawXdata}\n"
        line += f"self.rawYdata    = {self.rawYdata}"
        print(line)
        """
        
"""Interface TekVertical
class TekVertical(BaseVertical):

    def __init__(self, nrOfChan, dev):
        super().__init__(nrOfChan, dev) # visa dev will be initted by the Baseclass
        self.nrOfChan = nrOfChan
        
        for i in range(1, nrOfChan+1):
            self.channels.append({i:TekChannel(i, dev)})
            
    def chan(self, chanNr): 
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None     
"""

"""
class TekTrigger(BaseTriggerUnit):
    
    def __init__(self, vertical = None, dev=None):
        super().__init__(vertical, dev)
        self.vertical: TekVertical = vertical
        self.source = 1
        
    def level(self):
        self.visaInstr.query("TRIGger:MAIn:LEVel?")
        
    def level(self, level):
        self.visaInstr.write(f"TRIGGER:MAIN:LEVEL {level}") #Sets Trigger Level in V 
    
    def setSource(self, chanNr):
        
        vertical = self.vertical
        chans = vertical.channels
        theChan : TekChannel = None
        for  i, val in enumerate(chans):
                if (chanNr) in val.keys():
                    theChan = val[chanNr]
        
        if theChan!=None:
            self.visaInstr.write(f"TRIGger:MAIn:EDGE:SOUrce {theChan.name}")
            
    def getEdge(self):
        retDict = {}
        respStr = str(self.visaInstr.query("TRIGGER:MAIN:EDGE?"))
        splitted = respStr.split(";")
        #check if length of splitted equals 3:
        if len(splitted) != 3:
            return "ERROR!"  #TODO temp solution. Better throw exception and retun null dict.
        for prop in splitted:
            propSplit = str(prop).split(" ")
            retDict.update({str(propSplit[0]):str(propSplit[1])}) #TODO: check if dict containt correct fields.
        return retDict        

    def setCoupling(self, coup:str):
        if coup == "AC" or coup == "DC" or coup == "HFRej" or coup == "LFRej":
            self.visaInstr.write(f"TRIGGER:MAIN:EDGE:COUPLING {coup}")
        #TODO: decide whether to log or to print an error message when coup is incorrect.
        
    def setSlope(self, slope:str):
        if slope == "FALL" or slope == "RISe":
            self.visaInstr.write(f"TRIGGER:MAIN:EDGE:SLOPe {slope}")
        #TODO: decide whether to log or to print an error message when coup is incorrect.
        
    def getFrequency(self):
        respStr = str(self.visaInstr.query("TRIGger:MAIn:FREQuency?"))
        freqResp = respStr.split(" ")
        return float(freqResp[1]) #TODO: handle error situations
    
    def getholdOff(self): #Trigger holdoff blz 215 TRIGger:MAIn:HOLDOff:VALue?
        respStr = str(self.visaInstr.query("TRIGger:MAIn:HOLDOff:VALue?"))
        holdOffResp = respStr.split(" ")
        return float(holdOffResp[1]) #TODO: handle error situations
    
    def mode(self): #trigger mode blz 216 TRIGger:MAIn:MODe?
        respStr = str(self.visaInstr.query("TRIGger:MAIn:MODe?"))
        modeResp = respStr.split(" ")
        return str(modeResp[1]) #TODO: handle error situations
    
    def mode(self, modeVal):
        if modeVal == "AUTO" :
            self.visaInstr.write(f"TRIGGER:MAIN:EDGE:SLOPe AUTO")
        if modeVal == "NORMAL":
            self.visaInstr.write(f"TRIGGER:MAIN:EDGE:SLOPe NORMal")
        #TODO: decide whether to log or to print an error message when coup is incorrect.
    
    def getState(self): #tigger state zie blz 223 TRIGger:STATE?
        respStr = str(self.visaInstr.query("TRIGger:STATE?"))
        
        return str(respStr) #TODO: handle error situations
    
"""

"""Interface TekHorizontal
class TekHorizontal(BaseHorizontal):
    
    TIMEBASE_HASHMAP = {
                    "0":"5e-9","1": "10e-9", "2":"25e-9","3":"50E-9",
                    "4":"100e-9","5":"250e-9","6":"500e-9",
                    "7":"1e-6","8":"2.5e-6","9":"5e-6",
                    "10":"10e-6","11":"25e-6","12":"50e-6",
                    
                    "13":"100e-6","14":"250e-6","15":"500e-6",
                    "16": "1e-3", "17": "2.5e-3", "18": "5e-3",
                    "19": "10e-3", "20": "25e-3", "21": "50e-3",
                    "22": "100e-3", "23": "250e-3", "24": "500e-3",
                    "25": "1", "26": "2.5", "27": "5"
                    }
    
         
    def __init__(self, dev = None):
        super().__init__(dev)
    
        
    def setRoll(self, flag:bool):
        print("Let's Roll")
        return None
    
    def getTimeDivs(self):
        return TekHorizontal.TIMEBASE_HASHMAP
    
    def setTimeDiv(self, value):
        self.visaInstr.write (f"HORIZONTAL:MAIN:SECDIV {value}")

"""
