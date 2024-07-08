import pyvisa as visa
import numpy as np
import time
import struct
from tektronix.scope.Acquisitions import TekTrace
from tektronix.scope.TekLogger import TekLog
from tektronix.scope.Acquisitions import TekScopeEncodings

class TekChannel(object):
    #def __init__(self, chan_no: int, scope=None):
        # 25/6/24: Got a partially imported or circular import error. A way to prevent the circular is explained here:
        # https://stackoverflow.com/questions/64807163/importerror-cannot-import-name-from-partially-initialized-module-m
        # But an better alternative is to change the structure so its purely hierarchical.
        
        #from tektronix.scope.TekScopes import TekScope
    def __init__(self, chan_no: int, visaInstr):
        self._name = f"CH{chan_no}"
        #self._inst = scope.getDevice() # get handle to the underlying VISA instrument.
        self._inst = visaInstr
        self.log = TekLog()
        #if scope != None:
        #    self._parentScope = scope
        self._last_trace = TekTrace()
        self._nrOfDivs = 5  # TODO: should be set during initialisation of the scope.
        self._isVisible = False
        self.setVisible(True)
        self._encoding = None
        #self.setEncoding(TekScopeEncodings.RIBinary) #Not necessary, already doen in default setting of scope object
        
    def setToDefault(self):
        pass
        
        
    def setVisible(self, state:bool):
        if state:
            self._inst.write(f"SELECT:{self._name} ON")
            self._isVisible = True
        else:
            self._inst.write(f"SELECT:{self._name} OFF")
            self._isVisible = False
            
    def isVisible(self):
        return self._isVisible
                
    def setEncoding(self, encoding: TekScopeEncodings):
        if isinstance(encoding, TekScopeEncodings):
            if (encoding==encoding.RIBinary or encoding==encoding.ASCII or 
            encoding==encoding.RPBinary or
            encoding==encoding.SRIbinary or
            encoding==encoding.SRPbinary):
                self._inst.write(f"DATa:ENCdg {encoding.value}")
                self._encoding = encoding
        else:
            self.log.addToLog("Unknown encoding type. switch to RIBinary format")
            self._inst.write(f"DATa:ENCdg {encoding.RPBinary.value}")
                
    def getLastTrace(self):
        return self._last_trace
    
    def queryHorizontalSecDiv(self):
        SEC_DIV = float(self._inst.query('HORIZONTAL:MAIN:SECDIV?')) #Requesting the horizontal scale in SEC/DIV
        return SEC_DIV   
    
    def setVertGain(self, gain):
        #TODO check validity of param
        self._inst.write(f"c:VOLts {gain}")
        
    def setVertScale(self, scale):
        #TODO check validity of param
        self._inst.write(f"{self._name}:SCALE {scale}") #Sets V/DIV CH1
        

    def setAsSource(self):
        self._inst.write(f"DATA:SOURCE {self._name}") #Sets the channel as data source for transimitting data   
    
    def getNrOfPoints(self):
        #TODO:
        # correct handling of event code 2244
        return int(self._inst.query(f"wfmpre:{self._name}:nr_pt?")) #For a channel version of this command:see programming guide page 231
          
    def capture(self):
        """
            copied code below from
             https://github.com/tektronix/Programmatic-Control-Examples/blob/master/Examples/Oscilloscopes/BenchScopes/src/SimplePlotExample/tbs_simple_plot.py
        """
        #self._inst.write('autoset EXECUTE')  # autoset
        #bin_wave =self._inst.query_binary_values("CURV?")
        self.log.addToLog("start querying scope")
        bin_wave = self._inst.query_binary_values('curve?', datatype='b', container=np.array)
        self._last_trace.rawYdata = bin_wave
        self.log.addToLog("scope query ended")
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
        total_time = tscale * numberOfPoints
        tstop = tstart + total_time
        scaled_time = np.linspace(tstart, tstop, num=numberOfPoints, endpoint=False)
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        scaled_wave = (unscaled_wave - vpos) * vscale + voff
        #put the data into internal 'struct'
        self._last_trace.scaledYdata = scaled_wave
        self._last_trace.scaledXData = scaled_time

    
    """
Syntax WFMPre?
Related Commands
Returns The format of the response when the DATa:SOUrce waveform is activated is:
BYT_Nr <NR1>;BIT_Nr <NR1>;ENCdg { ASC | BIN }; BN_Fmt { RI | RP
};BYT_Or { LSB | MSB };NR_Pt <NR1>; WFID <Qstring>;PT_FMT {ENV |
Y};XINcr <NR3>; PT_Off <NR1>;XZERo <NR3>;XUNit<QString>;YMUlt
<NR3>; YZEro <NR3>;YOFF <NR3>;YUNit <QString>

Hieronder een output van de scoop na aanzetten en autoscale
2;16;BIN;RP;MSB;2500;"Ch1, DC coupling, 5.0E-1 V/div, 5.0E-5 s/div,
 2500 points, Sample mode";Y;2.0E-7;0;-2.5E-4;"s";7.8125E-5;0.0E0;3.2768E4;"Volts"

Nogmaals maar dan met de fmt:
BYT_Nr <NR1> = 2;
BIT_Nr = 16;
ENCdg = BIN;
BN_Fmt = RP;
BYT_Or = MSB;
NR_Pt  = 2500;
WFID = "Ch1, DC coupling, 5.0E-1 V/div, 5.0E-5 s/div, 2500 points, 
Sample mode";
;PT_FMT  = Y;
;XINcr = 2.0E-7;
 PT_Off = 0;
 XZERo = -2.5E-4;
 XUNit = "s";
 YMUlt = 7.8125E-5;
 YZEro = 0.0E0;
 YOFF = 3.2768E4
 YUNit = "Volts"
        
        
        """
   
    def queryWaveFormPreamble(self):
        #TODO add intern state for ascii or binary. Defines query or binary_query
        self.setAsSource()
        response = self._inst.query('WFMPRE?')
        
            
    
    def createTimeVector(self):
        """
        #Converting the raw time data of each sample to the correct time values for each sample
        for i in range(int(NR_PT)):
        timeSample = ((i-PT_OFF_CH1)*XINCR_CH1)+XZERO_CH1
        timeData.append(timeSample)
        """
    
    def sampleValue2Voltage(self):
        pass
        """
        for i in range(len(splitDataCH2)):
        scopeDataCH2.append(int(splitDataCH2[i]))
        voltageSampleCH2 = ((float(scopeDataCH2[i])-YOFF_CH2)*YMULT_CH2)+YZERO_CH2
        voltageDataCH2.append(voltageSampleCH2)
        """
    
    
    """
    scope.query('WFMPRE?')) #Same as above, but with more information 

XZERO_CH1 = float(scope.query('WFMPRE:XZERO?')) #Requesting Horizontal Position value in s
XINCR_CH1 = float(scope.query('WFMPRE:XINCR?')) #Requesting multiplier for scaling time data
PT_OFF_CH1 = float(scope.query('WFMPRE:PT_OFF?')) #Requesting Trigger Offset in sample values

YZERO_CH1 = float(scope.query('WFMPRE:YZERO?')) #Requesting waveform conversion factor (Not sure what this is)
YMULT_CH1 = float(scope.query('WFMPRE:YMULT?')) #Requesting multiplier for scaling voltage data
YOFF_CH1 = float(scope.query('WFMPRE:YOFF?')) #Requesting vertical offset in V for calculating voltage

V_DIV_CH1 = float(scope.query('CH1:SCALE?')) #Requesting the vertical scale of CH1 in V/DIV

debug output.
'1;8;BIN;RI;MSB;2500;"Ch1, DC coupling, 2.0E0 V/div, 2.5E-4 s/div, 2500 points, Sample mode";Y;1.0E-6;0;-1.25E-3;"s";8.0E-2;0.0E0;0.0E0;"Volts"'
    
    """
    
    
    
    """
        getTrace
        immediate measurement of channel trace 
        see: https://forum.tek.com/viewtopic.php?t=136954
    """
       
    def getVoltage(self):
        self._inst.write(f"MEASUREMENT:IMMED:SOURCE {self._name}") #force scope to do immediate measurement
        self._inst.write("MEASUREMENT:IMMED:TYPE MEAN")
        self._inst.write("acquire:state on")
        self._inst.query("*opc?")
        return self._inst.query('measurement:immed:value?')


