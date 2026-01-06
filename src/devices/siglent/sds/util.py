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



class SiglentIDN(object):
    def __init__(self, mybrand, mymodel, myserial, myfirmware) -> None:
        self.brand = mybrand
        self.model = mymodel
        self.serial = myserial
        self.firmware = myfirmware
        

def decodeIDN(idnstr:str):
        """
        example
        Siglent Technologies,SDS1204X-E,SDS1EBAC0L0098,7.6.1.15
        """
        splitted = idnstr.split(",")
        if len(splitted) != 4:
            return None
        manufacturer  = "Siglent"
        if manufacturer in splitted[0]:
            if len(splitted[2])==14:
                brand = splitted[0]
                model = splitted[1]
                serial = splitted[2]
                firmware = splitted[3]
                siglentIdn = SiglentIDN(brand,model, serial, firmware) 
                return siglentIdn
        return None

def getModel(devStr:str):
        """
        Parameters: 
            devStr: de sectienaam uit de ini-file
            models: een lijst met typenummers die horen bij deze class. 
        Siglent heeft een strak modelnummer schema, zo lijkt het tenminste. Desktop/Bench scopes beginnen met de 
        letters SDS en handhelds met de letters SHS. Daarna volgen 3 of 4 cijfers en eventueel wat letters, al dan niet met 
        spaties en/of streepjes.
        De ini. file moet deze richtlijn volgen. Mogelijk komt er 'Siglent ' voorafgaande het modelnummer te staan, maar dat 
        zijn dan de opties.
        Aanpak voor decodering:
        1. Zit 'Siglent' in de sectienaam van de ini file? Zo ja, dan moet die vooraan staan. Verder niks mee doen
        2. Zit 'Siglent' niet in de sectie naam, dan moet, na strippen van spaties en streepjes de letters "SDS" of "SHS"
        komen. Zitten die er niet in, return false.
        3. Na de letters "SDS" of "SHS" moeten er 3 of 4 cijfers komen, zo niet -> return false
        4. Het gevonden modelnr van 3 of 4 cijfers moet vergeleken worden met KNOWN_MODELS. 
        Meest eenvoudige manier om te checken of een klasse de juiste sectie uit de ini pakt, is
        door de nummers uit de strings te isoleren.
        Eigenlijk heb ik twee functies nodig: 1. haal de nummers uit een string, bijv 12345AXD34, moet dan twee getallen
        opleveren 12345 en 34. 2. Haal de alpha tekens uit de string, dus bij dezelfde string is dat AXD."""
        brandStr = "Siglent"
        res = devStr.find(brandStr)
        if res != -1:
            devStr=devStr.strip(brandStr)
        devStr = devStr.strip()
        devStr = devStr.strip("-") #the sectionname should now start with "SDS" or "SHS"
        if "SDS" not in devStr and "SHS" not in devStr:
            return None
        #A siglent device have been found, now check the numbers
        
        tmp1 = devStr[3:6]
        tmp2 = devStr[3:7]
        devNr = None
        if tmp2.isnumeric():
            #4 digit number
            devNr = int(tmp2)
            suppStr = devStr[7:]
            return devNr, suppStr
        else:
            if tmp1.isnumeric():
                #it is a 3 digit modelnum
                devNr = int(tmp1)
                suppStr = devStr[6:]
                return devNr, suppStr
            else:
                return None
        """
            oude code, bewaar ik nog even , misschien toch nog handig.        
            currModel = None 
            for model in models:
                modelstr = str(model)
                tmp1 = modelstr[3:6]
                tmp2 = modelstr[3:7]
                if tmp2.isnumeric():
                    #4 digit number
                    currModel = int(tmp2)
                    currModelRange = range(currModel, currModel+99)
                    if devNr in currModelRange: #TODO: check supplemental 
                        return True
                else:
                    if tmp1.isnumeric():
                        #it is a 3 digit modelnum
                        currModel = int(tmp1)
                        currModelRange = range(currModel, currModel+999)
                        if devNr in currModelRange: #TODO: check supplemental string
                            return True
            return False
        """
        

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

