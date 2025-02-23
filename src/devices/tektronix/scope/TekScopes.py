import pyvisa as visa
import numpy as np
import socket
from devices.BaseScope import BaseScope
from devices.tektronix.scope.Acquisitions import TekScopeEncodings, WaveformPreamble
from devices.tektronix.scope.Channel import TekChannel

from devices.tektronix.scope.TekLogger import TekLog

class TekScope(BaseScope):
    
    @classmethod
    def getDevice(cls, urls, host):
        """
            Tries to get (instantiate) this device, based on matched url or idn response
            This method will ONLY be called by the BaseScope class, to instantiate the proper object during
            creation by the __new__ method of BaseScope.     
        """    
        urlPattern = "USB" #fix for now, TODO: make more robust e.g. able to connect to TCP or serial.
        if host == None:
            for url in urls:
                if urlPattern in url:
                    rm = visa.ResourceManager()
                    mydev = rm.open_resource(url)
                    mydev.timeout = 10000  # ms
                    mydev.read_termination = '\n'
                    mydev.write_termination = '\n'
                    desc = mydev.query("*idn?")
                    if desc.find("TEKTRONIX,TDS") > -1: #Tektronix device found via IDN.
                        cls.visaInstr = mydev
                        return cls        
        else:
            try:
                ip_addr = socket.gethostbyname(host)
                addr = 'TCPIP::'+str(ip_addr)+'::INSTR'
                mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                cls.visaInstr = mydev
                return cls
            except socket.gaierror:
                
                return None
        
        return None

    def __init__(self, host = None):
        """ 
            Constructor for Tektronix TDS oscilloscoop. This class is a subclass of BaseScope. BaseScope implements
            the autoregristration scheme for subclasses of PEP487 which is available since python 3.6. 
        """
    
        self._channels = []
        self.log = TekLog()
        rm = visa.ResourceManager()
        self._inst = None # None means unconnected state of the scope.
        theList = rm.list_resources()
        pattern = "USB" #fix for now, TODO: make more robust e.g. able to connect to TCP or serial.
        for url in theList:
            if pattern in url:
                self.log.addToLog("VISA device found on USB")
                mydev = rm.open_resource(url)
                mydev.timeout = 10000  # ms
                mydev.read_termination = '\n'
                mydev.write_termination = '\n'
                desc = mydev.query("*idn?")
                if desc.find("TEKTRONIX,TDS") > -1:
                    self._inst = mydev
                    self.log.addToLog("Tektronix TDS found, assuming a two Channel TDS2002B")
                    # self._idn.decodeIDN(desc)
                    #TODO: based on IDN detect type/model scope and based on that instantiate number of channel
                    #code below assumes TDS2002B/C with 2 channels
                    myCH1 = TekChannel(1, mydev)#TODO:code has te be removed, because of list of Channels.
                    self.CH1 = myCH1            #TODO:code has te be removed, because of list of Channels.
                    self.CH1.setVisible(True)
                    self._channels.append(myCH1)
                    myCH2 = TekChannel(2, mydev)#TODO:code has te be removed, because of list of Channels.
                    self.CH2 = myCH2            #TODO:code has te be removed, because of list of Channels.
                    self.CH2.setVisible(True)
                    self._channels.append(myCH2)
                    self.setToDefault()
                    self.preamble = WaveformPreamble(mydev)
                    self.preamble.queryPreamble()
                    break
            else:
                self.log.addToLog("Tekscope: no Tektronix found on USB.")        
    
    def setToDefault(self):
        self.setBinEncoding()
        self.setNrOfByteTransfer(2)

    
    ##### DATA TRANSFER RELATED METHODS ######
    def queryEncoding(self):
        return self._inst.query("DATa:ENCdg?")
    
    
    #TODO: might be better to move encoding to channel. This is the case if scope holds last encoding settings on a channel base.
    def setEncoding(self, encoding: TekScopeEncodings):
        if isinstance(encoding, TekScopeEncodings):
            if (encoding==encoding.RIBinary or encoding==encoding.ASCII or 
                encoding==encoding.RPBinary or
                encoding==encoding.SRIbinary or
                encoding==encoding.SRPbinary):
                self._inst.write(f"DATa:ENCdg {encoding.value}")
        else:
            self.log.addToLog("Unknown encoding type. switch to RIBinary format")
            self._inst.write(f"DATa:ENCdg {encoding.RPBinary.value}")
    
    def setBinEncoding(self):
        self._inst.write('data:encdg RIBINARY')
    
    #FOR TEKTRONIX TDS series nrOfBytes is 1 or 2.
    def setNrOfByteTransfer(self, nrOfBytes=1):
        if (nrOfBytes==1):
            self._inst.write('wfmpre:byt_nr 1')
        elif (nrOfBytes==2):
            self._inst.write('wfmpre:byt_nr 2')
        else:
            self._inst.write('wfmpre:byt_nr 1')
            self.log.addToLog("ÏNVALID USER SETTING! Number of byte transfer set to one.")
    
    def getNrOfPoints(self):
        #TODO:
        # correct handling of event code 2244
        return int(self._inst.query('wfmpre:nr_pt?')) #For a channel version of this command:see programming guide page 231
        
            
    def setTimeBase(self, time):
        #checkinp of time param is not necessary: the scope forces incorrect values to the nearest acceptable value
        self._inst.write(f"HORizontal:MAIn:SCAle {time}")
        #print(self._inst.query("HORizontal:MAIn:SCAle?"))
        
    def setTimeDiv(self, time):
        self.setTimeBase(time)
    
    def setTrigger(self, level):
        self._inst.write(f"TRIGGER:MAIN:LEVEL {level}") #Sets Trigger Level in V 
    
    #moved to channel and renamed it.
    #def queryHorizontalPositon(self):
    #    SEC_DIV = float(self._inst.query('HORIZONTAL:MAIN:SECDIV?')) #Requesting the horizontal scale in SEC/DIV
 
    def setHorizontalPositon(self, pos):
        self._inst.write(f"HORizontal:POSITION {pos}") #Sets Horizontal Position in s
   
    """
        Sets or queries which waveform will be transferred from the oscilloscope by the
        CURVe, WFMPre, or WAVFrm? queries. You can transfer only one waveform
        at a time.
    """   
    def setChanAsDataSource(self,channel):
        #check if channel is valid 
        self._inst.write(f"DATA:SOURCE {channel}") #Sets the channel as data source     
    
    def setDataTransferWidth(self,width):
        #TODO: check validity of width param     
        self._inst.write(f"DATA:WIDTH {width}")
        
        
    def setStartSampleNr(self, startNr):
        #TODO check if startNr is correct
        self._inst.write(f"DATA:START {startNr}") #Sets start of sample data 
        self._inst.write("DATA:STOP 2500") #Sets end of sample data
    
    def setStopSampleNr(self, stopNr):
        #TODO check if startNr is correct
        self._inst.write(f"DATA:STOP {stopNr}") #Sets end of sample data

    def queryNrOfSamples(self):
        NR_PT =  int(self._inst.query('WFMPRE:NR_PT?')) #Requesting the number of samples
        return NR_PT
    
    class Horizontal(object):
        def __init__(self, position:float):
            self._position = position
        
        def setPosition(self, pos):
            pass
        
        def setScale(self, tdiv):
            pass
        
        def setSecDiv(self, tdiv):
            self.setScale(tdiv)
        
        def setTimeDiv(self, tdiv):
            self.setScale(tdiv)    