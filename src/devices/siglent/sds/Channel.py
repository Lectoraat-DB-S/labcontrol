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
import pickle

# SDSChannel: abstraction of a Siglent oscilloscope channel.
# Usage: set or get 'vertical' channel properties of a scope and/or start a capture.
# Assumption: all channels of a scope model a equivalent.
# Getting vertical div, vertical offset,


from devices.BaseScope import BaseChannel, BaseWaveForm, BaseWaveFormPreample

class SDSChannel(BaseChannel):
    #IMMEDMEASTYPES =["CRMs","CURSORRms","DELay","FALL",
    #                    "FREQuency","MAXImum","MEAN","MINImum","NONe","NWIdth","PDUty","PERIod","PHAse", 
    #                    "PK2pk","PWIdth","RISe"]
    
    @classmethod
    def getChannelClass(cls, chan_no, dev):
        """ Tries to get (instantiate) the device, based on the url"""
        if cls is SDSChannel:
            return cls
        else:
            return None      
    
    def __init__(self, chan_no: int, visaInstr:pyvisa.resources.MessageBasedResource):
        super().__init__(chan_no, visaInstr)
        self.name = f"C{chan_no}"
        self.visaInstr: pyvisa.resources.MessageBasedResource = visaInstr
        self.WFP= SDSWaveFormPreamble(visaInstr)
        self.WF = SDSWaveForm()

    def query(self, cmd: str):
        return self.visaInstr.query(cmd)
    
    def write(self, cmd: str):
        self.visaInstr.write(cmd)

    def getVdiv(self):
        VDIV = self.query(f"{self._name}:VDIV?")
        return VDIV

    def getVofs(self):
        VOFS = self.query(f"{self._name}:OFST?")
        return VOFS
    
    def getWaveformPreamble(self):
        """The query returns the parameters of the source using by the command
        :WAVeform:SOURce.
        See text output from a Siglent scope for reference. See Repo.
        """
        wvpRespStr = self.visaInstr.query_binary_values(f"{self.name}:WaveForm? DESC", datatype='B', container=np.ndarray)
        self.WFP.decodePreambleStr(params=wvpRespStr)
        
    def capture(self):
        
        self.getWaveformPreamble() #for quering the preamble, in order to have fresh WVP
        
        data = self.visaInstr.query_binary_values(f"{self._name}:WF? DAT2", datatype='B', is_big_endian=False, container=np.ndarray)
        try:
            
            trace = np.frombuffer(data, dtype=np.byte)
            self._WVT.setRawTrace(trace)
            self.WF.convertRaw_to_voltage()
        except Exception as e:
            self._logger.error(e)
    
    def getTimeAxis(self):
        horOffset = self.WVP.trigDelay
        sampleInterval = self.WVP.xincr
        tdiv = self._WVT._WVP.timeDiv
        nrOfPoints = self.WVP.nrOfSamples
        FirstSampleTime = horOffset -tdiv*(14/2)
        lastSampleTime = FirstSampleTime + nrOfPoints*sampleInterval
        timeArr = np.arange(FirstSampleTime,lastSampleTime,sampleInterval)
        
        return timeArr
    
    def getTimeAxisRange(self):
        #See programming manual sds, page 142:
        #first point = delay - (timebase*(hori_grid_size/2))
        
        mydelay = self._WVT._WVP._delay
        mytimebase = self.WVP.timeDiv
        timeOfFirstSample = mydelay - (mytimebase*(self._hori_grid_size/2))
        self.WVP.lastValidSample = timeOfFirstSample +(self.WVP.xincr * self.WVP.nrOfSamples)
        return (self.WVP.firstValidSample,  self.WVP.lastValidSample)

    ########## PARAMETER MEASUREMENTS (PAVA) ###########
    
    def getAllParam(self):
        return self.query(f"{self.name}:PAVA? ALL")

    def getBase(self):
        return float( self.query(f"{self.name}:PAVA? BASE"))
    
    def getNDuty(self):
        return float( self.query(f"{self.name}:PAVA? NDUTY"))
    
    #negative width
    def getNWid(self):
        return float( self.query(f"{self.name}:PAVA? NWID"))
    
    #negative overshoot
    def getOvSN(self):
        return float( self.query(f"{self.name}:PAVA? OVSN"))
    
    #mean for cyclic waveform
    def getCMean(self):
        response = self.query(f"{self.name}:PAVA? CMEAN")
        return splitAndStripV(response)
    
    #positive overshoot
    def getOvSP(self):
        response = self.query(f"{self._name}:PAVA? OVSP")
        return float(response)
    
    #root mean square for cyclic part of waveform
    def getCMean(self):
        response = self.query(f"{self._name}:PAVA? CRMS")
        return splitAndStripV(response)
     
    #duty cycle
    def getDuty(self):
        response =self.query(f"{self._name}:PAVA? DUTY")
        return float( )
    
    #period
    def getPeriod(self):
        response = self.query(f"{self._name}:PAVA? PER")
        return splitAndStripSec(response)

    #falltime
    def getFall(self):
        response =self.query(f"{self._name}:PAVA? FALL")
        return splitAndStripSec(response)
    
    #(Vmin-Vbase)/ Vamp before the waveform rising transition
    def getRPRE(self):
        response =self.query(f"{self._name}:PAVA? RPRE")
        return float(response )
    
    #positive width
    def getPwidth(self):
        response = self.query(f"{self._name}:PAVA? PWID")
        return float(response )
    
    #(Vmin-Vbase)/ Vamp before the waveform falling transition
    def getFPRE(self):
        response =  self.query(f"{self._name}:PAVA? FPRE")
        return float(response)
    
    #root mean square
    def getRMS(self):
        response = self.query(f"{self._name}:PAVA? RMS")
        return splitAndStripV(response)
    
    #maximum
    def getMax(self):
        response = self.query(f"{self._name}:PAVA? MAX")
        return splitAndStripV(response)
    
    #risetime
    def getRise(self):
        response = self.query(f"{self._name}:PAVA? RISE")
        return float( response)
    
    #minimum
    def getMin(self):
        response =self.query(f"{self._name}:PAVA? MIN")
        return splitAndStripV(response)
    
    #top
    def getTop(self):
        response = self.query(f"{self._name}:PAVA? TOP")
        return splitAndStripV(response)
    
    #mean
    def getMean(self):
        response = self.query(f"{self._name}:PAVA? MEAN")
        return splitAndStripV(response)
    
    #width
    def getWidth(self):
        response = self.query(f"{self._name}:PAVA? WID")
        return float(response )
    
    #Gets the measured parameter 'amplitude'
    #example response: 'C1:PAVA AMPL,3.20E-01V\n'
    def getAmplitude(self):
        response =self.query(f"{self._name}:PAVA? AMPL")
        return splitAndStripV(response)
        
    def getPKPK(self):
        response =self.query(f"{self._name}:PAVA? PKPK")
        return splitAndStripV(response)
        
    def getFrequency(self):
        response = self.query(f"{self._name}:PAVA? FREQ")
        return splitAndStripHz(response)
  

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
        self.nrOfSamples            = None  #Number of points of (last) acquired waveform
        self.vdiv                   = None  #Number of units (e.g. V) per division 
        self.yoff                   = None  #Vertical offset. Calc floating values from raw data : VERTICAL_GAIN * data - VERTICAL_OFFSET
        self.maxGridVal             = None  #Maximum allowed value. It corresponds to the upper edge of the grid.
        self.minGridVal             = None  #Minimum allowed value. It corresponds to the lower edge of the grid.
        self.nomBits                = None  #Measure of the intrinsic precision of the observation: ADC data is 8 bit, 
                                            #when averaged it is 10-12 bit, etc. TODO: implement 
        self.timeDiv                = None  #TDIV: the amount of time per division. SEE TIMEBASE_HASHMAP.
        self.trigDelay              = None  #HORIZ_OFFSET: trigger offset, seconds between the trigger and the first data point
        self.xincr                  = None  #HORIZ_INTERVAL: float sampling interval for time domain waveforms. 
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
        self.yUnitStr               = None #VERTUNIT: units of the vertical axis

        self.xUnitStr               = None #HORUNIT: units of the horizontal axis
        self.horUncertainty         = None #uncertainty from one acquisition to the  next, of the horizontal offset in seconds
        self.trigTimeStamp          = None #TRIGGER_TIME: time of the trigger
        
        self.recordType             = None
        self.processingDone         = None
        self.vertCouplingstr        = None #self._vertCoupling = None
        self.ymult                  = None #self._vertGain = None
        self.bwLimit                = None
        self.vertVernier            = None
        self.acqVertOffs            = None # geen idee wat dit is.
        self.waveSource             = None
       
    def decodePreambleStr(self, params):
        instrument_name = struct.unpack("16s", params[76:92])[0] #string type parameter.
        instrument_number = struct.unpack("L", params[92:96])[0] #long int type parameter.
        temp = struct.unpack('4c', params[96:100])[0] #string type parameter.
        trace_label = str(temp)
        self.nrOfSamples = struct.unpack('i', params[116:120])[0]
        self.wfsu_sp = struct.unpack('i', params[136:140])[0]
        self.wfsu_fp = struct.unpack('i', params[140:144])[0]
        self.wfsu_si = struct.unpack('i', params[144:148])[0]
        
        
        probe = struct.unpack('f', params[328:332])[0]
        sweeps_per_acq = struct.unpack('L', params[148:152])[0] #for Long sized parameter, use 'L'
        self.pairPoints=struct.unpack('x', params[152:154])[0] #Word= kind of parameter, use 'x' for hex decoding?
        self.pairOffset=struct.unpack('x', params[154:156])[0] #Word= kind of parameter, use 'x' for hex decoding?
        self.vdiv = struct.unpack('f', params[156:160])[0] * probe
        
        self.yoff = struct.unpack('f', params[160:164])[0] * probe
        self.maxGridVal = struct.unpack('f', params[164:168])[0] * probe
        self.minGridVal = struct.unpack('f', params[168:172])[0] * probe
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
        #                   for the number of seconds and some bytes
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
        self.acqVertOffs = struct.unpack('f', params[340:344])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        self.waveSource = struct.unpack('H', params[344:346])[0] # enum, 2 bytes use 'H' for now. need check!
        #TODO: if the object WFP really is the WaveForm object for this channel, then all values have now been set. THIS MUST BE CHECKED.

    
    
