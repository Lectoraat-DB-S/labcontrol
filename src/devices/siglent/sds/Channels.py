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
from devices.siglent.sds.util import WaveFormPreamble
from devices.siglent.sds.util import TIMEBASE_HASHMAP

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


    def __init__(self, chan_no: int, dev):
        self._name = f"C{chan_no}"
        self._dev = dev
        self._WFP = WaveFormPreamble()
        self._last_trace = None
        self._nrOfDivs = 5 # TODO: should be set during initialisation of the scope.
        self.full_code = 256 # TODO: should be set during initialisation of the scope.
        self.center_code = 127 # TODO: should be set during initialisation of the scope.
        self.max_code = self.full_code/2
        self._hori_grid_size = 14
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
        print(f"{self._name}: Volt_DIV {value}")


    def get_waveform_preamble(self):
        """The query returns the parameters of the source using by the command
        :WAVeform:SOURce.
        See text output from a Siglent scope for reference. See Repo.
        """
        params = self._dev._inst.query_binary_values("C1:WaveForm? DESC", datatype='B', container=np.ndarray)
        instrument_name = struct.unpack("16s", params[76:92])[0] #string type parameter.
        instrument_number = struct.unpack("L", params[92:96])[0] #long int type parameter.
        temp = struct.unpack('4c', params[96:100])[0] #string type parameter.
        trace_label = str(temp)
        total_points = struct.unpack('i', params[116:120])[0]
        probe = struct.unpack('f', params[328:332])[0]
        sweeps_per_acq = struct.unpack('L', params[148:152])[0] #for Long sized parameter, use 'L'
        #points_per_pair=struct.unpack('x', params[152:154])[0] #Word= kind of parameter, use 'x' for hex decoding?
        #pair_offset=struct.unpack('x', params[154:156])[0] #Word= kind of parameter, use 'x' for hex decoding?
        vdiv = struct.unpack('f', params[156:160])[0] * probe
        voffset = struct.unpack('f', params[160:164])[0] * probe
        code_per_div = struct.unpack('f', params[164:168])[0] * probe
        nom_bits = struct.unpack('H', params[172:174])[0]  # for Word sized parameter, use 'H'
        horiz_interval = struct.unpack( 'f', params[176:180])[0]
        delay = struct.unpack('d', params[180:188])[0]
        pixel_offset = struct.unpack('d', params[188:196])[0]  #
        verti_unit_str = str(struct.unpack('48s', params[196:244])[0])  # vertaling naar string lijkt niet ok.
        hori_unit_str = str(struct.unpack('48s', params[244:292])[0])
        # trigger_time=struct.unpack('time', params[296:312])[0] #time parameter? how to decode?
        record_type = struct.unpack('H', params[316:318])[0]  # enum, 2 bytes use 'H' for now. need check!
        processing_done = struct.unpack('H', params[318:320])[0]  # enum, 2 bytes use 'H' for now. need check!

        #### timebase is a enum, need to convert first
        timebase_enum = struct.unpack('h', params[324:326])[0]
        timebase = float(TIMEBASE_HASHMAP.get(str(timebase_enum)))
        #TODO: if hashmap doesn't  contain requested key:
        #   It's an error, but probably not a  showstopper, because script is not fit
        #   for the current connected sds, or scope is not a siglent.
        #   FIX: a. create a error class/enum with corresponding exception or combination of the two and
        #   need to classify the error based on more or better information
        #   For now: just print an error message and keep on!
        if timebase == None:
            print("ERROR TIMEBASE CONVERT: UNKNOWN KEY!\n")
        #### end timebase convert

        vert_coupling=struct.unpack('H', params[326:328])[0] # enum, 2 bytes use 'H' for now. need check!
        # fixed_vert_gain=struct.unpack('x', params[332:334])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        BW_limit=struct.unpack('H', params[334:336])[0] #enum, 2 bytes use 'H' for now. need check!
        # vert_vernier=struct.unpack('f', params[336:340])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        # acq_vert_offset=struct.unpack('f', params[340:344])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        wave_src=struct.unpack('H', params[344:346])[0] # enum, 2 bytes use 'H' for now. need check!

        self._WFP.set(total_points, vdiv, voffset, code_per_div, timebase, delay, horiz_interval)
        return (total_points, vdiv, voffset, code_per_div, timebase, delay, horiz_interval)
    
    def get_trigger_status(self):
        """The command query returns the current state of the trigger.

        :return: str
                    Returns either "Arm", "Ready", "Auto", "Trig'd", "Stop", "Roll"
        """
        return self._dev.query(":TRIGger:STATus?")

    def capture(self):
        """_summary_

        :param src_channel: _description_
        """
        #while True:
        #    res = self.get_trigger_status()
        #    if res == SiglentSDSTriggerStatus.STOP.value:
        #        break

        # Send command that specifies the source waveform to be transferred
        #print(self._name)
        #self._dev.write(":WAVeform:SOURce {}".format(self._name))
        #self._dev.write('WFSU SP,4,NP,0,FP,0')
        #self._dev.write('WFSU SP,1,NP,0,FP,0')
        #data = self._dev.query_raw(":WAVeform:DATA?")
        #data = self._dev.query_raw('C1:WF? DAT2')
        #data = data[11:-2]  # eliminate header and remove last two bytes
        #print(f"{self._name}:WF? DAT2")
        data = self._dev._inst.query_binary_values(f"{self._name}:WF? DAT2", datatype='B', is_big_endian=False, container=np.ndarray)
        try:
            trace = np.frombuffer(data, dtype=np.byte)
            self._last_trace = self.convert_to_voltage(trace)
            #self._last_trace = data
        except Exception as e:
            print(e)

        return self._last_trace

    def getMaxOfTrace(self):
        return max(self._last_trace)

    def capture_raw(self):
        """_summary_

        :param src_channel: _description_
        """
        while True:
            res = self.get_trigger_status()
            if res == SiglentSDSTriggerStatus.STOP.value:
                break

            # Send command that specifies the source waveform to be transferred
        self.write(":WAVeform:SOURce {}".format(self._name))
        data = self.query_raw(":WAVeform:DATA?")
        data = data[11:-2]  # eliminate header  and remove last two bytes
        try:
            self._last_trace = np.frombuffer(data, dtype=np.byte)
        except Exception as e:
            print(e)

        return self._last_trace

    def getTRDL(self):
        #need to check diff between this en hori 
        delay_str = self._dev._inst.query("TRig_DeLay?") #according to pyvisa API: query returns str
        delay_str = delay_str.strip("S\n") #Need to combine 'S' with the '\n'. Only strip('S'), doesnot work.
        delay_str = delay_str.strip("TRDL")
        delay_str = delay_str.strip() #remove leading zero
        return float(delay_str) #return a float
    def getVdiv(self):
        VDIV = device.query('C1:VDIV?')
        return VDIV

    def getVofs(self):
        VOFS = device.query('C1:OFST?')
        return VOFS

    def getVcenterTV(self):
        CENTERTV = device.query('TRDL?')
        return CENTERTV

    def getVofs(self):
        TB = device.query('TDIV?')
        return TB
    def getTimeAxisRange(self):
        #See programming manual sds, page 142:
        #first point = delay - (timebase*(hori_grid_size/2))
        self._WFP._timeOfFirstSample = self._WFP._delay -(self._WFP._timebase*(self._hori_grid_size/2))
        self._WFP._timeOfLastSample = self._WFP._interval * self._WFP._total_points
        return (self._WFP._timeOfFirstSample,  self._WFP._timeOfLastSample)

    def timebase_scale(self) -> float:
        """The query returns the current horizontal scale setting in seconds per
        division for the main window.

        :return: float

        """
        return float(self._dev._inst.query_binary_values(":TIMebase:SCALe?"))

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
