import time
import vxi11
import struct
import numpy as np
from enum import Enum
import socket
import pyvisa as visa
import logging
import time
import xdrlib
from devices.siglent.sds.util import splitAndStripHz, splitAndStripSec, splitAndStripV 
from devices.siglent.sds.util import WaveFormPreamble
from devices.siglent.sds.util import WaveFormTrace
from devices.siglent.sds.util import TIMEBASE_HASHMAP
import pickle

# SDSChannel: abstraction of a Siglent oscilloscope channel.
# Usage: set or get 'vertical' channel properties of a scope and/or start a capture.
# Assumption: all channels of a scope model a equivalent.
# Getting vertical div, vertical offset,

class SDSChannel(object):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    center_code = 127


    def __init__(self, chan_no: int, dev, logger):
        self._name = f"C{chan_no}"
        self._logger = logger
        self._dev = dev
        self._WVT = WaveFormTrace()
        self._nrOfDivs = 5 # TODO: should be set during initialisation of the scope.
        self.full_code = 256 # TODO: should be set during initialisation of the scope.
        self.center_code = 127 # TODO: should be set during initialisation of the scope.
        self.max_code = self.full_code/2
        self._hori_grid_size = 14 # TODO: is this a fixed number for Siglent? Check this.
        
            
    def calculate_voltage(self, x, vdiv, voffset, code_per_div):
        if x > self.center_code:
            x -= self.full_code
        #FS=10 hokjes=top-top
        #0->1.0 = 127 stapjes
        #0->1.0 = 5 hokjes

        """
            Calculation of voltage value, as shown on scope, can only be performed if one has the limitations
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
        return (x*self._nrOfDivs*vdiv/self.max_code) -voffset

    def sampNr2TimeVect(self, hdiv, interval):
        pass
    def convert_to_voltage(self, raw_array) -> np.ndarray:
        # Get the parameters of the source
        total_points, vdiv, voffset, code_per_div, timebase, delay, interval = self.get_waveform_preamble()
        vect_voltage = np.vectorize(self.calculate_voltage)

        return vect_voltage(raw_array, vdiv, voffset, code_per_div)

    def setIimeBase(self, value):
        """The query returns the parameters of the source using by the command
        :WAVeform:SOURce.
        See text output from a Siglent scope for reference. See Repo.
        """
        self._dev._inst.write(f"Time_DIV {value}")
        
    def setTimeDiv(self, value):
        self.setIimeBase(value)

    def setVoltDiv(self, value):
        """The query returns the parameters of the source using by the command
        :WAVeform:SOURce.
        See text output from a Siglent scope for reference. See Repo.
        <channel>: Volt_DIV <v_gain>
        """
        self._dev._inst.write(f"{self._name}:VOLT_DIV {value}")


    def get_waveform_preamble(self):
        """The query returns the parameters of the source using by the command
        :WAVeform:SOURce.
        See text output from a Siglent scope for reference. See Repo.
        """
        WFP = self._WVT.getWVP()
        params = self._dev._inst.query_binary_values("C1:WaveForm? DESC", datatype='B', container=np.ndarray)
        instrument_name = struct.unpack("16s", params[76:92])[0] #string type parameter.
        instrument_number = struct.unpack("L", params[92:96])[0] #long int type parameter.
        temp = struct.unpack('4c', params[96:100])[0] #string type parameter.
        trace_label = str(temp)
        WFP._total_points = struct.unpack('i', params[116:120])[0]
        
        probe = struct.unpack('f', params[328:332])[0]
        sweeps_per_acq = struct.unpack('L', params[148:152])[0] #for Long sized parameter, use 'L'
        #points_per_pair=struct.unpack('x', params[152:154])[0] #Word= kind of parameter, use 'x' for hex decoding?
        #pair_offset=struct.unpack('x', params[154:156])[0] #Word= kind of parameter, use 'x' for hex decoding?
        WFP._vdiv = struct.unpack('f', params[156:160])[0] * probe
        
        WFP._voffset = struct.unpack('f', params[160:164])[0] * probe
        WFP._maxGridVal = struct.unpack('f', params[164:168])[0] * probe
        WFP._minGridVal = struct.unpack('f', params[168:172])[0] * probe
        #nom_bits: an intrinsic measure of precision. Raw data is 8 bits, but averaging increases number of bits.
        WFP._nrOfADCBits = struct.unpack('H', params[172:174])[0]  # for Word sized parameter, use 'H'
        WFP._sampInterval = struct.unpack( 'f', params[176:180])[0]
        WFP._delay = struct.unpack('d', params[180:188])[0]
        WFP._pixelOffset = struct.unpack('d', params[188:196])[0]  #
        WFP._vertUnit = str(struct.unpack('48s', params[196:244])[0])  # vertaling naar string lijkt niet ok.
        WFP._horUnit = str(struct.unpack('48s', params[244:292])[0])
        # trigger_time=struct.unpack('time', params[296:312])[0] #time parameter? how to decode?
        WFP._recordType = struct.unpack('H', params[316:318])[0]  # enum, 2 bytes use 'H' for now. need check!
        WFP._processingDone = struct.unpack('H', params[318:320])[0]  # enum, 2 bytes use 'H' for now. need check!

        #### timebase is a enum, need to convert first
        timebase_enum = struct.unpack('h', params[324:326])[0]
        WFP._timebase = float(TIMEBASE_HASHMAP.get(str(timebase_enum)))
        #TODO: if hashmap doesn't  contain requested key:
        #   It's an error, but probably not a  showstopper, because script is not fit
        #   for the current connected sds, or scope is not a siglent.
        #   FIX: a. create a error class/enum with corresponding exception or combination of the two and
        #   need to classify the error based on more or better information
        #   For now: just print an error message and keep on!
        if WFP._timebase == None:
            self._logger.error("ERROR TIMEBASE CONVERT: UNKNOWN KEY!\n")
        #### end timebase convert

        WFP._vertCoupling = struct.unpack('H', params[326:328])[0] # enum, 2 bytes use 'H' for now. need check!
        WFP._vertGain = struct.unpack('H', params[332:334])[0]
        WFP._bwLimit = struct.unpack('H', params[334:336])[0] #enum, 2 bytes use 'H' for now. need check!
        # vert_vernier=struct.unpack('f', params[336:340])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        # acq_vert_offset=struct.unpack('f', params[340:344])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        WFP._waveSource=struct.unpack('H', params[344:346])[0] # enum, 2 bytes use 'H' for now. need check!

        
    def get_trigger_status(self):
        """The command query returns the current state of the trigger.

        :return: str
                    Returns either "Arm", "Ready", "Auto", "Trig'd", "Stop", "Roll"
        """
        return self._dev.query(":TRIGger:STATus?")

    def capture(self):
        
        #self._dev.write(":WAVeform:SOURce {}".format(self._name))
        #self._dev.write('WFSU SP,4,NP,0,FP,0')
        #self._dev.write('WFSU SP,1,NP,0,FP,0')
        #data = self._dev.query_raw(":WAVeform:DATA?")
        #data = self._dev.query_raw('C1:WF? DAT2')
        #data = data[11:-2]  # eliminate header and remove last two bytes
        #datatype param: see https://docs.python.org/3/library/struct.html#format-characters. 'B' means unsigned char
  
        data = self._dev._inst.query_binary_values(f"{self._name}:WF? DAT2", datatype='B', is_big_endian=False, container=np.ndarray)
        try:
            trace = np.frombuffer(data, dtype=np.byte)
            self._WVT.setTrace(self.convert_to_voltage(trace))
            #self._last_trace = data
        except Exception as e:
            self._logger.error(e)

        return trace

    def getMaxOfTrace(self):
        return max(self._WVT.getTraceData())

    def getTRDL(self):
        #need to check diff between this en hori 
        delay_str = self._dev._inst.query("TRig_DeLay?") #according to pyvisa API: query returns str
        delay_str = delay_str.strip("S\n") #Need to combine 'S' with the '\n'. Only strip('S'), doesnot work.
        delay_str = delay_str.strip("TRDL")
        delay_str = delay_str.strip() #remove leading zero
        return float(delay_str) #return a float

    def getVdiv(self):
        VDIV = self._dev.query(f"{self._name}:VDIV?")
        return VDIV

    def getVofs(self):
        VOFS = self._dev.query(f"{self._name}:OFST?")
        return VOFS

    def getVcenterTV(self):
        CENTERTV = self._dev.query('TRDL?')
        return CENTERTV

    def getTimeBase(self):
        TB = self._dev.query('TDIV?')
        return TB
    
    def getTimeAxisRange(self):
        #See programming manual sds, page 142:
        #first point = delay - (timebase*(hori_grid_size/2))
        
        mydelay = self._WVT._WVP._delay
        mytimebase = self._WVT._WVP._timebase
        timeOfFirstSample = mydelay - (mytimebase*(self._hori_grid_size/2))
        self._WVT._WVP._timeOfFirstValidSample = timeOfFirstSample
        self._WVT._WVP._timeOfLastValidSample = timeOfFirstSample +(self._WVT._WVP._sampInterval * self._WVT._WVP._total_points)
        return (self._WVT._WVP._timeOfFirstValidSample,  self._WVT._WVP._timeOfLastValidSample)

    def timebase_scale(self) -> float:
        """The query returns the current horizontal scale setting in seconds per
        division for the main window.

        :return: float

        """
        return float(self._dev._inst.query_binary_values(":TIMebase:SCALe?"))
    
    ########## PARAMETER MEASUREMENTS (PAVA) ###########
    
    def getAllParam(self):
        return self._dev._inst.query(f"{self._name}:PAVA? ALL")

    def getBase(self):
        return float( self._dev._inst.query(f"{self._name}:PAVA? BASE"))
    
    def getNDuty(self):
        return float( self._dev._inst.query(f"{self._name}:PAVA? NDUTY"))
    
    #negative width
    def getNWid(self):
        return float( self._dev._inst.query(f"{self._name}:PAVA? NWID"))
    
    #negative overshoot
    def getOvSN(self):
        return float( self._dev._inst.query(f"{self._name}:PAVA? OVSN"))
    
    #mean for cyclic waveform
    def getCMean(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? CMEAN")
        return splitAndStripV(response)
    
    #positive overshoot
    def getOvSP(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? OVSP")
        return float( )
    
    #root mean square for cyclic part of waveform
    def getCMean(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? CRMS")
        return splitAndStripV(response)
     
    #duty cycle
    def getDuty(self):
        response =self._dev._inst.query(f"{self._name}:PAVA? DUTY")
        return float( )
    
    #period
    def getPeriod(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? PER")
        return splitAndStripSec(response)

    #falltime
    def getFall(self):
        response =self._dev._inst.query(f"{self._name}:PAVA? FALL")
        return splitAndStripSec(response)
    
    #(Vmin-Vbase)/ Vamp before the waveform rising transition
    def getRPRE(self):
        response =self._dev._inst.query(f"{self._name}:PAVA? RPRE")
        return float(response )
    
    #positive width
    def getPwidth(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? PWID")
        return float(response )
    
    #(Vmin-Vbase)/ Vamp before the waveform falling transition
    def getFPRE(self):
        response =  self._dev._inst.query(f"{self._name}:PAVA? FPRE")
        return float(response)
    
    #root mean square
    def getRMS(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? RMS")
        return splitAndStripV(response)
    
    #maximum
    def getMax(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? MAX")
        return splitAndStripV(response)
    
    #risetime
    def getRise(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? RISE")
        return float( response)
    
    #minimum
    def getMin(self):
        response =self._dev._inst.query(f"{self._name}:PAVA? MIN")
        return splitAndStripV(response)
    
    #top
    def getTop(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? TOP")
        return splitAndStripV(response)
    
    #mean
    def getMean(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? MEAN")
        return splitAndStripV(response)
    
    #width
    def getWidth(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? WID")
        return float(response )
    
    #Gets the measured parameter 'amplitude'
    #example response: 'C1:PAVA AMPL,3.20E-01V\n'
    def getAmplitude(self):
        response =self._dev._inst.query(f"{self._name}:PAVA? AMPL")
        return splitAndStripV(response)
        
    def getPKPK(self):
        response =self._dev._inst.query(f"{self._name}:PAVA? PKPK")
        return splitAndStripV(response)
        
    def getFrequency(self):
        response = self._dev._inst.query(f"{self._name}:PAVA? FREQ")
        return splitAndStripHz(response)
    
    def saveTrace(self, filename):
        #saves the trace of this channel object, or performs a capture and 
        #saves the trace.
        if self._last_trace == None:
            # get a trace
            self.get_waveform_preamble()
            self.capture()
            #TODO: actualsave.
        else:
            #dump the WVP and trace data 
            #see: https://docs.python-guide.org/scenarios/serialization/ use Pickle
            pkl_wvp_file = f"{filename}_pkl_wvp.dat"
            pkl_file = open('data.pkl', 'rb')
            pickle.dump(self._WFP, pkl_file)
                        
        
class SiglentSDSTriggerStatus(Enum):
    ARM = "Arm"
    READY = "Ready"
    AUTO = "Auto"
    TRIGD = "Trig'd"
    STOP = "Stop"
    ROLL = "Roll"

class SiglentWaveformWidth(Enum):
    BYTE = "BYTE"
    WORD = "WORD"
