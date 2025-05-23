from enum import Enum
import pyvisa
import numpy as np
import time
import struct

from devices.BaseScope import BaseChannel, BaseWaveForm, BaseWaveFormPreample
from devices.tektronix.scope.TekLogger import TekLog


class TekChannel(BaseChannel):
    IMMEDMEASTYPES =["CRMs","CURSORRms","DELay","FALL",
                        "FREQuency","MAXImum","MEAN","MINImum","NONe","NWIdth","PDUty","PERIod","PHAse", 
                        "PK2pk","PWIdth","RISe"]
    
    @classmethod
    def getChannelClass(cls, chan_no, dev):
        """ Tries to get the right device class, based on the url"""
        if cls is TekChannel:
            return cls
        else:
            return None      
    def __init__(self, chan_no: int, visaInstr:pyvisa.resources.MessageBasedResource):
        super().__init__(chan_no, visaInstr)
        self.name = f"CH{chan_no}"
        self.log = TekLog()
        #if scope != None:
        #    self._parentScope = scope
        self.WFP= TekWaveFormPreamble(visaInstr)
        self.WF = TekWaveForm()
        self.nrOfDivs = 5          # TODO: should be set during initialisation of the scope.
        
        #self.setVisible(state=True)
        self.encoding = None
        
    def queryNrOfSamples(self):
        NR_PT =  int(self.visaInstr.query('WFMPRE:NR_PT?')) #Requesting the number of samples
        return NR_PT     
         
    def setVisible(self, state:bool):
        if state:
            self.visaInstr.write(f"SELECT:{self.name} ON")
            self.isVisible = True
        else:
            self.visaInstr.write(f"SELECT:{self.name} OFF")
            self.isVisible = False
            
    def isVisible(self):
        return self.isVisible
                
    
    def getLastTrace(self):
        return self.WF
       
    def setVertScale(self, scale):
        #TODO check validity of param
        self.visaInstr.write(f"{self.name}:SCALE {scale}") #Sets V/DIV CH1
  
    def setVoltsDiv(self, scale):
        #TODO check validity of param
        vertscalelist = [2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1, 2, 5]
        if scale in vertscalelist:
            self.visaInstr.write(f"{self.name}:SCALE {scale}") #Sets V/DIV CH1   
        else:   
            self.log.addToLog("invalid VDIV input, ignoring.....") 
    
    def setAsSource(self):
        """Sets or queries which waveform will be transferred from the oscilloscope by the
        CURVe, WFMPre, or WAVFrm? queries. You can transfer only one waveform
        at a time.
        """ 
        #check if channel is valid 
        self.visaInstr.write(f"DATA:SOURCE {self.name}") #Sets the channel as data source     
    
    def getSource(self):   
        return self.visaInstr.query(f"DATA:SOURCE?")
    
    def getNrOfPoints(self):
        #TODO:
        # correct handling of event code 2244
        return int(self.visaInstr.query(f"wfmpre:{self.name}:nr_pt?")) #For a channel version of this command:see programming guide page 231
          
    def capture(self):
        """Capture: getting the waveform data from the oscilloscope. This is the Tektronix TDS2000 series 
        implementation. According to the information in the TDS programming manual on page 54, 86, this method 
        implements the following logic:
        2. Use the DATa:ENCdg command to specify the waveform data format.
        3. Use the DATa:WIDth command to specify the number of bytes per data point.
        4. Use the DATa:STARt and DATa:STOP commands to specify the part of the
        waveform that you want to transfer.
        5. Use the WFMPre? command to transfer waveform preamble information.
        6. Use the CURVe command to transfer waveform data.
        1. It sets this channel to be visible, preventing therefore an errormessage send by the scope.
        2. It sets this channel as being the source which has to be transferred by the scope to the computer. As
            the TDS programming manual states on page 86: 'Only one waveform can be transferred at a time.' 
        3. It sets the binary data format for transerring data.
        4. It sets the number of bytes per data point to 1. 
        5. It will query the preamble of this channel.
        6. It will set the relevant data members of this channels waveformdata structure.
        7. It will query the scope for the data.
        8. When data has been transferred, this method will set the relevant datamembers of this channel's waveform
            struct. """
        wfp = self.WFP
        trace = self.WF
        self.setVisible(True)
        self.setAsSource()
        self.visaInstr.write(f"DATa:ENCdg RIBinary")
        self.visaInstr.write(f"DATA:WIDTH 1")
        wfp.queryPreamble()
        trace.setWaveFormID(wfp)
        self.log.addToLog("start querying scope")
        bin_wave = self.visaInstr.query_binary_values('curve?', datatype='b', container=np.array)
        #bin_wave = bin_wave - trace.yoff
        self.log.addToLog("scope query ended")
        trace.rawYdata = bin_wave
        trace.rawXdata = np.linspace(0, wfp.nrOfSamples-1, num=int(wfp.nrOfSamples),endpoint=False)
        total_time = wfp.sampleStepTime * wfp.nrOfSamples
        tstop = wfp.xzero + total_time
        scaled_time = np.linspace( wfp.xzero, tstop, num=int(wfp.nrOfSamples))
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        scaled_wave = (unscaled_wave - trace.yoff) *  trace.ymult  + trace.yzero
        #put the data into internal 'struct'
        trace.scaledYdata = scaled_wave
        trace.scaledXdata = scaled_time
        
    
    ##### DATA TRANSFER RELATED METHODS ######
    def queryEncoding(self):
        return self.visaInstr.query("DATa:ENCdg?")
    

    def queryWaveFormPreamble(self):
        #TODO add intern state for ascii or binary. Defines query or binary_query
        self.setAsSource()
        response = self.visaInstr.query('WFMPRE?')
        self.WFP.decode(response)


    #### IMMED MEASUREMENT METHODS #####
    def getAvailableMeasurements(self):
        return TekChannel.IMMEDMEASTYPES
        
    def getImmedMeasParam(self):
        """Returns all immediate measurement setup parameters. Immediate queries
        and commands are the preferred methods for programming. An immediate
        measurement selection is not visible or accessible through the display screen
        or front panel."""
        response = self.visaInstr.query("MEASUrement:IMMed?")
        return response
    
    def immedMeasType(self):
        """Queries the immediate type of measurement configured for this TDS oscilloscope"""
        return str(self.visaInstr.query(f"MEASUREMENT:IMMED:TYPE?"))

    def immedMeasType(self, measType):
        """Sets the immediate type of measurement to be executed by this TDS oscilloscope.
        The parameeter measType must be one of:
        CRMs        : calculate true Root Mean Square voltage of the first complete cycle in the
                        waveform
        CURSORRms   : Same as CRMs but between start and end point.
        DELay       : the delay from one waveform's edge event to another
        FALL        : is the fall time between 90% and 10% of the first falling edge of the waveform. 
                        Falling edge must be displayed to measure. The oscilloscope automatically 
                        calculates the 10% and 90% measurement points.
        FREQuency   : the reciprocal of the period measured in Hertz.
        MAXImum     : the value of the largest point in the waveform.
        MEAN        : the arithmetic mean over the entire waveform.
        MINImum     : the value of the smallest point in the waveform.
        NONe        : disables the measurement specified by <x>
        NWIdth      : the negative pulse width between the first falling edge and the next rising edge 
                        at the waveform 50% level. Falling and rising edges must be displayed to measure. 
                        The oscilloscope automatically calculates the 50% measurement point.
        PDUty       :
        PERIod      : the duration, in seconds, of the first complete cycle in the waveform.
        PHAse 
        PK2pk       : the absolute difference between the maximum and minimum amplitude.
        PWIdth      : the positive pulse width between the first rising edge and the next falling edge at
                        the waveform 50% level. Rising and falling edges must be displayed to measure. 
                        The oscilloscope automaticall0 calculates the 50% measurement point.
        RISe        : vthe rise time between 10% and 90% of the first rising edge of the waveform. Rising 
                        edge must be displayed to measure. The oscilloscope automatically calculates the 
                        10% and 90% measurement points.
        """
        for hulp in TekChannel.IMMEDMEASTYPES:
            if measType == hulp or measType == hulp.upper() or measType == hulp.lower():
                self.visaInstr.write(f"MEASUREMENT:IMMED:TYPE {measType}")        
            
    def doImmedMeas(self, measType):
        """Starts immediate measurements of a prior setted measurement type to be performed periodically by this TDS oscilloscope
        Remark: this method does not check ESR of events setted or fired, as noted by the programmers manual on page 162:
        NOTE. If the channel specified by MEASUrement:IMMed:SOUrce is not currently
        displayed, the oscilloscope generates event 2225 and returns 9.9E37.
        If Trigger View is active, Scan mode is in effect, or the display format is set to XY,
        this query returns 9.9E37 and generates event 221 (Settings conflict)
        When math is FFT, turned on, and used as a measurement source, attempting to
        query the measurement value returns 9.9e37 and raises error 2225 (no waveform
        to measure)."""
        self.immedMeasType(measType)
        self.visaInstr.write(f"MEASUREMENT:IMMED:SOURCE {self.name}")
        return self.visaInstr.query("MEASUrement:IMMed:VALue?")
        
    def getMean(self):
        """Gets the mean of this channel's waveform by doing an Immediate Measurement"""
        response = self.doImmedMeas("MEAN")        
        return float(response)
    
    def getMax(self):
        """Gets the maximum value of highest point in this channel's waveform by doing an Immediate 
        Measurement"""
        response = self.doImmedMeas("MAXImum")        
        return float(response)

    

