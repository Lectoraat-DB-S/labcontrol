import struct

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
import numpy as np
class WaveFormPreamble(object):
    def __init__(self):
        self._total_points = None
        self._vdiv  = None
        self._voffset  = None
        self._code_per_div  = None
        self._timebase  = None
        self._delay = None
        self._interval = None
        self._timeOfFirstValidSample = None
        self._timeOfLastValidSample = None
        self._firstPoint = None
        self._sparsingFactor = None
        self._segmentIndex = None
        self._subArrayCount = None #For sequences acquisitions4
        self._nrOfSweepsPerAcq = None
        self._pairPoints = None
        self._pairOffset = None
        self._nrOfADCBits = None
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

    def set(self, total_points, vdiv, voffset, code_per_div, timebase, delay, interval):
        self._total_points = total_points
        self._vdiv  = vdiv
        self._voffset  = voffset
        self._code_per_div  = code_per_div
        self._timebase  = timebase
        self._delay = delay
        self._interval = interval

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

def decodeWaveFormDescriptor(desc: np.ndarray):
    instrument_name = struct.unpack("16s", desc[76:92])[0]  # string type parameter.
    instrument_number = struct.unpack("L", desc[92:96])[0]  # long int type parameter.
    temp = struct.unpack('4c', desc[96:100])[0]  # string type parameter.
    trace_label = str(temp)
    total_points = struct.unpack('i', desc[116:120])[0]
    probe = struct.unpack('f', desc[328:332])[0]
    sweeps_per_acq = struct.unpack('L', desc[148:152])[0]  # for Long sized parameter, use 'L'
    # points_per_pair=struct.unpack('x', desc[152:154])[0] #Word= kind of parameter, use 'x' for hex decoding?
    # pair_offset=struct.unpack('x', desc[154:156])[0] #Word= kind of parameter, use 'x' for hex decoding?
    vdiv = struct.unpack('f', desc[156:160])[0] * probe
    voffset = struct.unpack('f', desc[160:164])[0] * probe
    code_per_div = struct.unpack('f', desc[164:168])[0] * probe
    nom_bits = struct.unpack('H', desc[172:174])[0]  # for Word sized parameter, use 'H'
    horiz_interval = struct.unpack('f', desc[176:180])[0]
    delay = struct.unpack('d', desc[180:188])[0]
    pixel_offset = struct.unpack('d', desc[188:196])[0]  #
    verti_unit_str = str(struct.unpack('48s', desc[196:244])[0])  # vertaling naar string lijkt niet ok.
    hori_unit_str = str(struct.unpack('48s', desc[244:292])[0])
    # trigger_time=struct.unpack('time', params[296:312])[0] #time parameter? how to decode?
    record_type = struct.unpack('H', desc[316:318])[0]  # enum, 2 bytes use 'H' for now. need check!
    processing_done = struct.unpack('H', desc[318:320])[0]  # enum, 2 bytes use 'H' for now. need check!

    #### timebase is a enum, need to convert first
    timebase_enum = struct.unpack('h', desc[324:326])[0]
    timebase = float(TIMEBASE_HASHMAP.get(str(timebase_enum)))
    # TODO: if hashmap doesn't  contain requested key:
    #   It's an error, but probably not a  showstopper, because script is not fit
    #   for the current connected sds, or scope is not a siglent.
    #   FIX: a. create a error class/enum with corresponding exception or combination of the two and
    #   need to classify the error based on more or better information
    #   For now: just print an error message and keep on!
    if timebase == None:
        print("ERROR TIMEBASE CONVERT: UNKNOWN KEY!\n")
    #### end timebase convert

    vert_coupling = struct.unpack('H', desc[326:328])[0]  # enum, 2 bytes use 'H' for now. need check!
    # fixed_vert_gain=struct.unpack('x', desc[332:334])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
    BW_limit = struct.unpack('H', desc[334:336])[0]  # enum, 2 bytes use 'H' for now. need check!
    # vert_vernier=struct.unpack('f', desc[336:340])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
    # acq_vert_offset=struct.unpack('f', desc[340:344])[0] # enum = kind of parameter, use 'x' for now.Don't what this really means need check!
    wave_src = struct.unpack('H', desc[344:346])[0]  # enum, 2 bytes use 'H' for now. need check!
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

