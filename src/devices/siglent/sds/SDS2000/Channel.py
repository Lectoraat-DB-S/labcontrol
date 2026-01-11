#New version
import time
import struct
import numpy as np
from enum import Enum
import pyvisa
import logging
import time
from devices.siglent.sds.util import splitAndStripHz, splitAndStripSec, splitAndStripV 
from devices.siglent.sds.util import TIMEBASE_HASHMAP
import configparser
from devices.siglent.sds.SDS2000.commands_full import SCPI

from devices.BaseScope import BaseChannel, BaseWaveForm, BaseWaveFormPreample


# SDSChannel: abstraction of a Siglent oscilloscope channel.
# Usage: set or get 'vertical' channel properties of a scope and/or start a capture.
# Assumption: all channels of a scope model a equivalent.
# Getting vertical div, vertical offset,


class SDS2kChannel(BaseChannel):
    #IMMEDMEASTYPES =["CRMs","CURSORRms","DELay","FALL",
    #                    "FREQuency","MAXImum","MEAN","MINImum","NONe","NWIdth","PDUty","PERIod","PHAse", 
    #                    "PK2pk","PWIdth","RISe"]
    
    @classmethod
    def getChannelClass(cls, chan_no, dev):
        """ Tries to get (instantiate) the device, based on the url"""
        if cls is SDS2kChannel:
            return cls
        else:
            return None      
    
    def __init__(self, chan_no: int, visaInstr:pyvisa.resources.MessageBasedResource):
        super().__init__(chan_no, visaInstr)
        self.name = f"CHANnel{chan_no}"
        self.visaInstr: pyvisa.resources.MessageBasedResource = visaInstr
        self.WFP= SDSWaveFormPreamble(visaInstr)
        self.WF = SDS2kWaveForm()
        self.WF.setInstr(visaInstr)
        self.WF.setChanId(self.name)

    def query(self, cmd: str):
        return self.visaInstr.query(cmd)
    
    def write(self, cmd: str):
        self.visaInstr.write(cmd)
    
    def setVisible(self, state:bool):
        tState = "ON"
        if state:
            tState = "ON"
        else:
            tState = "OFF"
                
        self.write(SCPI["CHANNEL"]["switch"](self.chanNr, tState))
    
    def isVisible(self):
        pass

    def position(self):
        """Gets the (vertical) position of this channel with respect to the center graticule. Unit of position is divisions (divs)."""
        return self.query(SCPI["CHANNEL"]["offset?"](self.chanNr))


    def position(self, pos):
        """"Sets the (vertical) position of this channel with respect to center. Parameter pos is the deviation from center in divisions (divs). 
        A positive value means above center, negative means below center. """
        self.write(SCPI["CHANNEL"]["offset"](self.chanNr, pos))
    
    def getVdiv(self):
        """Gets the vertical sensitivity (i.e. Vdiv) of this channel. This is the default method for setting  
        Vdiv, as defined in BaseChannel.
        """
        VDIV = self.query(SCPI["CHANNEL"]["scale?"](self.chanNr))
        return VDIV
    
    def setVdiv(self, value):
        """Sets the vertical sensitivity (i.e. Vdiv) of this channel. This is the default method for setting  
        Vdiv, as defined in BaseChannel.
        """
        #self.write(f"{self.name}:VDIV {value}")
        self.write(SCPI["CHANNEL"]["scale"](self.chanNr, value))

    def setVoltsDiv(self, value):
        """Sets the vertical sensitivity (i.e. Vdiv) of this channel. This is the alternative method for setting  
        Vdiv. Same functionality as 'setVdiv'.
        """
        self.setVdiv(value)

    def getYoffset(self): #TODO: was getYzero, check of reference are not broken by rename.
        """Gets the vertical offset of this channel. For this SDS implementation the parameter 
        'yoff' will be queried. 
        """
        VOFS = self.query(SCPI["CHANNEL"]["offset?"](self.chanNr))
        return VOFS
    
    def getXzero(self):
        """Gets the horizontal offset of this channel on display. For this SDS implementation, the trigger delay parameter 
        has been selected.
        """
        return self.query(SCPI["TIMEBASE"]["position?"]())

    
    def getWaveformPreamble(self):
        """The query returns the parameters of the source using by the command
        :WAVeform:SOURce.
        See text output from a Siglent scope for reference. See Repo.
        """
        wvpRespStr = self.visaInstr.query_binary_values(f"{self.name}:WaveForm? DESC", datatype='B', is_big_endian=False, container=np.ndarray)
        self.WFP.decodePreambleStr(params=wvpRespStr)
        
    def capture(self)->BaseWaveForm:
        self.getWaveformPreamble() #for quering the preamble, in order to have fresh WVP
        data = self.visaInstr.query_binary_values(f"{self.name}:WF? DAT2", datatype='B', is_big_endian=False, container=np.ndarray)
        try:
            
            trace = np.frombuffer(data, dtype=np.byte)
            self.WF.rawYdata = trace
            self.WF.rawXdata = np.linspace(0, self.WFP.nrOfSamples-1, num=int(self.WFP.nrOfSamples),endpoint=False)
            self.WF.rawYToVolts(self.WFP.vdiv, self.WFP.yoff)
            self.WF.rawXtoTime(self.WFP.trigDelay, self.WFP.xincr,self.WFP.timeDiv, self.WFP.nrOfSamples)
            return self.WF
        except Exception as e:
            #TODO: fix logger hassle
            #self.logger.error(e)
            print("Exception during capture SDS!!")
            return None
    
    ########## PARAMETER MEASUREMENTS (PAVA) ###########
    
    def getAvailableMeasurements(self):
        """Gets the available (parameter) measurements of this channel, by using a SDS built-in function."""
        return self.query(f"{self.name}:PAVA? ALL")

    def getBase(self):
        return float( self.query(f"{self.name}:PAVA? BASE"))
    
    def getNDuty(self):
        return float( self.query(f"{self.name}:PAVA? NDUTY"))
    
    #negative width
    def getNWid(self):
        """Gets the (negative) pulse widht of the waveform of this channel, by using a SDS built-in function."""
        return float( self.query(f"{self.name}:PAVA? NWID"))
    
    #negative overshoot
    def getOvSN(self):
        """Gets the (negative) overshoot of the waveform of this channel, by using a SDS built-in function."""
        return float( self.query(f"{self.name}:PAVA? OVSN"))
    
    #mean for cyclic waveform
    def getCMean(self):
        """Gets the cyclic Mean of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self.name}:PAVA? CMEAN")
        return splitAndStripV(response)
    
    #positive overshoot
    def getOvSP(self):
        """Gets the (positive) overshoot of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self._name}:PAVA? OVSP")
        return float(response)
    
    #root mean square for cyclic part of waveform
    def getCMRS(self):
        """Gets the cyclic RMS of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self._name}:PAVA? CRMS")
        return splitAndStripV(response)
     
    #duty cycle
    def getDuty(self):
        """Gets the dutycycle of the waveform of this channel, by using a SDS built-in function."""
        response =self.query(f"{self._name}:PAVA? DUTY")
        return float(response)
    
    #period
    def getPeriod(self):
        """Gets the period of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self._name}:PAVA? PER")
        return splitAndStripSec(response)

    #falltime
    def getFall(self):
        """Gets the fall time of the waveform of this channel, by using a SDS built-in function."""
        response =self.query(f"{self.name}:PAVA? FALL")
        return splitAndStripSec(response)
    
    #(Vmin-Vbase)/ Vamp before the waveform rising transition
    def getRPRE(self):
        response =self.query(f"{self.name}:PAVA? RPRE")
        return float(response )
    
    #positive width
    def getPwidth(self):
        response = self.query(f"{self.name}:PAVA? PWID")
        return float(response )
    
    #(Vmin-Vbase)/ Vamp before the waveform falling transition
    def getFPRE(self):
        response =  self.query(f"{self.name}:PAVA? FPRE")
        return float(response)
    
    #root mean square
    def getRMS(self):
        """Gets the RMS value of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self.name}:PAVA? RMS")
        return splitAndStripV(response)
    
    #maximum
    def getMax(self):
        """Gets the max. value of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self.name}:PAVA? MAX")
        return splitAndStripV(response)
    
    #risetime
    def getRise(self):
        """Gets the rise time (10%-90%?) of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self.name}:PAVA? RISE")
        return float( response)
    
    #minimum
    def getMin(self):
        """Gets the min. value of the waveform of this channel, by using a SDS built-in function."""
        response =self.query(f"{self.name}:PAVA? MIN")
        return splitAndStripV(response)
    
    #top
    def getTop(self):
        """Gets the location of the top of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self.name}:PAVA? TOP")
        return splitAndStripV(response)
    
    #mean
    def getMean(self):
        """Gets the mean of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self.name}:PAVA? MEAN")
        return splitAndStripV(response)
    
    #width
    def getWidth(self):
        """Gets the width of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self.name}:PAVA? WID")
        return float(response )
    
    #Gets the measured parameter 'amplitude'
    #example response: 'C1:PAVA AMPL,3.20E-01V\n'
    def getAmplitude(self):
        """Gets the amplitude of the waveform of this channel, by using a SDS built-in function."""
        response =self.query(f"{self.name}:PAVA? AMPL")
        return splitAndStripV(response)
        
    def getPKPK(self):
        """Gets the peak-to-peak value of the waveform of this channel, by using a SDS built-in function."""
        response =self.query(f"{self.name}:PAVA? PKPK")
        return splitAndStripV(response)
        
    def getFrequency(self):
        """Gets the frequency of the waveform of this channel, by using a SDS built-in function."""
        response = self.query(f"{self.name}:PAVA? FREQ")
        return splitAndStripHz(response)
    
    def getPhaseTo(self, input: 'SDS2kChannel'): 
        """Gets the phase between this channel and the input. The phase will be
        calculated according the fomulae: self.phase - input.phase.
        Remark: the input parameter has been written as 'SDSChannel' and not
        SDSChannel (without the qoutes). Reason: the inability of Python to use the type definition
        SDSChannel as a formal parameter of a method, before its definition. A class is known after
        finalizing its description.  
        As described in PEP484, expressing an unresolved name as a string literator is the way to go, 
        in order to resolve the name later.
        """
        return self.visaInstr.query(f"MEAD PHA,{self.name}-{input.name}")    
  