class TekWaveFormPreamble(BaseWaveFormPreample):
    """Class for holding the Tektronix TDS1000 scope series preamble. Extends BaseWaveFormPreamble.
    A preample is data describing the unit, range and spacing of a Waveform."""

    @classmethod
    def getWaveFormPreambleClass(cls, dev):
        """ Tries to get (instantiate) the right instance based on the type"""
        if cls is TekWaveFormPreamble:
            return cls
        else:
            return None      

    def __init__(self, dev:pyvisa.resources.MessageBasedResource=None):
        """TekWaveFormPreamble init. Inits all datamembers to the value None.
        Following data members are set:
        self.nrOfBytePerTransfer   : Number of bytes per sample or in total => check!
        self.nrOfBitsPerTransfer   : Number of bits per sample or in total => check!
        self.encodingFormatStr     : Encoding sting used during transfer, see documentation
        self.binEncodingFormatStr  : Encoding used during transfer, binary, see documentation
        self.binFirstByteStr       : Location of first byte(? Checken!), see documentation
        self.nrOfSamples           : number of samples of acquired waveform
        self.vertMode              : Indicaties YT,XY, or FFT mode
        self.sampleStepTime        : Sampleperiode (?, CHECKEN)
        self.xincr                 : Time between to samples
        self.xzero                 : Location of X=0 on screen horizontally
        self.xUnitStr              : Horizontal axis unit
        self.ymult                 : Vertical gain, or VDIV
        self.yzero                 : Location of Y=0 on screen vertically
        self.yoff                  : Vertical offset on the display
        self.yUnitStr              : Vertical axis unit"""
        super().__init__(dev=dev)
        ##### START OF TEKTRONIX TDS TYPICAL PARAMETERS DEFINITION ####### 
        self.nrOfBytePerTransfer   = None
        self.nrOfBitsPerTransfer   = None
        self.encodingFormatStr     = None
        self.binEncodingFormatStr  = None
        self.binFirstByteStr       = None
        self.nrOfSamples           = None
        self.vertMode              = None #Y, XY, or FFT.
        self.sampleStepTime            = None
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
        self.sampleStepTime         = float(paramlist[8])
        self.xincr                  = float(paramlist[8])
        self.xzero                  = float(paramlist[10])
        self.xUnitStr               = str(paramlist[11])
        self.ymult                  = float(paramlist[12])
        self.yzero                  = float(paramlist[13])
        self.yoff                   = float(paramlist[14])
        self.yUnitStr               = str(paramlist[15])
        self.decodeChanPreamble(paramlist[6])
        
    def queryPreamble(self):
        """Method for getting the preamble of the scope and set the correct data members
        of this preamble"""
        response = self.visaInstr.query("WFMPRE?")
        self.decode(response)
    
    def decodeChanPreamble(self, chanStrToDecode):
        """Method for decoding the query data of the scope and set the correct data members
        of this preamble"""
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

    @classmethod
    def getWaveFormClass(cls):
        """ Tries to get (instantiate) the right instance based on the type"""
        if cls is TekWaveForm:
            return cls
        else:
            return None      
        
    def __init__(self):
        ####TEKTRONIX TDS SPECIFIC WAVEFORM PARAMS ########
        super().__init__()
        self.rawYdata       = None #data without any conversion or scaling taken from scope
        self.rawXdata       = None #just an integer array
        self.scaledYdata    = None #data converted to correct scale e.g units
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
        self.sampleStepTime = None # same as XINCR, Ts = time between to samples.
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
        self.sampleStepTime = wfp.sampleStepTime
        self.yzero          = wfp.yzero
        self.yoff           = wfp.yoff
        self.ymult          = wfp.ymult
        self.yUnitStr       = wfp.yUnitStr
         
    def dump(self):
        line = f"self.rawYdata    = {self.rawXdata}\n"
        line += f"self.rawYdata    = {self.rawYdata}"
        print(line)