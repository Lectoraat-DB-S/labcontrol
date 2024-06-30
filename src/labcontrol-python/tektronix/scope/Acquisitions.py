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
        self.V_DIV       = None # probably the same as Ymult.
        self.XZERO       = None # Horizontal Position value
        self.XUnitStr    = None # unit of X-as/xdata
        self.XINCR       = None # multiplier for scaling time data, time between two sample points.
        self.NR_PT       = None # the number of points of trace.
        self.sampleTime  = None # same as XINCR, Ts = time between to samples.

        self.YZERO       = None 
        self.YMULT       = None # vertical step scaling factor. Needed to translate binary value of sample to real stuff.
        self.YOFF        = None # vertical offset in V for calculating voltage
        self.YUnitStr    = None
        self.couplingstr = None
        self.acqModeStr  = None
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
    
class WaveformPreamble(object):
    def __init__(self, visaInstrument):
        self._inst = visaInstrument
        self.thisTrace              = TekTrace()
        self.nrOfBytePerTransfer    = None
        self.nrOfBitsPerTransfer    = None
        self.encodingFormatStr      = None
        self.binEncodingFormatStr   = None
        self.binFirstByteStr        = None
        self.nrOfPoints             = None
        self.vertMode               = None #Y, XY, or FFT.
   
    def queryPreamble(self):
        response = self._inst.query('WFMPRE?')
        self.decode(response)
        
    def getTrace(self):
        return self.thisTrace
    
    def getPreamble(self):
        return self
    
    def decode(self, strToDecode):
        paramlist = strToDecode.split(';')

        self.nrOfBytePerTransfer  = int(paramlist[0])
        self.nrOfBitsPerTransfer  = int(paramlist[1])
        self.encodingFormatStr    = str(paramlist[2])
        self.binEncodingFormatStr = str(paramlist[3])
        self.binFirstByteStr      = str(paramlist[4])
        self.nrOfPoints           = int(paramlist[5])
        self.vertMode             = str(paramlist[7])
        self.thisTrace.sampleTime = float(paramlist[8])
        self.thisTrace.XINCR      = float(paramlist[8])
        self.thisTrace.XZERO      = float(paramlist[10])
        self.thisTrace.XUnitStr   = str(paramlist[11])
        self.thisTrace.YMULT      = float(paramlist[12])
        self.thisTrace.YZERO      = float(paramlist[13])
        self.thisTrace.YOFF       = float(paramlist[14])
        self.thisTrace.YUnitStr   = str(paramlist[15])
        self.decodeChanPreamble(paramlist[6])
        
        return self
    # decodeChanPreamble
    # input: chanStrToDecode = a string containing the stripped substring of the preamble
    # which is the 7th element of the splitted preamble string of a TDS Series Oscilloscope. 
    # this method will further split and clean this substring.
    # probably called by WaveformPreamble.decode.
    def decodeChanPreamble(self, chanStrToDecode):
        #6th element in channellist of TDS
        channelParamList = chanStrToDecode.strip('"')
        channelParamList=channelParamList.strip("'")
        channelParamList=channelParamList.split(',')
        sourceChanStr = str(channelParamList[0])
        hulp = (channelParamList[1].strip()).split()
        self.thisTrace.couplingstr = str(hulp[0])
        hulp = (channelParamList[2].strip()).split()
        self.thisTrace.V_DIV  = float(hulp[0])
        hulp = (channelParamList[3].strip()).split()
        self.thisTrace.secDiv = float(hulp[0])
        hulp = (channelParamList[4].strip()).split()
        self.thisTrace.NR_PT = float(hulp[0])
        hulp = (channelParamList[5].strip())
        self.thisTrace.acqModeStr = str(hulp)
    
    
    """
    OLD CODE FROM capture methode
     #numberOfPoints = int(self._inst.query('wfmpre:nr_pt?'))
        numberOfPoints = self.getNrOfPoints()
        #TODO: move these queries to one logic location without creating (circurlar) import errors
        tscale = float(self._inst.query('wfmpre:xincr?'))
        tstart = float(self._inst.query('wfmpre:xzero?'))
        vscale = float(self._inst.query('wfmpre:ymult?'))  # volts / level
        voff = float(self._inst.query('wfmpre:yzero?'))  # reference voltage
        vpos = float(self._inst.query('wfmpre:yoff?'))  # reference position (level)
        #print(self._inst.query("WFMPre?"))
        self._last_trace.secDiv = self.queryHorizontalSecDiv()
        # create scaled vectors
        # horizontal (time)
        self.getLastTrace().NR_PT = numberOfPoints
        self.getLastTrace().XINCR = tscale
        self.getLastTrace().XZERO = tstart
        self.getLastTrace().YMULT = vscale
        self.getLastTrace().YZERO = voff
        self.getLastTrace().YOFF = vpos
        
    """    
