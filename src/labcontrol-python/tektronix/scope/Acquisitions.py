#from tektronix.scope.Channel import TekChannel
from enum import Enum
#A class that holds one registration of a channel
class TekTrace(object):
    #def __init__(self, channel: TekChannel):
    def __init__(self):
        self.rawYdata    = None #data without any conversion or scaling taken from scope
        self.rawXdata    = None 
        self.scaledYdata = None #data converted to correct scale e.g untis
        self.scaledXData = None 
        #Horizontal data settings of scope
        self.secDiv      = None # see TDS prog.guide table2-17: (horizontal)scale = (horizontal) secdev 
        self.V_DIV       = None 
        self.XZERO       = None # Horizontal Position value in s
        self.XINCR       = None # multiplier for scaling time data, time between two sample points.
        self.TRIG_OFF    = None # Trigger Offset in sample values
        self.NR_PT       = None # the number of points of trace.

        self.YZERO       = None # waveform conversion factor 
        self.YMULT       = None # multiplier for scaling voltage data
        self.YOFF        = None # vertical offset in V for calculating voltage
        #self.myChannel   = None # reference to channel where this trace is part of.
    
    def dump(self):
        line = f"self.rawYdata    = {self.rawXdata}\n"
        line += f"self.rawYdata    = {self.rawYdata}"
        print(line)
         
class TekScopeEncodings(Enum):
    ASCII = "ASCi"
    RIBinary = "RIBinary" #Signed Integer, most significant byte first, fastest
    RPBinary = "RPBinary" #positive Integer, most significant byte first
    SRIbinary = "SRIbinary"#Signed Interger, least significant byte first.
    SRPbinary = "SRPbinary"#positive Integer, least significant byte first
        