import pyvisa
import numpy as np
import socket
from devices.BaseScope import BaseScope, BaseVertical, BaseHorizontal
from devices.tektronix.scope.Horizontal import TekHorizontal
from devices.tektronix.scope.Vertical import TekVertical
from devices.tektronix.scope.Trigger import TekTrigger
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
    def getScopeClass(cls, rm, urls, host):
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
            urlPattern = "USB" 
            if host == None:
                for url in urls:
                    if urlPattern in url:
                        mydev = rm.open_resource(url)
                        mydev.timeout = 10000
                        mydev.chunk_size = 20480
                        
                        mydev.encoding = 'latin_1'
                        mydev.read_termination = None # See discussion https://github.com/pyvisa/pyvisa/issues/741
                        mydev.write_termination = None 
                        mydev.write('*cls') # clear ESR
                        mydev.write("HEADER OFF\n") # No header => less data. TDS used during test was configured with no header. To be sure: turn it off.
                        desc = mydev.query("*IDN?")
                      
                        if desc.find("TEKTRONIX,TDS") > -1: #Tektronix device found via IDN.
                            return (cls, mydev)
                
                return (None, None)
                            
            else:
                try:
                    ip_addr = socket.gethostbyname(host)
                    addr = 'TCPIP::'+str(ip_addr)+'::INSTR'
                    mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                    cls.__init__(cls,mydev)
                    return (cls, mydev)
                except socket.gaierror:
                    print("Socket Error")
                    return (None, None)
        else:
            return (None, None)
    
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
    #def __init__(self, visaResc: pyvisa.resources.MessageBasedResource):
        """ 
            Constructor for Tektronix TDS oscilloscoop. This class is a subclass of BaseScope. BaseScope implements
            the autoregristration scheme for subclasses of PEP487 which is available since python 3.6. 
        """
        super().__init__(visaInstr) #baseclass will store referentie to the device.
        # set binary encoding and transfer 1 byte per sample, for fast communication between computer and devices.
        self.visaInstr.write(f"DATa:ENCdg RIBinary")
        self.visaInstr.write(f"DATA:WIDTH 1")
        self.horizontal = TekHorizontal(visaInstr)
        self.vertical = TekVertical(2, visaInstr)
        self.trigger = TekTrigger(self.vertical,visaInstr)
        #self.setToDefault(self)
       
       
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
    