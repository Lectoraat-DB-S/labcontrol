import pyvisa as visa
import numpy as np

from tektronix.scope.Channel import TekChannel
from tektronix.scope.Acquisitions import TekScopeEncodings, WaveformPreamble
from tektronix.scope.TekLogger import TekLog

class TekScope(object):
    def __init__(self):
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
                    #self.setToDefault()
                    break
            else:
                self.log.addToLog("Tekscope: no Tektronix found on USB.")        

    #Returns the handle to the connected (VISA) instrument or None if no instrument found.
    def getDevice(self):
        return self._inst
    
    def setToDefault(self):
        self.setBinEncoding()
        self.setNrOfByteTransfer(1)
        for chan in self._channels:
            pass
            
    def queryWaveFormPreamble(self):
        #TODO add intern state for ascii or binary. Defines query or binary_query
        response = self._inst.query('WFMPRE?')
        print(response)
        preamble = WaveformPreamble()
        preamble.decode(response)
        print(preamble)
    
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
    
    """
    WFMPre:NR_Pt? (Query Only)
    Returns the number of points that are in the transmitted waveform record, as
    specified by DATa:SOUrce. The number of points depends on DATa:STARt,
    DATa:STOP, and whether DATa:SOUrce is YT or FFT. NR_Pt is at most 2500 for
    YT and 1024 for FFT. NR_Pt is always at least one.
    When the DATa:SOUrce is not displayed, the TDS210 and TDS220 (firmware
    below V 2.00) with a TDS2CMA communications module will return a value. All
    other oscilloscope, firmware version, and module combinations will generate an
    error and will return event code 2244.
    """
    def getNrOfPoints(self):
        #TODO:
        # correct handling of event code 2244
        return int(self._inst.query('wfmpre:nr_pt?')) #For a channel version of this command:see programming guide page 231
        
            
    def setTimeBase(self, time):
        #TODO check validity of time param
        self._inst.write(f"HORizontal:MAIn:SCAle {time}")
        #print(self._inst.query("HORizontal:MAIn:SCAle?"))
    
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
    