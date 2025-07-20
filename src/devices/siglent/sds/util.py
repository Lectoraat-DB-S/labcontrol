from scipy.optimize import curve_fit
import struct
import numpy as np
import pyvisa
from enum import Enum
MATH_FUNC_ADD = 0
MATH_FUNC_SUB = 1
MATH_FUNC_MUL = 2
MATH_FUNC_RAT = 3
MATH_FUNC_FFT = 4
MATH_FUNC_INT = 5
MATH_FUNC_DIF = 6
MATH_FUNC_SQR = 7

def sine_function(x, amp, omega, phase, offset):
    return amp * np.sin(omega * x + phase) + offset

def guessSine(t, y, intialGuess=None):

    if intialGuess == None:
        initial_guess = [1,2, 0, 0]

    # Perform the curve fitting
    params, covariance = curve_fit(sine_function, t, y, p0=intialGuess)

    # Extract the fitted parameters
    A_fit, B_fit, C_fit, D_fit = params

    print(f"Fitted parameters: A={A_fit}, B={B_fit}, C={C_fit}, D={D_fit}")
    # Generate y values using the fitted parameters
    print(f"covariantie = {covariance}")
    return params, covariance


class SIGLENT_TIME_STAMP(object):
    def __init__(self):
        self.seconds    = None  #float => 64 bits
        self.minutes    = None  #byte => 8 bits, signed
        self.hours      = None  #byte => 8 bits
        self.days       = None  #byte => 8 bits
        self.month      = None  #byte => 8 bits
        self.years      = None  #word => 16 bits
        self.unused     = None  #word => 16 bits

    def decode(self, byteArray):
        self.seconds = struct.unpack('f', byteArray[296:304])[0] #time parameter? how to decode?
        self.minutes = struct.unpack('B', byteArray[304:305])[0]

class BANDWIDTH_LIMIT(Enum): # for bwlimtit param of preamble
    OFF     = 0
    M20     = 1
    M200    = 3

class RECORDTYPE(Enum):
    single_sweep        = 0
    interleaved         = 1
    histogram           = 2
    graph               = 3
    filter_coefficient  = 4
    complex             = 5
    extrema             = 6
    sequence_obsolete   = 7
    centered_RIS        = 8
    peak_detect         = 9

KNOWN_MODELS = [
        "SDS1000CFL",   #non-SPO model Series
        "SDS1000A",     #non-SPO model Series
        "SDS1000CML+",  #non-SPO model Series
        "SDS1000CNL+",  #non-SPO model Series
        "SDS1000DL+",   #non-SPO model Series
        "SDS1000E+",    #non-SPO model Series
        "SDS1000F+",    #non-SPO model Series
        "SDS2000",      #SPO model Series
        "SDS2000X",     #SPO model Series
        "SDS1000X",     #SPO model Series
        "SDS1000X+",    #SPO model Series
        "SDS1000X-E",   #SPO model Series
        "SDS1000X-C",   #SPO model Series
        #USED MODEL (TESTED) SHOWN BELOW
        "SDS2504X Plus",
        "SDS1202X",
        "SDS1202X-E",
    ]

class SiglentIDN(object):
    def __init__(self, mybrand, mymodel, myserial, myfirmware) -> None:
        self.brand = mybrand
        self.model = mymodel
        self.serial = myserial
        self.firmware = myfirmware
        

def checkIDN(idnstr:str):
        """
        example
        Siglent Technologies,SDS1204X-E,SDS1EBAC0L0098,7.6.1.15
        """
        splitted = idnstr.split(",")
        if len(splitted) != 4:
            return None
        manufacturer  = "Siglent"
        if manufacturer in splitted[0]:
            if splitted[1] in KNOWN_MODELS:
                if len(splitted[2])==14:
                    brand = splitted[0]
                    model = splitted[1]
                    serial = splitted[2]
                    firmware = splitted[3]
                    siglentIdn = SiglentIDN(brand,model, serial, firmware) 
                    return siglentIdn
        return None

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

