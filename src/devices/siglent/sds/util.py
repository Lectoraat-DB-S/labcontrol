import struct
import numpy as np

MATH_FUNC_ADD = 0
MATH_FUNC_SUB = 1
MATH_FUNC_MUL = 2
MATH_FUNC_RAT = 3
MATH_FUNC_FFT = 4
MATH_FUNC_INT = 5
MATH_FUNC_DIF = 6
MATH_FUNC_SQR = 7

def rawSave():
    #wat opslaan?
    #Soort apparaat, merk, model(nummer), datum registratie.
    #conversieinfo (hangt van apparaat af): 
    # Generieke info: aantal samples, aantal kanalen, samplerate, eenheid van horizontale en vertical as 
    # kanaal instellingen: verticale en horizontale offset, gain instelling
    # Tijdbasis en trigger instellingen
    columnName =f"sampleCH{channr}"
    nrOfSamp = 0
    

def saveTrace():
    columnNames ={"s"}

#hulpfunctie
def splitAndStripV(response):
    response =response.rstrip()
    response =response.strip("V")
    splitted = response.split(",")
    return float(splitted[1])

def splitAndStripHz(response):
    response =response.rstrip()
    response =response.strip("Hz")
    splitted = response.split(",")
    return float(splitted[1])

def splitAndStripSec(response):
    response =response.rstrip()
    response =response.strip("s")
    response =response.strip("S")
    splitted = response.split(",")
    return float(splitted[1])

def splitAndStripProc(response):
    response =response.rstrip()
    response =response.strip("%")
    splitted = response.split(",")
    return float(splitted[1])


"""
  TIMEBASE: enum
               _0       200_ps/div
               _1       500_ps/div
               _2       1_ns/div
               _3       2_ns/div
               _4       5_ns/div
               _5       10_ns/div
               _6       20_ns/div
               _7       50_ns/div
               _8       100_ns/div
               _9       200_ns/div
               _10      500_ns/div
               _11      1_us/div
               _12      2_us/div
               _13      5_us/div
               _14      10_us/div
               _15      20_us/div
               _16      50_us/div
               _17      100_us/div
               _18      200_us/div
               _10      500_us/div
               _20      1_ms/div
               _21      2_ms/div
               _22      5_ms/div
               _23      10_ms/div
               _24      20_ms/div
               _25      50_ms/div
               _26      100_ms/div
               _27      200_ms/div
               _28      500_ms/div
               _29      1_s/div
               _30      2_s/div
               _31      5_s/div
               _32      10_s/div
               _33      20_s/div
               _34      50_s/div
               _35      100_s/div
               _100     EXTERNAL
               endenum

"""
""" INR STATUSBIT TABLE. FORMAT: VALUE, DESCRIPTION.
"""
INR_HASHMAP = {
                    "0":"A new signal has been acquired",
                    "1": "A screen dump has terminated", 
                    "2":"A return to the local state is detected",
                    "3":"A time-out has occurred in a data block transfer",
                    "4":"A segment of a sequence waveform has been acquired",
                    "5":"Reserved for LeCroy use",
                    "6":"Memory card, floppy or hard disk has become full in ―AutoStore Fill‖ mode",
                    "7":"A memory card, floppy or hard disk exchange has been detected",
                    "8":"Waveform processing has terminated in Trace A",
                    "9":"Waveform processing has terminated in Trace B",
                    "10":"Waveform processing has terminated in Trace C",
                    "11":"Waveform processing has terminated in Trace D",
                    "12":"Pass/Fail test detected desired outcome",
                    "13":"Trigger is ready"
                    }
TIMEBASE_HASHMAP = {
                    "0":"200e-12","1": "500e-12", "2":"1e-9","3":"2E-9",
                    "4":"5e-9","5":"10e-9","6":"20e-9","7":"50e-9",
                    "8":"100e-9","9":"200e-9","10":"500e-9",
                    "11":"1e-6","12":"2e-6","13":"5e-6",
                    "14":"10e-6","15":"20e-6","16":"50e-6",
                    "17":"100e-6","18":"200e-6","19":"500e-6",
                    "20": "1e-3", "21": "2e-3", "22": "5e-3",
                    "23": "10e-3", "24": "20e-3", "25": "50e-3",
                    "26": "100e-3", "27": "200e-3", "28": "500e-3",
                    "29": "1", "30": "2", "31": "5",
                    "32": "10", "33": "20", "34": "50",
                    "35": "100"
                    }
