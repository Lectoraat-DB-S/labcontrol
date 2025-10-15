from enum import Enum
import pyvisa
import numpy as np
import time
import struct

from devices.BaseScope import BaseChannel, BaseWaveForm, BaseWaveFormPreample
from devices.tektronix.scope.TekLogger import TekLog


class TekChannel(BaseChannel):
    IMMEDMEASTYPES =["CRMs","CURSORRms","DELay","FALL",
                        "FREQuency","MAXImum","MEAN","MINImum","NONe","NWIdth","PDUty","PERIod","PHAse", 
                        "PK2pk","PWIdth","RISe"]
    VALIDPROBEVALS = [1, 10, 20, 50, 100, 500, 1000]

    @classmethod
    def getChannelClass(cls, chan_no, dev):
        """ Tries to get the right device class, based on the url"""
        if cls is TekChannel:
            return cls
        else:
            return None      
    def __init__(self, chan_no: int, visaInstr:pyvisa.resources.MessageBasedResource, perMeasDict:dict, 
                 nHDivs = 10, nVDivs = 10 , visHDivs = 10, visVDivs = 8):
        super().__init__(chan_no, visaInstr)
        self.name = f"CH{chan_no}"
        self.log = TekLog()
        self.perMeasDict:dict = perMeasDict
        self.nrOfHoriDivs = nHDivs # maximum number of divs horizontally
        self.nrOfVertDivs = nVDivs # maximum number of divs vertically 
        self.visibleHoriDivs = visHDivs # number of visible divs on screen
        self.visibleVertDivs = visVDivs # number of visible divs on screen
        #if scope != None:
        #    self._parentScope = scope
        self.WFP= TekWaveFormPreamble(visaInstr)
        self.WF = TekWaveForm()
        if self.isVisible():
            self.setSource()
            self.WFP.queryPreamble()
            self.WF.setPreamble(self.WFP)
            
        
        #self.setVisible(state=True)
        self.encoding = None
        
    def queryNrOfSamples(self):
        NR_PT =  int(self.visaInstr.query('WFMPRE:NR_PT?')) #Requesting the number of samples
        return NR_PT     
             
    def setVisible(self, state:bool):
        if state:
            self.visaInstr.write(f"SELECT:{self.name} ON")
            self.isVisible = True
        else:
            self.visaInstr.write(f"SELECT:{self.name} OFF")
            self.isVisible = False
            
    def isVisible(self):
        resp = self.query(f"SELECT:{self.name}?")
        resp = resp.strip('\n')
        if resp == "0" or resp == 0:
            return False
        else:
            return True
        

    def setCoupling(self, coupling):
        if coupling == "AC" or coupling == "DC" or coupling == "GND":
            self.write(f"{self.name}:COUPLING AC")

    def setProcMode(self, mode):
        super().setProcMode(mode)
                
    def getLastTrace(self):
        return self.WF
    
    def probe(self, factor):
        #CH<x>:PRObe { 1 | 10 | 20 | 50 | 100 | 500 | 1000 }
        if factor in TekChannel.VALIDPROBEVALS:
            self.write(f"{self.name}:PRObe {factor}")
        return
    
    """
    def probe(self):
        resp = self.query(f"{self.name}:PRObe?")
        resplist = resp.split()
        respsize = len(resplist)
        match respsize:
            case 0:
                return "ERROR"
            case 1:
                return int(resplist[0])
            case 2:
                return int(resplist[1])
            case _:
                return "ERROR"
        return"""
       
    def setVertScale(self, scale):
        """Sets the vertical sensitivity of this channel. Has same functionality as 'setVoltsDiv'"""
        #TODO check validity of param
        self.visaInstr.write(f"{self.name}:SCALE {scale}") #Sets V/DIV CH1
  
    def setVoltsDiv(self, scale): 
        """Sets the vertical sensitivity (i.e. Vdiv) of this channel. This is the alternative method for setting  
        Vdiv. Same functionality as 'setVdiv'.
        """
        #TODO check validity of param
        vertscalelist = [2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1, 2, 5]
        if scale in vertscalelist:
            self.visaInstr.write(f"{self.name}:SCALE {scale}") #Sets V/DIV CH1   
        else:   
            self.log.addToLog("invalid VDIV input.....") 
            self.visaInstr.write(f"{self.name}:SCALE {scale}") #Sets V/DIV CH1 
    
    def setVdiv(self, value):
        """Sets the vertical sensitivity (i.e. Vdiv) of this channel. This is the default method for setting  
        Vdiv, defined in BaseChannel.
        """
        self.setVoltsDiv(value) 
    
    def getVdiv(self):
        """Sets the vertical sensitivity (i.e. Vdiv) of this channel. This is the default method for setting  
        Vdiv, defined in BaseChannel.
        """
        return self.visaInstr.query(f"{self.name}:SCALE ?") 
    
    def position(self):
        """Gets the (vertical) position of this channel with respect to the center graticule. Unit of position is divisions (divs)."""
        return self.visaInstr.query(f"{self.name}:POSition?") 
    
    def position(self, pos):
        """"Sets the (vertical) position of this channel with respect to center. Parameter pos is the deviation from center in divisions (divs). 
        A positive value means above center, negative means below center. """
        self.visaInstr.write(f"{self.name}:POSition {pos}")

    def getYzero(self):
        """Gets the vertical offset of this channel. For this TDS implementation the parameter 
        'yzero' has been selected. Remark a TDS has also an 'yoff' parameter, which is an offset value in digitizer
        levels. The y value of a sample is to be calculated by: 
        value_in_YUNits = ((curve_in_dl - YOFF_in_dl) * YMUlt) + YZERO_in_YUNits 
        The yoff parameter is accessible through the WaveFormPreamble object of this channel
        """
        return self.WFP.yzero
    
    def getXzero(self):
        """Gets the vertical offset of this channel on display. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        return self.WFP.xzero


    def setSource(self):
        """Sets this channel as the source for transferring waveform or measurements from this oscilloscope by queries 
        like CURVe, WFMPre, or WAVFrm?. As specified by the manual, one can transfer only one waveform at a time.
        """ 
        #check if channel is valid 
        self.visaInstr.write(f"DATA:SOURCE {self.name}") #Sets the channel as data source     
    
    def getSource(self): 
        """Gets the current source (i.e. which channel) of which the waveform will be retrieved at a capture, for 
        instance"""  
        return self.visaInstr.query(f"DATA:SOURCE?")
    
    def getNrOfPoints(self):
        """Gets the number of datapoints present when the waveform of this channel will be retrieved."""
        # correct handling of event code 2244
        return int(self.visaInstr.query(f"wfmpre:{self.name}:nr_pt?")) #For a channel version of this command:see programming guide page 231
          
    def capture(self)->BaseWaveForm:
        """Capture: getting the waveform data from the oscilloscope. This is the Tektronix TDS2000 series 
        implementation. According to the information in the TDS programming manual on page 54, 86, this method 
        implements the following logic:
        2. Use the DATa:ENCdg command to specify the waveform data format.
        3. Use the DATa:WIDth command to specify the number of bytes per data point.
        4. Use the DATa:STARt and DATa:STOP commands to specify the part of the
        waveform that you want to transfer.
        5. Use the WFMPre? command to transfer waveform preamble information.
        6. Use the CURVe command to transfer waveform data.
        1. It sets this channel to be visible, preventing therefore an errormessage send by the scope.
        2. It sets this channel as being the source which has to be transferred by the scope to the computer. As
            the TDS programming manual states on page 86: 'Only one waveform can be transferred at a time.' 
        3. It sets the binary data format for transerring data.
        4. It sets the number of bytes per data point to 1. 
        5. It will query the preamble of this channel.
    ge    6. It will set the relevant data members of this channels waveformdata structure.
        7. It will query the scope for the data.
        8. When data has been transferred, this method will set the relevant datamembers of this channel's waveform
            struct. """
        
        #self.setVisible(True)
        self.setSource()
        #self.visaInstr.write(f"DATa:ENCdg RIBinary")
        #self.visaInstr.write(f"DATA:WIDTH 1")
        
        self.WFP.queryPreamble()
        wfp = self.WFP
        trace = self.WF
        wfp = self.WFP
        
        trace.setPreamble(wfp)
        #self.log.addToLog("start querying scope")
        #5-9-2025: when saving data in a file, comma's appears. Might be due transport format of Tektronix 
        bin_wave = self.visaInstr.query_binary_values('curve?\n', datatype='b', container=np.array)
        #bin_wave = bin_wave - trace.yoff
        self.log.addToLog("scope query ended")
        trace.rawYdata = bin_wave
        trace.rawXdata = np.linspace(0, wfp.nrOfSamples-1, num=int(wfp.nrOfSamples),endpoint=False)
        total_time = wfp.xincr * wfp.nrOfSamples
        tstop = wfp.xzero + total_time
        scaled_time = np.linspace( wfp.xzero, tstop, num=int(wfp.nrOfSamples))
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        # See programming manual, page 240, formulae below for calculatie y-values.
        temp = (unscaled_wave - trace.yoff) *  trace.ymult  + trace.yzero  
        #scaled_wave = (unscaled_wave - trace.yoff) *  trace.ymult  + trace.yzero 
        scaled_wave = np.array(temp)
        #put the data into internal 'struct'
        trace.scaledYdata = scaled_wave
        trace.scaledXdata = scaled_time
        return trace
        
    ##### DATA TRANSFER RELATED METHODS ######
    def getEncoding(self):
        """Gets the current encoding used by this scope."""
        return self.visaInstr.query("DATa:ENCdg?")
    
    def getWaveformPreamble(self):
        """Gets the description of the current waveform (i.e. preamble) of this channel."""
        #TODO add intern state for ascii or binary. Defines query or binary_query
        self.setSource()
        response = self.visaInstr.query('WFMPRE?')
        self.WFP.decode(response)

    ### BaseScope Measurements ##
    def getPkPk(self):
        """Calculates or finds the peak-to-peak maximum value in this channels last waveform. This TDS
        implementation use immed measurements to implement this functionality. TDS doesnot have a pk2pk method, therefore the
        min and max immed measurements will be used.
        """
        retval = None
        retval = super().getPkPk()
        if self.mode == "HW":
            maxVal = self.getMax()
            minVal = self.getMin()
            retval = maxVal - minVal

        return retval
    #### IMMED MEASUREMENT METHODS #####
    def getAvailableMeasurements(self):
        return TekChannel.IMMEDMEASTYPES
        
    def getImmedMeasParam(self):
        """Returns all immediate measurement setup parameters. Immediate queries
        and commands are the preferred methods for programming. An immediate
        measurement selection is not visible or accessible through the display screen
        or front panel."""
        response = self.visaInstr.query("MEASUrement:IMMed?")
        return response
    
    def immedMeasType(self):
        """Queries the immediate type of measurement configured for this TDS oscilloscope"""
        return str(self.visaInstr.query(f"MEASUREMENT:IMMED:TYPE?"))

    def immedMeasType(self, measType):
        """Sets the immediate type of measurement to be executed by this TDS oscilloscope.
        The parameter measType must be one of:
        CRMs        : calculate true Root Mean Square voltage of the first complete cycle in the
                        waveform
        CURSORRms   : Same as CRMs but between start and end point.
        DELay       : the delay from one waveform's edge event to another
        FALL        : is the fall time between 90% and 10% of the first falling edge of the waveform. 
                        Falling edge must be displayed to measure. The oscilloscope automatically 
                        calculates the 10% and 90% measurement points.
        FREQuency   : the reciprocal of the period measured in Hertz.
        MAXImum     : the value of the largest point in the waveform.
        MEAN        : the arithmetic mean over the entire waveform.
        MINImum     : the value of the smallest point in the waveform.
        NONe        : disables the measurement specified by <x>
        NWIdth      : the negative pulse width between the first falling edge and the next rising edge 
                        at the waveform 50% level. Falling and rising edges must be displayed to measure. 
                        The oscilloscope automatically calculates the 50% measurement point.
        PDUty       :
        PERIod      : the duration, in seconds, of the first complete cycle in the waveform.
        PHAse 
        PK2pk       : the absolute difference between the maximum and minimum amplitude.
        PWIdth      : the positive pulse width between the first rising edge and the next falling edge at
                        the waveform 50% level. Rising and falling edges must be displayed to measure. 
                        The oscilloscope automaticall0 calculates the 50% measurement point.
        RISe        : vthe rise time between 10% and 90% of the first rising edge of the waveform. Rising 
                        edge must be displayed to measure. The oscilloscope automatically calculates the 
                        10% and 90% measurement points.
        """
        for hulp in TekChannel.IMMEDMEASTYPES:
            if measType == hulp or measType == hulp.upper() or measType == hulp.lower():
                self.visaInstr.write(f"MEASUREMENT:IMMED:TYPE {measType}")        
            
    def doImmedMeas(self, measType):
        """Starts immediate measurements of a prior setted measurement type to be performed periodically by this
        TDS oscilloscope
        Remark: this method does not check ESR of events setted or fired, as noted by the programmers manual on 
        page 162: NOTE. If the channel specified by MEASUrement:IMMed:SOUrce is not currently
        displayed, the oscilloscope generates event 2225 and returns 9.9E37.
        If Trigger View is active, Scan mode is in effect, or the display format is set to XY,
        this query returns 9.9E37 and generates event 221 (Settings conflict)
        When math is FFT, turned on, and used as a measurement source, attempting to
        query the measurement value returns 9.9e37 and raises error 2225 (no waveform
        to measure)."""
        if not self.isVisible:
            self.setVisible(True) #preven event 2225
        #TODO: prevent event 221: check on a) Trigger View b) Scan mode or c) display mode is XY
        # Add a) Trigger view seems only settable through the front panel, see programming manual page 2-39:
        #   NOTE 1. While Trigger View is active (when you push the front-panel TRIG VIEW button), the 
        #       oscilloscope ignores the set form of most commands. If you send a command at this time, 
        #       the oscilloscope generates execution error 221 (Settings conflict).
        #   According to the TDS user manual, page 108:
        #       "TRIG VIEW Button. Use the Trigger View mode to have the oscillo-
        #           scope display the conditioned trigger signal. You can use this mode
        #           to see the following types of information: effects of the Trigger
        #           Coupling option, AC Line trigger source, and the signal connected to the EXT TRIG BNC.
        #               NOTE. This is the only button that you must hold down to use. When
        #               you hold down the TRIG VIEW button, the only other button you can
        #               use is the PRINT button. The oscilloscope disables all other
        #               front-panel buttons. The knobs continue to be active."
        #       The Trigger view state is not queryable by the Tigger State? command. The only way found in the manual to 
        #       check on this setting, is to send the  "CURSor:HBArs:UNIts? (Query Only)" Command, read page 2-63 for its 
        #       descriptions: 
        #               "UNKNOWN indicates that Trigger View is active. This also generates event message
        #                   221. (Settings conflict)"
        # Add b) One seems not be able to the TDS in scan mode, see programming manual, page 2-68:
        #               "In Scan Mode (Sec/div ≥100 ms and AUTO Mode), approximately one division
        #                   of data points will be invalid due to the blanked moving cursor."
        #         Also see page 2-198: "AUTO generates a trigger if a trigger is not detected within a specific 
        #           time period. AUTO also enables scan mode for sweep speeds of 100 ms/div and slower."
        #       So to prevent situation b) one must check 1) the timebase <100 ms and 2) Trigger mode is NOT AUTO.
        # Add c) to check on FFT mode, send the "Math?" command, see page 2-130
        #   To check on XY display mode, issue an "DISplay:FORMat?" Query.
        self.immedMeasType(measType)
        self.visaInstr.write(f"MEASUREMENT:IMMED:SOURCE {self.name}")
        return self.visaInstr.query("MEASUrement:IMMed:VALue?")
        
    def getMean(self):
        """Gets the arimethic mean of this channel's waveform by doing an Immediate Measurement"""
        immedResult = self.doImmedMeas("MEAN")        
        return float(immedResult)
    
    def getMax(self):
        """Gets the maximum value of highest point in this channel's waveform by doing an Immediate 
        Measurement"""
        immedResult = self.doImmedMeas("MAXImum")        
        return float(immedResult)
    
    def getMin(self):
        """Gets the maximum value of highest point in this channel's waveform by doing an Immediate 
        Measurement"""
        immedResult = self.doImmedMeas("MINImum")        
        return float(immedResult)
    
    def getNWidth(self):
        """Gets the maximum value of highest point in this channel's waveform by doing an Immediate 
        Measurement. It is the negative pulse width, between the first falling edge and the next rising 
        edge at the waveform 50% level. Falling and rising edges must be displayed to measure. 
        The oscilloscope automatically calculates the 50% measurement point."""
        immedResult = self.doImmedMeas("NWIdth")        
        return float(immedResult)
    
    
    def getPhaseTo(self, input: 'TekChannel'): #input is een channeltype of een MATH type.
        """Sets this channel of this Tektronix scope in performing a phase IMMED measurement, which is a feature avalaible only 
        on TBS1000B/EDU, TBS1000, TDS2000C, TDS1000C-EDU Series. The phase will be
        calculated according the fomulae: self.phase - input.phase.
        Remark on coding: the type of the input parameter has been written as 'TekChannel' and not
        TekChannel (without the qoutes). Reason is the inability of Python to use the type definition
        TekChannel as a formal parameter of a method, as this TekChannel class definition file has not 
        been ended yet. Therefore the class has not been defined yet and can't by used as a parameter. 
        As described in PEP484, expressing an (temporary) unresolved name as a string literator is 
        the way to go, by the assumption it will be resolved later.
        Precondition: 
        1. the mode of this channel (self.mode) equals to 'HW', as this is an measurement done by hardware, 
        i.e. a TDS2002C scope.
        2. All supplied signals to the scope have same shape and frequency. If not, the behaviour of Tektronix scope is unknown, 
        as it is not specified
        TODO: the 'SW' version of this methodk, need an estimated of the frequency of the signals. This need could be circumventend
        when a method to estimate frequency based on acquired waveform is available
        """
        if self.mode == 'HW':
            #TODO: check if scope is able to perform the measurement.
            self.immedMeasType("PHAse")
            myinput: TekChannel = input
            self.visaInstr.write(f"MEASUREMENT:IMMED:SOURCE {self.name}")
            self.visaInstr.write(f"MEASUREMENT:IMMED:SOURCE2 {myinput.name}")
            return self.visaInstr.query("MEASUrement:IMMed:VALue?")
        else:
            return None
        
    def getPhaseTo(self, input:'BaseChannel', freqEstimate=1000):
        """Performs a phase measurement with respect to the input. This method is an overridden variant of getPhase to and is
        fully implementend in software. Therefore, this method should be used if a scope has no features on board for measurering phase,
         or when the scope is to slow, which is the case with the TDS2002C."""
        phEstimate = super().getPhaseTo(self, input, freqEstimate)
        return phEstimate

    def getFrequency(self):
        """Gets the frequency [Hz] of this channel's waveform by doing an Immediate 
        Measurement"""
        immedResult = self.doImmedMeas("FREQuency")        
        return float(immedResult)
    
    def getPeriod(self):
        """Gets the period time [s] of this channel's waveform by doing an Immediate 
        Measurement"""
        immedResult = self.doImmedMeas("PERIod")        
        return float(immedResult)
    
    def getDuty(self):
        """Gets the positive duty cycle of this channel's waveform by doing an Immediate 
        Measurement"""    
        immedResult = self.doImmedMeas("PDUty")        
        return float(immedResult)
    
    ######### Periodic measurements control #####
    def clearMeas(self):
        """Clears all previously setted periode measurements"""
        self.perMeasDict.clear()

    def addMeas(self, measType):
        """Adds a periodic Measurement to the current set. Maximum of 5 measurements allowed.
        returns True if measurement added of
        False if measurement was not added (full)"""
        index = len(self.perMeasDict)
        currIndexStr = str(index+1)
        if measType in TekChannel.IMMEDMEASTYPES and index < 6:
            self.perMeasDict[currIndexStr]={self.name : measType}
            print(f"MEASUrement:MEAS{currIndexStr}:TYPe {measType}")
            print(f"MEASUrement:MEAS{currIndexStr}:VALue?")
            self.visaInstr.write(f"MEASUrement:MEAS{currIndexStr}:SOUrce {self.name}\n")
            self.visaInstr.write(f"MEASUrement:MEAS{currIndexStr}:TYPe {measType}\n")
            print(self.visaInstr.query("*ESR?\n"))
            print(self.visaInstr.query("ALLEv?\n"))
            time.sleep(1)
            self.visaInstr.write(f"MEASUrement:MEAS{currIndexStr}:VALue?\n")
            time.sleep(1)
            print(self.visaInstr.query("*ESR?\n"))
            print(self.visaInstr.query("ALLEv?\n"))
            return True
        else:
            return False

    def getAvMeasVals(self):
        """"Queries all values of previously set measurement. Values will be returned in a key,value dict"""
        pass

    def set2_80(self, val):
        """Sets the vertical sensitivity of this channel to 80% of value val, in order to make 
        better use of available bits.
        This method sets this channel such val corresponds to 80% of the visible max value on screen.
         assuming zero offset.  """
        newVdiv = val/(0.5 * self.visibleVertDivs)
        self.setVdiv(newVdiv)
        # validate newVdiv 
        # write value.

    def set2FS(self, minVal, maxVal):
        """Set the  'vertical gain'of this channel to maximize the signal on screen (min. 80% of full screen). Goal: better use of 
        the 8 bits digitalisation (ADC).
        Input: min en max value of the signal itself. Not the min/max position on screen.
        Preconditions: 
        1. waveform is centered vertically on screen, so 'position' is 0 divs.
        2. The parameters 'minVal' and 'maxVal' were acquired during:
            a. A non-clipping situation, i.e. the signal was fully displayed, vertically as horizontally. 
            Preferably, this signal was acquired have been accHet signaal is volledig zichtbaar op scherm of anders het signaal zit binnen +/- 5 divs.
        #   
        #   3. AC of DC coupling? Vermoeden dat dit er niet toe doet voor deze functie.
        # a. bereken gem. waarde = offset signaal. (Dus niet de momentele schermpositie, het gaat om het signaal zelf)
        # b. 
        # """
        pass


    

    ##################################################################################################
    