class SDSWaveFormPreamble(BaseWaveFormPreample):
    """Class for holding the SIGLENT SDS1000 scope series preamble. Extends BaseWaveFormPreamble.
    A preample is data describing the unit, range and spacing of a Waveform."""

    @classmethod
    def getWaveFormPreambleClass(cls, dev):
        """ Tries to get (instantiate) the right instance based on the type"""
        if cls is SDSWaveFormPreamble:
            return cls(dev)
        else:
            return None      
    
    def __init__(self, visaInstruments):
        """SDSWaveFormPreamble init. Inits all datamembers to the value None.
        Following data members are set:
        TBD """
        super().__init__(visaInstruments)
        self.descriptor             = None  #What is this. Check..

        self.nomBits                = None  #Measure of the intrinsic precision of the observation: ADC data is 8 bit, 
                                            #when averaged it is 10-12 bit, etc. TODO: implement 
        self.trigDelay              = None  #HORIZ_OFFSET: trigger offset, seconds between the trigger and the first data point
                                            #TODO: check if is same as sample interval.
        self.firstValidPoint        = None  #FIRST_VALID_PNT count of number of points to skip before first good point
                                            #FIRST_VALID_POINT = 0 for normal waveforms.
        self.lastValidPoint         = None  #Index of last good data point in record before padding (blanking) was started. 
                                            #LAST_VALID_POINT = WAVE_ARRAY_COUNT-1, except for aborted sequence and rollmode 
                                            #acquisitions
        #The definition of subsequent parameter is somewhat vague: it should be the same as the SN param of the WFSU command, but the
        #programming manual does not mentions such a param. Probably the NP param is referred.
        
        self.wfsu_fp                = None
        self.wfsu_sp                = None
        self.wfsu_si                = None #SEGMENT_INDEX: see SI of WFSU command in programming manual
        
        
        self.subArrayCount          = None #For sequences acquisitions
        self.nrOfSweepsPerAcq       = None
        self.pairPoints             = None
        self.pairOffset             = None
        self.pixelOffset            = None #PIXEL_OFFSET: needed to know how to display the waveform
        self.horUncertainty         = None #uncertainty from one acquisition to the  next, of the horizontal offset in seconds
        self.trigTimeStamp          = None #TRIGGER_TIME: time of the trigger
        
        self.vertCouplingstr        = None #self._vertCoupling = None
        self.ymult                  = None #self._vertGain = None
        self.vertVernier            = None
        self.acqVertOffs            = None # geen idee wat dit is.
        self.waveSource             = None
        self.instrumentName         = None
        self.instrumentNr           = None
        # TODO: horiGridSize is not part of the SDS preamble, its more like a constant belowing to
        # this scope series. Therefore, it should be a configurable parameter (e.g. in an ini file)
        # Grid size is the same as div. See also the programming manual, page 142/143, gridsize = 14 .
        #self.horiGridSize           = 14
        # TODO: just like a horizontal grid size, an oscilloscope has also a vertical grid, which  
        # is the same as 'vertical divs'. The SDS scope series apparently has two vertigal grids:
        # a physical range of 10 divs and a visible range of 8 divs.  
        #self.vertGridsize           = 10
        #self.visVertGridSize        = 8
        
    def decodePreambleStr(self, params):
        self.descriptor = struct.unpack("16s", params[0:16])[0]
        # see programming manual: first 8 chars should bij WAVEDESC
        if self.descriptor[0:8] != b'WAVEDESC':
            print("ERROR: Siglent SDS wrong discriptor at capture!")
        self.instrumentName = struct.unpack("16s", params[76:92])[0] #string type parameter.
        self.instrumentNr = struct.unpack("L", params[92:96])[0] #long int type parameter.
        temp = struct.unpack('4c', params[96:100])[0] #string type parameter.
        trace_label = str(temp)
        self.nrOfSamples = struct.unpack('i', params[116:120])[0]
        self.wfsu_sp = struct.unpack('i', params[136:140])[0]
        self.wfsu_fp = struct.unpack('i', params[140:144])[0]
        self.wfsu_si = struct.unpack('i', params[144:148])[0]
        
        
        self.probeAtt = struct.unpack('f', params[328:332])[0]
        sweeps_per_acq = struct.unpack('L', params[148:152])[0] #for Long sized parameter, use 'L'
        #self.pairPoints=struct.unpack('x', params[152:154])[0] #Word= kind of parameter, use 'x' for hex decoding?
        #self.pairOffset=struct.unpack('x', params[154:156])[0] #Word= kind of parameter, use 'x' for hex decoding?
        self.vdiv = struct.unpack('f', params[156:160])[0] * self.probeAtt
        
        self.yoff = struct.unpack('f', params[160:164])[0] * self.probeAtt
        self.maxGridVal = struct.unpack('f', params[164:168])[0] * self.probeAtt
        self.minGridVal = struct.unpack('f', params[168:172])[0] * self.probeAtt
        #nom_bits: an intrinsic measure of precision. Raw data is 8 bits, but averaging increases number of bits.
        self.nomBits = struct.unpack('H', params[172:174])[0]  # for Word sized parameter, use 'H'
        self.xincr = struct.unpack( 'f', params[176:180])[0]
        self.trigDelay = struct.unpack('d', params[180:188])[0]  # Equals HORIZ_OFFSET
        self.pixelOffset = struct.unpack('d', params[188:196])[0]  #
        self.yUnitStr = str(struct.unpack('48s', params[196:244])[0])  # vertaling naar string lijkt niet ok.
        self.xUnitStr = str(struct.unpack('48s', params[244:292])[0])
        self.horUncertainty =  struct.unpack( 'f', params[292:296])[0]
        # 
        #time_stamp         double precision floating point number,
        #         0          for the number of seconds and some bytes
        #                   for minutes, hours, days, months and year.
        #                   double  seconds     (0 to 59)
        #                   byte    minutes     (0 to 59)
        #                   byte    hours       (0 to 23)
        #                   byte    days        (1 to 31)
        #                   byte    months      (1 to 12)
        #                   word    year        (0 to 16000)
        #                   word    unused
        self.recordType = struct.unpack('H', params[316:318])[0]  # enum, 2 bytes use 'H' for now. need check!
        self.processingDone = struct.unpack('H', params[318:320])[0]  # enum, 2 bytes use 'H' for now. need check!

        #### timebase its a enum, need to convert first
        timebase_enum = struct.unpack('h', params[324:326])[0]
        self.timeDiv = float(TIMEBASE_HASHMAP.get(str(timebase_enum)))
        #TODO: if hashmap doesn't  contain requested key:
        #   It's an error, but probably not a  showstopper, because script is not fit
        #   for the current connected sds, or scope is not a siglent.
        #   FIX: a. create a error class/enum with corresponding exception or combination of the two and
        #   need to classify the error based on more or better information
        #   For now: just print an error message and keep on!
        if self.timeDiv == None:
            self._logger.error("ERROR TIMEBASE CONVERT: UNKNOWN KEY!\n")
        #### end timebase convert

        self.vertCouplingstr = struct.unpack('H', params[326:328])[0] # enum, 2 bytes use 'H' for now. need check!
        self.vertGain = struct.unpack('H', params[332:334])[0]
        self.bwLimit = struct.unpack('H', params[334:336])[0] #enum, 2 bytes use 'H' for now. need check!
        self.vertVernier = struct.unpack('f', params[336:340])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        #self.acqVertOffs = struct.unpack('f', params[340:344])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        self.waveSource = struct.unpack('H', params[344:346])[0] # enum, 2 bytes use 'H' for now. need check!
        #TODO: if the object WFP really is the WaveForm object for this channel, then all values have now been set. THIS MUST BE CHECKED.

    
    