class WaveFormTrace(object):
    def __init__(self):
        self._nrOfDivs = 5 # TODO: should be set during initialisation of the scope.
        self.full_code = 256 # TODO: should be set during initialisation of the scope.
        self.center_code = 127 # TODO: should be set during initialisation of the scope.
        self.max_code = self.full_code/2
        self._hori_grid_size = 14 # TODO: is this a fixed number for Siglent? Check this.
        self._rawdata = None
        self._tracedata = None
        self._WVP = WaveFormPreamble()
        
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
        
    def getWVP(self):
        return self._WVP
    
    def getTrace(self):
        return self._tracedata
    
    def setTrace(self, data):
        self._tracedata = data
        
    def getRawTrace(self):
        return self._rawdata
    
    def setRawTrace(self, data):
        self._rawdata = data

class WaveFormPreamble(object):
    def __init__(self):
        #TODO: put subsequent in order of the waveform template.
        self._total_points = None               #Number of points of (last) acquired waveform
        self._vdiv  = None                      #Number of units (e.g. V) per division 
        self._voffset  = None                   #Vertical offset. Calc floating values from raw data : VERTICAL_GAIN * data - VERTICAL_OFFSET
        self._maxGridVal  = None                #Maximum allowed value. It corresponds to the upper edge of the grid.
        self._minGridVal  = None                #Minimum allowed value. It corresponds to the lower edge of the grid.
        self._nomBits = None                    #Measure of the intrinsic precision of the observation: ADC data is 8 bit, 
                                                #when averaged it is 10-12 bit, etc. TODO: implement 
        self._timebase  = None                  #TDIV: the amount of time per division. SEE TIMEBASE_HASHMAP.
        self._delay = None                      #HORIZ_OFFSET: trigger offset, seconds between the trigger and the first data point
        self._interval = None                   #HORIZ_INTERVAL: float sampling interval for time domain waveforms. 
                                                    #TODO: check if is same as sample interval.
        self._timeOfFirstValidSample = None     #FIRST_VALID_PNT count of number of points to skip before first good point
                                                #   FIRST_VALID_POINT = 0
                                                #   for normal waveforms.
        self._timeOfLastValidSample = None      #Index of last good data point in record before padding (blanking) was started. 
                                                #   LAST_VALID_POINT = WAVE_ARRAY_COUNT-1
                                                #   except for aborted sequence and rollmode acquisitions
        self._firstPoint = None
        self._sparsingFactor = None
        #The definition of subsequent parameter is somewhat vague: it should be the same as the SN param of the WFSU command, but the
        #programming manual does not mentions such a param. Probably the NP param is referred.
        self._segmentIndex = None               #SEGMENT_INDEX: see Above
        
        
        self._subArrayCount = None #For sequences acquisitions
        self._nrOfSweepsPerAcq = None
        self._pairPoints = None
        self._pairOffset = None
        self._horizontalInterval = None         #HORIZ_INTERVAL: sampling interval for time domain waveforms
        self._horizontalOffset =  None              #HORIZ_OFFSET: trigger offset for the first sweep of the trigger
                                                #   seconds between the trigger and the first data point
        self._pixelOffset = None                #PIXEL_OFFSET: needed to know how to display the waveform
        self._vertUnit = None                   #VERTUNIT: units of the vertical axis

        self._horUnit = None                    #HORUNIT: units of the horizontal axis
        self._horUncertainty = None             #uncertainty from one acquisition to the  next, of the horizontal offset in seconds
        self._triggerTime = None                #TRIGGER_TIME: time of the trigger
        
        self._recordType = None
        self._processingDone = None
        self._vertCoupling = None
        self._vertGain = None
        self._bwLimit = None
        self._waveSource = None
        #NOM_SUBARRAY_COUNT
        #HORIZ_INTERVAL: float2
        #HORIZ_OFFSET: double;
        # PIXEL_OFFSET: double;
        #VERTUNIT: unit_definition;4
        ##HORUNIT: unit_definition;
        # HORIZ_UNCERTAINTY: float;
        # TRIGGER_TIME: time_stamp;
        # ACQ_DURATION: float;
        # Acquisition_TYPE:
        # PROCESSING_DONE: enum
        # < 320 > RESERVED5: word;
        # RIS_SWEEPS: word;
        # TIMEBASE: enum
        # VERT_COUPLING: enum
        # PROBE_ATT: float
        # FIXED_VERT_GAIN: enum
        # BANDWIDTH_LIMIT: enum
        # VERTICAL_VERNIER: float#
        # ACQ_VERT_OFFSET: float
        # WAVE_SOURCE: enum
    def isEmpty(self):
        if ((self._total_points == None) and  (self._vdiv  == None) and (self._voffset == None)):
            return True
        else:
            return False

    def set(self, total_points, vdiv, voffset, code_per_div, timebase, delay, interval):
        self._total_points = total_points
        self._vdiv  = vdiv
        self._voffset  = voffset
        self._code_per_div  = code_per_div
        self._timebase  = timebase
        self._delay = delay
        self._interval = interval
        
    def decodeWaveFormDescriptor(self, params):
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
            self._logger.error("ERROR TIMEBASE CONVERT: UNKNOWN KEY!\n")
        #### end timebase convert

        vert_coupling=struct.unpack('H', params[326:328])[0] # enum, 2 bytes use 'H' for now. need check!
        # fixed_vert_gain=struct.unpack('x', params[332:334])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        BW_limit=struct.unpack('H', params[334:336])[0] #enum, 2 bytes use 'H' for now. need check!
        # vert_vernier=struct.unpack('f', params[336:340])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        # acq_vert_offset=struct.unpack('f', params[340:344])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
        wave_src=struct.unpack('H', params[344:346])[0] # enum, 2 bytes use 'H' for now. need check!

        self._WFP.set(total_points, vdiv, voffset, code_per_div, timebase, delay, horiz_interval)
        return (total_points, vdiv, voffset, code_per_div, timebase, delay, horiz_interval)
    

