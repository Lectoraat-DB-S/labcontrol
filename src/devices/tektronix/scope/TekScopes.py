import pyvisa as visa
import numpy as np
import socket
from devices.BaseScope import BaseScope, BaseVertical, BaseHorizontal
from devices.tektronix.scope.Horizontal import TekHorizontal
from devices.tektronix.scope.Vertical import TekVertical
from devices.tektronix.scope.Trigger import TekTrigger

from devices.tektronix.scope.TekLogger import TekLog

debug=True

class TekScope(BaseScope):
    
    @classmethod
    def getDevice(cls, rm, urls, host):
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
                            cls.__init__(cls, mydev)
                            return cls
                            
            else:
                try:
                    ip_addr = socket.gethostbyname(host)
                    addr = 'TCPIP::'+str(ip_addr)+'::INSTR'
                    mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                    cls.__init__(cls,mydev)
                    return cls
                except socket.gaierror:
                    
                    return None
        else:
            return None
    
    def __init__(self, dev):
        """ 
            Constructor for Tektronix TDS oscilloscoop. This class is a subclass of BaseScope. BaseScope implements
            the autoregristration scheme for subclasses of PEP487 which is available since python 3.6. 
        """
        #Edit 26-04-2025: commented line below. Calling super at this state will mess up the scope object creation
        #process.
        #super().__init__(dev) #baseclass will store referentie to the device.
        self.horizontal = TekHorizontal(dev)
        self.vertical = TekVertical(2, dev)
        self.trigger = TekTrigger(self.vertical,dev)
       
       
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
    