class SDS2kWaveForm(BaseWaveForm):

    def setInstr(self, visaInstr:pyvisa.resources.MessageBasedResource):
        self.visaInstr = visaInstr

    def setChanId(self, theChanId):
        self.myChanId = theChanId


    @classmethod
    def getWaveFormClass(cls):
        """ Tries to get (instantiate) the device, based on the url"""
        if cls is SDS2kWaveForm:
            return cls
        else:
            return None      
        
    def __init__(self):
        super().__init__()
        self.visaInstr: pyvisa.resources.MessageBasedResource = None  #Added 11-1-2026, to beter reflect SDS2k waveform commands. 
        self.myChanId = None
        ####BELOW HAS TO BE CONVERTED TO SIGLENT. THIS IS TEKTRONIX TDS SPECIFIC WAVEFORM PARAMS ########
        self.rawYdata       = None #data without any conversion or scaling taken from scope
        self.rawXdata       = None #just an integer array
        self.scaledYdata    = None #data converted to correct scale e.g untis
        self.scaledXdata    = None #An integer array representing the fysical instants of the scaledYData.
        
        self.nrOfDivs = 5 # TODO: set this value during initialisation of the scope.
        self.full_code = 256 # TODO: set this value during initialisation of the scope.
        self.center_code = 127 # TODO: set this value during initialisation of the scope.
        self.max_code = self.full_code/2
        self.hori_grid_size = 14 # TODO: See programming manual, pag 142/143 gridsize = 14.        
        
    def rawYToVolts(self, vdiv, voffset):
        """Method to convert the raw bytevalue returned from the scope to its fysical equivalent.
        One has to have the SDS limitions in mind, in order to calculate this value correctly:
                - screen of scope consists of 10 'divs', although the fysical scope only shows 8 
                divisions. In other words: samples will always be represented in a range of 5 'divs'. 
                - The (vertical) resolution of the SDS1202X-E is 8 bits
                - The samples are coded as unsigned bytes: 0..255 decimal
                - Therefor, the center of the screen corresponds to 127 (decimal), if no vertical offset.
                    The center is represented by: self.center_code)
                - The formula to convert a raw unsigned byte value into a signed potential value is
                y_volts = (y_raw * 5/128)-voffset or y_volts = (y_raw * vdiv/25)-voffset TODO: check latter.               
        """ 
        y = self.rawYdata
        #np.where(y > self.center_code , y, y - self.full_code)

        voltfactor = vdiv/25.0
        tempVolt = np.multiply(y,voltfactor)
        res = np.subtract(tempVolt, voffset)
        self.scaledYdata = res

        return res
    
    def rawXtoTime(self, horOffset, sampleInterval, tdiv, nrOfPoints):
        """Method for converting the raw sample numbers, or the indices of the samples, to an array with sample time 
        instances. The formulae to calculate the time instances, see SDS programming manual on page 142/143, is:
        timeVal = trdl-( timebase*grid/2), where:
            trdl : Trigger delay, or horizontal offset.
            timebase : tdiv, or time per division (horizontally)
            grid: the number of division of the fysical scope screen, for SDS this is 14 divisions.
        This method sets the scaleXdata member of this SDS2kWaveForm object and also returns array with time values. 
        """

        FirstSampleTime = horOffset -tdiv*(self.hori_grid_size/2)
        lastSampleTime = FirstSampleTime + nrOfPoints*sampleInterval
        timeArr = np.arange(FirstSampleTime,lastSampleTime,sampleInterval)
        self.scaledXdata = timeArr
        
        return timeArr

    ############################ SIGLENT SDS2K SPECIFIC WAVEFORM COMMANDS ##########################################
    """According to the Siglent Programming guide for SDS2000 series (document EN11D) a SDS2k scope
    has the following WaveForm commands 
    :WAVeform:DATA          query only (implemented)
    :WAVeform:INTerval      command/query (both implemented)
    :WAVeform:MAXPoint      query only (implemented)
    :WAVeform:POINt         command/query (both implemented)
    :WAVeform:PREamble      query only (implemented)
    :WAVeform:SEQuence      command/query (both implemented)
    :WAVeform:SOURce        command/query (both implemented)
    :WAVeform:STARt         command/query (both implemented)
    :WAVeform:WIDTh         command/query (both implemented)
    For now, all these commands will be located in this class and used where needed.
    """    
    def getWVFData(self):
        """Method for transferring waveform data from oscilloscope. This method transfers the data of the source
        set by WAVeform:SOURce. """
        #TODO: check of deze functie goed omgaat met WORD breedte (dus 2 i.p.v. 1 byte)
        self.rawYdata = self.visaInstr.query_binary_values(f"{SCPI["WAVEFORM"]["data?"]()}", datatype='B', is_big_endian=False, container=np.ndarray)

    def setSource(self, newSrc):
        #TODO: checken geldigheid newSrc, moet C, F of D zijn.
        self.visaInstr.write(SCPI["WAVEFORM"]["source"](newSrc))
    
    def getSource(self):
        return self.visaInstr.query(SCPI["WAVEFORM"]["source?"]())

    def setStart(self, index):
        #TODO: checken of index een int is.
        self.visaInstr.write(SCPI["WAVEFORM"]["start"](index))
    
    def getStart(self):
        return self.visaInstr.query(SCPI["WAVEFORM"]["start?"]())

    def setInterval(self, intVal):
        #TODO: checken of intval een int is.
        self.visaInstr.write(SCPI["WAVEFORM"]["interval"](intVal))

    def getInterval(self):
        return self.visaInstr.query(SCPI["WAVEFORM"]["interval?"]())  


    def setNrOfPts(self, nrOfPts):
        #TODO: checken of nrOfPts een int is.
        self.visaInstr.write(SCPI["WAVEFORM"]["points"](nrOfPts))

    def getNrOfPts(self):
        return self.visaInstr.query(SCPI["WAVEFORM"]["points?"]())  

    def getMaxNrOfPts(self):
        return self.visaInstr.query(SCPI["WAVEFORM"]["maxpoints?"]())
    
    def getPreamble(self):
        #TODO: fix the decode of preamble
        return self.visaInstr.query(SCPI["WAVEFORM"]["preamble?"]())
    
    def getDataWidth(self):
        """Method for querying the number of bytes during transfer.
        Return: the number of bytes used per sample. Valid values are 1 or 2. 0 means error.
        """
        resp = self.visaInstr.query(SCPI["WAVEFORM"]["width?"]())
        if resp == "BYTE":
            return 1
        elif resp == "WORD":
            return 2
        else:
            return 0
    
    def setDataWidth(self, val):
        if val == 1:
            self.visaInstr.write(SCPI["WAVEFORM"]["width"]("BYTE"))
        elif val == 2:
            self.visaInstr.write(SCPI["WAVEFORM"]["width"]("WORD"))
        else:
            self.visaInstr.write(SCPI["WAVEFORM"]["width"]("BYTE"))

    def setSequence(self, val1 = 0, val2 = 0):
        #TODO: dit commando goed uitzoeken. Is een beetje lastig.
        self.visaInstr.write(SCPI["WAVEFORM"]["sequence"](val1)(val2))

    def getSequence(self):
        return self.visaInstr.query(SCPI["WAVEFORM"]["sequence?"]())



        
