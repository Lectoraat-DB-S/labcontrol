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
            Tries to get (instantiate) this device, based on matched url or idn response
            This method will ONLY be called by the BaseScope class, to instantiate the proper object during
            creation by the __new__ method of BaseScope.     
        """    
        if cls is TekScope:
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
                            return (cls, mydev)
                        else:
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
    
    def __init__(self, host: str, visaInstr:pyvisa.resources.MessageBasedResource):
    #def __init__(self, visaResc: pyvisa.resources.MessageBasedResource):
        """ 
            Constructor for Tektronix TDS osself, cilloscoop. This class is a subclass of BaseScope. BaseScope implements
            the autoregristration scheme for subclasses of PEP487 which is available since python 3.6. 
        """
        super().__init__(host,visaInstr) #baseclass will store referentie to the device.
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
    