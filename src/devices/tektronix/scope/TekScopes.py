import pyvisa
import numpy as np
import socket
from devices.BaseScope import BaseScope, BaseVertical, BaseHorizontal
from devices.tektronix.scope.Horizontal import TekHorizontal
from devices.tektronix.scope.Vertical import TekVertical
from devices.tektronix.scope.Trigger import TekTrigger
from devices.tektronix.scope.Acquisition import TekAcquisition
from devices.tektronix.scope.display import TekDisplay
from devices.BaseConfig import BaseDeviceConfig, BaseScopeConfig, LabcontrolConfig
from enum import Enum
from devices.tektronix.scope.TekLogger import TekLog

debug=True

class TekScopeEncodings(Enum):
    ASCII = "ASCi"
    RIBinary = "RIBinary" #Signed Integer, most significant byte first, fastest
    RPBinary = "RPBinary" #positive Integer, most significant byte first
    SRIbinary = "SRIbinary"#Signed Interger, least significant byte first.
    SRPbinary = "SRPbinary"#positive Integer, least significant byte first
      

class TekScope(BaseScope):
    
    @classmethod
    def getScopeClass(cls, rm, urls, host, scopeConfig: BaseScopeConfig = None):
        """
            This method will:
            1. Traverses all url's provided by parameter urls
            2  returns either the class of a Tektronix TDS 2kC series oscilloscope and the corresponding VISA object,
            if the url or idn response matches, or 
            3. returns None for both, if not.
            
            This method will be called by the BaseScope class during a factory process of creating a new BaseScope object:
            a. An user calls BaseScope.getDevice()
            b. BaseScope.getDevice loops the list of registered subclasses
            c. Every subclass's getScopeClass will be called, searching for a match.
            d1. If so, BaseScope. getDevice calls the __init__ method of the matched subclass type to start its creation and
                exits by returning the correct scope object
                Or, by not finding a match at all:
            d2. exits by returning None.
            
            BaseScope needs the correct scope type and an opened VISA reference to the TDS scope device to excute above
            mentioned factory process. 

            getScopeClass returns a tuple (cls ,instr) where cls is the class of the object and instr the opened reference to the 
            device when matched, or (None, None) if not. 
          
        """    
        if cls is TekScope:
            # As the TDS2k hasn't got a utp connection, the only option is usb.
            # But to be consistent with the Siglent implementation, this implementation follows next logic:
            # First try to find a Tektronix oscilloscope on USB. If not available, check the availability of a config object and ipaddress.
            # If not, return None.
            urlPattern = "USB" 
            mydev : pyvisa.resources.MessageBasedResource = None 
            
            for url in urls:
                if urlPattern in url:
                    mydev = rm.open_resource(url)
                    mydev.timeout = 10000
                    #mydev.chunk_size = 20480
                    
                    mydev.encoding = 'latin_1'
                    mydev.read_termination = None # See discussion https://github.com/pyvisa/pyvisa/issues/741
                    mydev.write_termination = None 
                    mydev.write('*cls') # clear ESR
                    mydev.write("HEADER OFF\n") # No header => less data. TDS used during test was configured with no header. To be sure: turn it off.
                    desc = mydev.query("*IDN?")
                    
                    if desc.find("TEKTRONIX,TDS") > -1: #Tektronix device found via IDN.
                        return (cls, mydev, scopeConfig)
            
                        
            if scopeConfig == None:
                return (None, None)
            for myConfig in scopeConfig:
                mydev = cls.SocketConnect(rm=rm, scopeConfig=myConfig)
                if mydev != None:
                    desc = mydev.query("*IDN?")
                    if desc.find("TEKTRONIX,TDS") > -1: #Tektronix device found via IDN.
                        mydev.write('*cls') # clear ESR
                        mydev.write("HEADER OFF\n") # No header => less data. TDS used during test was configured with no header. To be sure: turn it off.
                        return (cls, mydev, myConfig)
            return (None, None)        
            
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource = None, myconfig: BaseScopeConfig = None):
    #def __init__(self, visaResc: pyvisa.resources.MessageBasedResource):
        """ 
            Constructor for Tektronix TDS oscilloscoop. This class is a subclass of BaseScope. BaseScope implements
            the autoregristration scheme for subclasses of PEP487 which is available since python 3.6. 
        """
        super().__init__(visaInstr, myconfig) #baseclass will store referentie to the device.
        # set binary encoding and transfer 1 byte per sample, for fast communication between computer and devices.
        self.visaInstr.write(f"DATa:ENCdg RIBinary")
        self.visaInstr.write(f"DATA:WIDTH 1")
       
        #self.setToDefault(self)
        #TODO: set below with myconfig content.
        self.nrOfHoriDivs = 10 # maximum number of divs horizontally
        self.nrOfVertDivs = 10 # maximum number of divs vertically 
        self.visibleHoriDivs = 10 # number of visible divs on screen
        self.visibleVertDivs = 8 # number of visible divs on screen
        self.horizontal = TekHorizontal(visaInstr)
        self.vertical = TekVertical(2, visaInstr, self.nrOfHoriDivs, self.nrOfVertDivs,
                                         self.visibleHoriDivs, self.visibleVertDivs)

        self.trigger = TekTrigger(self.vertical,visaInstr)
        self.acquisition = TekAcquisition(visaInstr)
        self.display = TekDisplay(visaInstr)
        self.vertical.setProcMode(self.mode) #calling the baseclass method for setting the selected mode.


    def setProcMode(self, mode):
        super().setProcMode(mode)
       
       
    def setToDefault(self):
        self.setBinEncoding()
        self.setNrOfByteTransfer(1)

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
                
    def getNrOfPoints(self):
        #TODO:
        # correct handling of event code 2244
        return int(self.visaInstr.query('wfmpre:nr_pt?')) #For a channel version of this command:see programming guide page 231  
    
    def setDataTransferWidth(self,width):
        #TODO: check validity of width param     
        self.visaInstr.write(f"DATA:WIDTH {width}")
        
    def time(self):
        """Queries this TDS oscilloscope current time setting. Returns a string in hh:mm:ss format."""
        return str(self.visaInstr.query("TIMe?"))
    
    def time(self, timeVal):
        """Set this TDS oscilloscope time setting. timeVal must be a string in hh:mm:ss format."""
        self.visaInstr.write(f"TIMe {timeVal}")
        
    def setStartSampleNr(self, startNr):
        #TODO check if startNr is correct
        self.visaInstr.write(f"DATA:START {startNr}") #Sets start of sample data 
        self.visaInstr.write("DATA:STOP 2500") #Sets end of sample data
    
    def setStopSampleNr(self, stopNr):
        #TODO check if startNr is correct
        self.visaInstr.write(f"DATA:STOP {stopNr}") #Sets end of sample data

    ######### GPIB & Miscellinaneous COMMANDS ######
    def DESE(self):
        return self.visaInstr.query("DESE?")
    
    def DESE(self, bitsVal):
        self.visaInstr.write(f"DESE {bitsVal}")

    def ESE(self):
        return self.visaInstr.query("*ESE")
    
    def ESE(self, bitsVal):
        self.visaInstr.write(f"*ESE {bitsVal}")

    def ESR(self):
        return self.visaInstr.query("*ESR?")
    
    def ESR(self, bitsVal):
        self.visaInstr.write(f"*ESR {bitsVal}")

    def getAllEvents(self):
        return self.visaInstr.query("ALLEV?")

    def getLastEvents(self):
        return self.visaInstr.query("EVENT?")
    
    def getNrOfEvents(self):
        return self.visaInstr.query("EVQty?")

    def EVMsg(self):
        """"""
        return self.visaInstr.query("EVMsg?")
    
    def clear(self):
        self.visaInstr.write("*CLS")
    
    def STB(self):
        """"""
        return self.visaInstr.query("STB?")
    
    def getDefault(self):
        return self.visaInstr.query("FACtory?")
    
    def acquire(self):
        return self.visaInstr.query("ACQuire?")
    
    def acquire(self, state, mode=None, nrOfAvg=None, stopAfter=None):
        acqStr = ""
        if state == "OFF" or state =="ON" or state =="RUN" or state =="STOP":
            pass
        else:
            state = "RUN"
            
        acqStr += f"ACQUIRE:STATE {state}"

        if nrOfAvg == 4 or nrOfAvg == 16 or nrOfAvg == 64 or nrOfAvg == 128:
            acqStr += f"; NUMAVG {nrOfAvg}"

        if mode =="SAMPLE" or mode == "PEAKdetect" or mode == "AVErage":
            acqStr += f"; MODE {mode}"

        if stopAfter== "RUNSTop" or stopAfter == "SEQUENCE":
            acqStr += f"; STOPAFTER {stopAfter}"
        
        self.visaInstr.write(acqStr)
    