class SDSWaveForm(BaseWaveForm):

    @classmethod
    def getWaveFormClass(cls):
        """ Tries to get (instantiate) the device, based on the url"""
        if cls is SDSWaveForm:
            return cls
        else:
            return None      
        
    def __init__(self):
        super().__init__()
        ####BELOW HAS TO BE CONVERTED TO SIGLENT. THIS IS TEKTRONIX TDS SPECIFIC WAVEFORM PARAMS ########
        self.rawYdata       = None #data without any conversion or scaling taken from scope
        self.rawXdata       = None #just an integer array
        self.scaledYdata    = None #data converted to correct scale e.g untis
        self.scaledXdata    = None #An integer array representing the fysical instants of the scaledYData.
        
        self.nrOfDivs = 5 # TODO: should be set during initialisation of the scope.
        self.full_code = 256 # TODO: should be set during initialisation of the scope.
        self.center_code = 127 # TODO: should be set during initialisation of the scope.
        self.max_code = self.full_code/2
        self.hori_grid_size = 14 # TODO: is this a fixed number for Siglent? Check this.
        
    def calculate_voltage(self):
        x = self.getRawTrace()
        fc =self.full_code
        #np.where(x>5, x, temp)
        np.where(x > self.center_code , x, x - self.full_code)
        #FS=10 hokjes=top-top
        #0->1.0 = 127 stapjes
        #0->1.0 = 5 hokjes

        """
            To Calculate the voltage value, as shown on scope, can only be performed if one has the limitations
            of the oscilloscope in mind:
                - screen of scope consists of 10 'divs', although the fysical scope only shows 8 of them. 
                    The samples therefore  always represents a range of 5 'divs'. 
                - The (vertical) resolution of the SDS1202X-E is 8 bits
                - The center of the screen equals to a decimal sample value of 127 (self.center_code),
                    assuming 0.0 Volt offset (voffset)
                - The samples are coded as unsigned bytes, so one have to restore the sign in the code.
                - The range of samples is therefore -128 .... + 127
            So xnew = (xold * 5/128)-voffset                
        """
        voltfactor = self._WVP._vdiv/25
        tempVolt = np.multiply(x,voltfactor)
        res = np.subtract(tempVolt, self._WVP._voffset)
        
        return res
    
    def convertRaw_to_voltage(self):
        # Get the parameters of the source
        raw_array = self.getRawTrace()
        vect_voltage = self.calculate_voltage()
        self.setTrace(vect_voltage)
            