class TekWaveFormPreamble(BaseWaveFormPreample):
    """Class for holding the Tektronix TDS1000 scope series preamble. Extends BaseWaveFormPreamble.
    A preample is data describing the unit, range and spacing of a Waveform."""

    @classmethod
    def getWaveFormPreambleClass(cls, dev):
        """ Tries to get (instantiate) the right instance based on the type"""
        if cls is TekWaveFormPreamble:
            return cls
        else:
            return None      

    def __init__(self, dev:pyvisa.resources.MessageBasedResource=None):
        """TekWaveFormPreamble init. Inits all datamembers to the value None.
        Following data members are set:
        self.nrOfBytePerTransfer   : Number of bytes per sample or in total => check!
        self.nrOfBitsPerTransfer   : Number of bits per sample or in total => check!
        self.encodingFormatStr     : Encoding sting used during transfer, see documentation
        self.binEncodingFormatStr  : Encoding used during transfer, binary, see documentation
        self.binFirstByteStr       : Location of first byte(? Checken!), see documentation
        self.nrOfSamples           : number of samples of acquired waveform
        self.vertMode              : Indicaties YT,XY, or FFT mode
        self.xincr                 : Time between two samples
        self.xzero                 : Location of X=0 on screen horizontally
        self.xUnitStr              : Horizontal axis unit
        self.ymult                 : Vertical gain, or VDIV
        self.yzero                 : Is a value, expressed in YUNits, used to convert waveform record
                                     values to YUNitLocation of Y=0 on screen vertically
        self.yoff                  : Vertical offset in digitizer levels
        self.yUnitStr              : Vertical axis unit
        self.couplingstr           : "AC", "DC" or "GND"
        self.timeDiv               : Amount of time of one horizontal division on screen. Also called 'Timebase' 
        self.acqModeStr            : The sampling system of an oscilloscope has greater range than the horizontal scale. Therefore a scope is capable to take multiple
                                            samples for an acquisition interval. Typical Acquisition modes are 'sample mode', 'peak mode', or 'average(ing)' 
        self.sourceChanStr         : A string indicating the channel of this waveformpreamble, e.g. 'C1' or 'CH1', depending on scope brand or type.
        self.vdiv                  : the amount of vertical displacement per division of the screen.
            
        
        """
        super().__init__(dev=dev)
        
        
    def decode(self, strToDecode):
        paramlist = strToDecode.split(';')

        self.nrOfBytePerTransfer    = int(paramlist[0])
        self.nrOfBitsPerTransfer    = int(paramlist[1])
        self.encodingFormatStr      = str(paramlist[2])
        self.binEncodingFormatStr   = str(paramlist[3])
        self.binFirstByteStr        = str(paramlist[4])
        self.nrOfSamples            = int(paramlist[5])
        self.vertMode               = str(paramlist[7])
        self.xincr                  = float(paramlist[8])
        self.xzero                  = float(paramlist[10])
        self.xUnitStr               = str(paramlist[11])
        self.ymult                  = float(paramlist[12])
        self.yzero                  = float(paramlist[13])
        self.yoff                   = float(paramlist[14])
        self.yUnitStr               = str(paramlist[15])
        self.decodeChanPreamble(paramlist[6])
        
    def queryPreamble(self):
        """Method for getting the preamble of the scope and set the correct data members
        of this preamble"""
        response = self.visaInstr.query("WFMPRE?")
        self.decode(response)
    
    def decodeChanPreamble(self, chanStrToDecode):
        """Method for decoding the query data of the scope and set the correct data members
        of this preamble"""
        #6th element in channellist of TDS
        channelParamList = chanStrToDecode.strip('"')
        channelParamList=channelParamList.strip("'")
        channelParamList=channelParamList.split(',')
        self.sourceChanStr = str(channelParamList[0])
        hulp = (channelParamList[1].strip()).split()
        self.couplingstr = str(hulp[0])
        hulp = (channelParamList[2].strip()).split()
        self.vdiv  = float(hulp[0])
        hulp = (channelParamList[3].strip()).split()
        self.timeDiv = float(hulp[0])
        hulp = (channelParamList[4].strip()).split()
        self.nrOfSamples = float(hulp[0])
        hulp = (channelParamList[5].strip())
        self.acqModeStr = str(hulp)

class TekWaveForm(BaseWaveForm):

    @classmethod
    def getWaveFormClass(cls):
        """ Tries to get (instantiate) the right instance based on the type"""
        if cls is TekWaveForm:
            return cls
        else:
            return None      
        
    def __init__(self):
        ####TEKTRONIX TDS SPECIFIC WAVEFORM PARAMS ########
        super().__init__()
        
        
    def setPreamble(self, wfp: TekWaveFormPreamble):
        self.chanstr        = wfp.sourceChanStr
        self.couplingstr    = wfp.couplingstr
        self.timeDiv        = wfp.timeDiv
        self.vDiv           = wfp.vdiv
        self.xzero          = wfp.xzero
        self.xUnitStr       = wfp.xUnitStr
        self.xincr          = wfp.xincr
        self.nrOfSamples    = wfp.nrOfSamples
        self.yzero          = wfp.yzero
        self.yoff           = wfp.yoff
        self.ymult          = wfp.ymult
        self.yUnitStr       = wfp.yUnitStr
         
    def dump(self):
        line = f"self.rawYdata    = {self.rawXdata}\n"
        line += f"self.rawYdata    = {self.rawYdata}"
        print(line)