class Utils():
    def index2time(length, samp_rate, start_time = 0):
        """
        Creates a vector of timeinstances, to be used for plotting or calculations
        :param length: integer value giving the length of the registration of samples
        :param samp_rate: the sample rate used during registration
        :param start_time: the moment of the first sample, depends on moment of triggering.
        """
        #return np.linspace(start_time, length*(1.0/samp_rate, length)
        pass
    def samples2volts(samples, length, vdif, vofs):
        """
        Convert an array of mere meaningless samples into a array with voltage measurements
        :param samples: array with quantized (integer) values
        :param vdiv: the voltage per div setting of the oscilloscoop.
        :param vofs: the vertical offset of the oscilloscoop during acquisition.
        """
        #out=vofs + vdif* samples[i]
        pass



    
class TimeStamp(object):
    """
    ;                 time_stamp        double precision floating point number,
    ;                                   for the number of seconds and some bytes
    ;                                   for minutes, hours, days, months and year.
    ;
    ;                                   double  seconds     (0 to 59)       (8 bytes)
    ;                                   byte    minutes     (0 to 59)       (1 byte)
    ;                                   byte    hours       (0 to 23)       (1 byte)
    ;                                   byte    days        (1 to 31)       (1 byte)
    ;                                   byte    months      (1 to 12)       (1 byte)
    ;                                   word    year        (0 to 16000)    (2 bytes)
    ;                                   word    unused                      (2 bytes)
    ;                                   There are 16 bytes in a time field.
    """

    def __init__(self, time_dat):
        #convert byte array to timestamp struct
        self._seconds = struct.unpack('d', time_dat)

        pass

