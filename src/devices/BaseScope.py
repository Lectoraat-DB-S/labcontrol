import pyvisa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import configparser
import os
import socket

from devices.BaseConfig import LabcontrolConfig, BaseScopeConfig

class BaseScope(object):
    """BaseScope: base class for oscilloscope implementation.
        Implementations for oscilloscopes have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getScopeClass.
        3. Be sure BaseScope's constructor has access to the inheriting subclasses during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        4. Instantion must be done by calling the getDevice method. This method implements a factory kind of scheme. 
    """
    scopeList = []        
    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseScope subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.scopeList.append(cls)
         
    @classmethod
    def getScopeClass(cls, rm, urls, host=None, scopeConfigs: list = None):
        """Method for getting the right type of scope, so it can be created by the runtime.
        This Basescope implementation does nothing other the return the BaseScope type. The inheriting
        subclass should implement the needed logic"""
        pass
    
    @classmethod
    def getDevice(cls,host=None):
        """Method for handling the creation of the correct Scope object, by implementing a factory process. 
        Firstly, this method calls getScopeClass() for getting the right BaseScope derived type. If succesfull, this 
        method, secondly, returns this (class)type together with the needed parameters, to enable
        the Python runtime to create and initialise the object correctly.
        DON'T TRY TO CALL THE CONSTRUCTOR OF THIS CLASS DIRECTLY"""
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()
        myconfigs = LabcontrolConfig().find(cls) # myconfig is a list of config 

        for scope in cls.scopeList:
            scopetype, dev, theConfig = scope.getScopeClass(rm, urls, host, myconfigs)
            if scopetype != None:
                cls = scopetype
                return cls(dev, theConfig)
            
        return None # if getDevice can't find an instrument, return None.

    @classmethod
    def SocketConnect(cls, rm:pyvisa.ResourceManager = None, scopeConfig: BaseScopeConfig = None,
                timeOut = 10000, readTerm = '\n', writeTerm = '\n')->pyvisa.resources.MessageBasedResource:
        myConfig: BaseScopeConfig = scopeConfig
        if rm == None:
            return None
        
        if scopeConfig == None:
            return None
        else:
            host = myConfig.IPAddress #property
            mydev: pyvisa.resources.MessageBasedResource = None
            if host == None:
                return None
            try:
                #logger.info(f"Trying to resolve host {host}")
                ip_addr = socket.gethostbyname(host)
                mydev = rm.open_resource("TCPIP::"+str(ip_addr)+"::INSTR")
            except (socket.gaierror, pyvisa.VisaIOError) as error:
                #logger.error(f"Couldn't resolve host {host}")
                return None
            
            mydev = rm.open_resource("TCPIP::"+str(ip_addr)+"::INSTR")
            mydev.timeout = timeOut  # ms
            mydev.read_termination = readTerm
            mydev.write_termination = writeTerm
            return mydev
        #No return needed here. Every path within function returns None or resource.

    @classmethod
    def getModel(cls, devStr:str):
        """
        Function to extract/decode the modelno or model id from an indentification string. Is device specific, therefore 
        this implementation is empty."""
        return None
    
    
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource=None, scopeConfig: BaseScopeConfig = None):
        """This method takes care of the intialisation of a BaseScope object. This implementation leaves most
        datamembers uninitialised. A subclass should therefore override this function and initialise the datamembers. 
        Remark: don't forget to call super().__init()__ if needed!"""
        self.brand = None
        self.model = None
        self.serial = None
        self.firmware = None
        self.visaInstr : pyvisa.resources.MessageBasedResource = visaInstr
        self.horizontal : BaseHorizontal = None
        self.vertical : BaseVertical = None
        self.trigger : BaseTriggerUnit = None
        self.display : BaseDisplay = None
        self.acquisition : BaseAcquisition = None
        self.utility = None
        self.host = None
        
        self.nrOfHoriDivs = None# maximum number of divs horizontally
        self.nrOfVertDivs = None # maximum number of divs vertically 
        self.visibleHoriDivs = None# number of visible divs on screen
        self.visibleVertDivs = None # number of visible divs on screen
        

        #self.nrOfHoriDivs = scopeConfig.horizontalGrid # maximum number of divs horizontally
        #self.nrOfVertDivs = scopeConfig.verticalGrid # maximum number of divs vertically 
        #self.visibleHoriDivs = scopeConfig.visibleHorizontalGrid # number of visible divs on screen
        #self.visibleVertDivs = scopeConfig.visibleVerticalGrid # number of visible divs on screen
        self.mode = "SW"  #default setting for the data processing, when doing measurements with this scope.
        self._scopeConfig = scopeConfig

    
    #@property 
    def visaInstr(self) -> pyvisa.resources.MessageBasedResource: 
        """Method for getting the reference to this objects VISA resource. 
        The reference to a visaInstrument object will be set by init only. 
        Please don't alter this method or override it when deriving this class.
        """
        return self.visaInstr
    
    def acquire(self):
        pass
    
    def acquire(self, state, mode=None, nrOfAvg=None, stopAfter=None):
        pass

    def setProcMode(self, mode):
        """Sets the processing or measurement mode of this channel to "SW" or "HW". When set to "SW", every subsequent measurement
        request made by this scope or it sibling object will be done in software. 
        When set "HW", the request will be done by the oscilloscope (the hardware). If the actual connected scope doesn't not offer 
        the measurement function requested, the operation will be done in software, to maintain functional consistency for every scopes.
        """
        if mode == "SW" or mode == "HW":
            self.mode = mode    
            self.vertical.setProcMode(self.mode)
    
###################################### BASECHANNEL #########################################################
class BaseChannel(object):
    """BaseChannel: a baseclass for the abstraction of a channel of an oscilloscope.
    All channel implementation have to inherit from this baseclass.
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO fully implement the getChannelClass method of this class.
    3. Be sure this BaseChannel implementation has access to all inheriting subclasses during creation. If not, 
    the subclass won't be registered and creating the needed channel object(s) will fail."""

    channelList = []

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseChannel subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.channelList.append(cls)
    
    @classmethod
    def getChannelClass(cls, dev):
        """getChannelClass: factory method for scope channel objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass


    def __init__(self, chan_no: int, visaInstr:pyvisa.resources.MessageBasedResource):
        """Method voor initialising this Channel object.
        Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr = visaInstr
        self.chanNr = chan_no
        self.name = None
        self.WF = BaseWaveForm()            # the waveform ojbect of this channel
        self.WFP = BaseWaveFormPreample(visaInstr) # the waveformpreamble object for this channel
        self.mode = "SW" # measurements, pkpk for instance, will be performed in software. Set to "HW" when using scope functions 

    def query(self, cmdString):
        return self.visaInstr.query(cmdString)
    
    def write(self, cmdString: str):
        return self.visaInstr.write(cmdString) #returns number of bytes written.

    def writeRaw(self, cmdString:str):
        bytesToWrite = cmdString.encode()
        return self.visaInstr.write_raw(bytesToWrite) #returns the number of bytes written.

    def readRaw(self, nrOfBytes): # nrOfBytes defaults to None, meaning the resource wide set value is set.
        return self.visaInstr.read_raw(size=nrOfBytes)

    def getWaveformPreamble(self):
        """Gets the description of the current waveform (i.e. preamble) of this channel. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method by sending the proper SCPI commands."""
        pass 

    def setCoupling(self, coupling):
        pass

    def getCoupling(self):
        pass
    
    def setVisible(self, state:bool):
        pass

    def isVisible(self):
        pass

    def setProcMode(self, mode = "SW"):
        if mode == "SW" or mode == "HW":
            self.mode = mode
    
    def probe(self, factor):
        pass

    #def probe(self):
    #    pass

    def setProcMode(self, mode):
        """Sets the processing or measurement mode of this channel to "SW" or "HW". When set to "SW", every subsequent measurement request
        will be done in software. When set "HW", the request will be done by the oscilloscope (the hardware). If the scope 
        connect doesn't not offer the measurement requested, the operation will be done in software on the host computer"""
        if mode == "SW" or mode == "HW":
            self.mode = mode    
        
    def capture(self)->'BaseWaveForm':
        """Gets the waveform from the oscilloscope, by initiating a new aqquisition. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method by sending the proper SCPI commands 
        in order to: a. set this channel object as the source for the capture b. get waveform descriptors, c. get the 
        raw data and e. take care for converting the raw data to meaningfull physical quantities and handel the storage 
        it."""
        pass

    def setVdiv(self, value):
        """Sets the vertical sensitivity (i.e. Vdiv) of this channel. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        pass

    def getVdiv(self):
        """Gets the current vertical sensitivity (i.e. Vdiv) of this channel. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        pass

    def position(self):
        """Gets the (vertical) position of this channel with respect to the center graticule. Unit of position is divisions (divs)."""
        pass

    def position(self, pos):
        """"Sets the (vertical) position of this channel with respect to center. Parameter pos is the deviation from center in divisions (divs). 
        A positive value means above center, negative means below center. """
        pass


    def getXzero(self):
        """Gets the vertical offset of this channel on display. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        pass


    def getAvailableMeasurements(self):
        """Gets the available measurements of this oscilloscope. 'Measurements' are build-in, predefined data processing
        functions. Functionality depends on capabilities of a scope. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        pass
    
    def getMean(self):
        """Calculates the mean of the samples of this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality, but, if not present for the 
        scope instance used, by a software implementation of the derived class.
        """
        pass

    def getMax(self):
        """Calculates or finds the maximum value in this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality, but, if not present for the 
        scope instance used, by a software implementation of the derived class.
        """
        pass

    def getMin(self):
        """Calculates or finds the minimal value in this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality, but, if not present for the 
        scope instance used, by a software implementation of the derived class.
        """
        pass

    def getPkPk(self):
        """Calculates or finds the peak-to-peak maximum value in this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality, but, if not present for the 
        scope instance used, by a software implementation of the derived class.
        """
        if self.mode == "SW":
            maxVal = max(self.WF.scaledYdata)
            minVal = min(self.WF.scaledYdata)
            return maxVal-minVal

    def getPhaseTo(self, input):
        """Calculates the phase difference of this channels last waveform with respect to the input parameter. The
        phase should be calculated by: self.phase - input.phase. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality of the physical scope, but, 
        if not present, by a software implementation of the derived class.
        """
        pass

    def getPhaseTo(self, input:'BaseChannel', freqEstimate=1000):
        if self.mode == 'SW':
            phShift = self.calcPhaseShiftTo(input, freq=freqEstimate)
            return phShift
        else:
            return None
        

    def getFrequency(self):
        """Calculates the frequency of this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality of the physical scope, but, 
        if not present, by a software implementation of the derived class.
        """
        pass
    
    def getPeriod(self):
        """Measures the time needed for a full periode of this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality of the physical scope, but, 
        if not present, by a software implementation of the derived class.
        """
        pass

    def configPlot(self, plot: plt):
        """Method for configuring Matplotlib plots, based on the channels preamble data capture. This method
        implements the following base functionality:
        1. Setting x and y axes ranges.
        2. Setting x and y axes units
        3. Setting linear, logplot or loglogplot.
        4. Setting a base title for the plot.
        5. ....?.....
        Pre-condition: 1. waveform captured on this channel (at least once). 2. Matlibplot plot instance created   
        Input parameter : plot. A valid Matplotlib plot handle to be configured.
        Return: a configured plot handle. Plot data has to be supplied and show() to be called."""
        pass
        
    def getConfigPlot(self):
        """Method for getting a configured Matplotlib plot, based on the channels preamble data capture. This method
        implements the following base functionality:
        1. Creating a Matplotlib.pyplot instance
        2. Setting x and y axes ranges.
        3. Setting x and y axes units
        4. Setting linear, logplot or loglogplot.
        5. Setting a base title for the plot.
        6. ....?.....
        Pre-condition: 1. waveform captured on this channel (at least once).    
        Input parameter : None.
        Return: a created and configured plot handle, invisible with no data in it."""
        pass

    def getPlot(self):
        """Method for getting a completely configured plot. This method has the same functionality as getConfigPlot, but 
        this method actually plots the data, based on the current WaveForm of this channel.
        Precondition: waveform available
        Input parameter: None
        return: handle to matplotlib object."""
        pass 

    def clearMeas(self):
        pass

    def addMeas(self, measType):
        pass

    def getAvMeasVals(self):
        pass

    def set2_80(self, val):
        pass

    def findAllZC(self):
        if self.mode == 'SW':
            trace = self.WF
            ysamp = np.array(trace.scaledYdata)
            
            # to find the first zero crossing, one need the offset
            
            offset = np.mean(ysamp)
            positive = ysamp > offset
            idx = np.where(np.bitwise_xor(positive[1:], positive[:-1]))[0]
            return idx
        else:
            return None
        
    def calcPhaseShiftTo(self, input: 'BaseChannel', freq): #input is een channeltype of een MATH type.
        # calcPhaseShiftTo(self, input: 'BaseChannel', targetFreq)
        # 1. get idx of zcd of this channel
        mytdata = np.array(self.WF.scaledXdata)
        inptdata = np.array(input.WF.scaledXdata)
        myIdx = self.findAllZC()
        inputIdx = input.findAllZC()
        myZCtdata = mytdata[myIdx]
        inpZCtdata = inptdata[inputIdx]
        
        bool_mask = myZCtdata >= inpZCtdata[0]
        myZCtdata = myZCtdata[bool_mask][0]
        diff =  myZCtdata-inpZCtdata[0]

        return diff*freq*360.0
        
        # 2. get idx of zcd of the input channel
        # 3. As we want to know the phase to the input, the idx value of the input channel must be smaller 
        # than the idx of the zero crossing of this channel.


    def findFirstZC(self):
        pass

########## BASEVERTICAL ###########
    
class BaseVertical(object):
    """BaseVertical is a baseclass implementation of the vertical functionality of a scope.
    A Vertical of a real oscilloscope have to inherit from this class
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO implement the getVerticalClass method of this class
    3. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
    subclass will not be registated and the correct supply object won't be instantiated. 
    """
    VerticalList = list()
   
    @classmethod
    def getVerticalClass(cls, dev):
        """getVerticalClass: factory method for getting the right vertical type of an oscilloscope. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass 

    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseVertical subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.VerticalList.append(cls)

  
    def __init__(self, nrOfChan: int = 0, dev:pyvisa.resources.MessageBasedResource = None):
        """This method takes care of the intialisation of a BaseVertical object. Subclass must override this 
        method ,by initialising the datamembers needed. Remark: if the subclass relies on the intialisation done 
        below, don't forget to call super().__init()__ !"""
        self.channels = []          
        self.nrOfChan = nrOfChan       # A virtual Baseclass: so no channels available.
        self.visaInstr = dev             # default value = None, see param
        self.mode = "SW"
    
    #def chan(self, chanNr:int):          
    #def chan(self, chanNr)->BaseChannel: 
    #    """Get the channel object based on the number. This method should be overridden by the 
    #    inherting subclass, as this BaseVertical implementation is empty."""
    #    return None
    
    def chan(self, chanNr)->BaseChannel: 
        """Gets a channel, based on its index: 1, 2 etc."""
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None     
    

    def setProcMode(self, mode):
        """Sets the processing or measurement mode of this channel to "SW" or "HW". When set to "SW", every subsequent measurement request
        will be done in software. When set "HW", the request will be done by the oscilloscope (the hardware). If the scope 
        connect doesn't not offer the measurement requested, the operation will be done in software on the host computer"""
        if mode == "SW" or mode == "HW":
            self.mode = mode
            for  i in range(self.nrOfChan):
                chan:BaseChannel  = self.chan(i+1)
                chan.setProcMode(mode)

                
############ BaseHorizontal ###########
class BaseHorizontal(object):
    """BaseHorizontal: baseclass implementation of a scope horizontal functionality.
    Implementation of real supplies have to inherit from this class:
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO implement the getHorizontalClass method of this class
    3. Give BaseHorizontal's constructor access to all inheriting subclasses during its instantion. If not, 
    registration of the subclass will fail, which prevents creation of needed Horizontal type kind of object."""
    
    HorizontalList = list()

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseHorizontal subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.HorizontalList.append(cls)
    
    @classmethod
    def getHorizontalClass(cls, dev):
        """getHorizontalClass: a factory method for getting the right horziontal type of an oscilloscope. 
        Remark: this baseclass implementation is empty, all logic must be implemented by the subclass. """
        pass
        
          
    def __init__(self, dev:pyvisa.resources.MessageBasedResource= None):
        """This method takes care of the intialisation of a BaseHorizontal object. Subclasses must override this 
        method ,by initialising the datamembers needed. Remark: if the subclass relies on the intialisation done 
        below, don't forget to call super().__init()__ !"""
        self.visaInstr = dev             # default value = None, see param
        self.TB = 0.0                  # current value of timebase, unit sec/div
        self.SR = 0                    # samplerate
        self.POS = 0                   # Horizontal position in screen (of the waveforms)
        self.ZOOM = 0                  # Horizontal magnifying.

    def setRoll(self, flag:bool):
        """Method for setting horizontal roll (true/false). This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass       
    
    def getTimeDivs(self):
        """Method for getting available timebase setting. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""    
        pass

    def setTimeDiv(self, value):
        """Method for setting a timebase vaule. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""    
        pass

            
###################################### BASECWAVEFORMPREAMBLE ###################################################
class BaseWaveFormPreample(object):
    """BaseWaveFormPreambel: a base class for holding a channels waveform Preambel data.
    Implementation of real scopes have to subclass their waveform implementations from this class. Reason for
    doing so:
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
    @classmethod 
    def getWaveFormPreableObject(cls, dev):
    3. Be sure BasewaveForm's constructor has access to the inheriting subclass during instantion. If not, the
    subclass will not be registated and the correct supply object won't be instantiated. 
    """
    WaveFormPreambleList = list()

    @classmethod
    def getWaveFormPreableClass(cls, dev:pyvisa.resources.MessageBasedResource=None):
        pass

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseWaveFormPreamble subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.WaveFormPreambleList.append(cls)
    

    def __init__(self, dev:pyvisa.resources.MessageBasedResource=None):
        self.visaInstr = dev
        """The preamble here is originally the TekWaveFormPreamble init. This method inits all datamembers to the value None.
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
        
        self.tdiv                   = None # same as timeDiv => checken!!!
     
        self.nrOfBytePerTransfer    = None #Number of bytes per sample or in total => check!
        self.nrOfBitsPerTransfer    = None #Number of bits per sample or in total => check!
        self.encodingFormatStr      = None #Encoding sting used during transfer, see documentation
        self.binEncodingFormatStr   = None #Encoding used during transfer, binary, see documentation
        self.binFirstByteStr        = None #Location of first byte(? Checken!), see documentation
        self.nrOfSamples            = None #number of samples of acquired waveform
        self.vertMode               = None #Y, XY, or FFT.
        self.xincr                  = None #Time between two samples
        self.xzero                  = None #Location of X=0 on screen horizontally
        self.xUnitStr               = None #Horizontal axis unit
        self.ymult                  = None #Vertical gain, or VDIV
        self.yzero                  = None #Is a value, expressed in YUNits, used to convert waveform record
                                              #  values to YUNitLocation of Y=0 on screen vertically
        self.yoff                   = None #Vertical offset in digitizer levels
        self.yUnitStr               = None #Vertical axis unit
        self.couplingstr            = None #"AC", "DC" or "GND"
        self.timeDiv                = None #Amount of time of one horizontal division on screen. Also called 'Timebase' 
        self.acqModeStr             = None #The sampling system of an oscilloscope has greater range than the horizontal scale. Therefore a scope is capable to take multiple
                                            #samples for an acquisition interval. Typical Acquisition modes are 'sample mode', 'peak mode', or 'average(ing)' 
        self.sourceChanStr          = None #A string indicating the channel of this waveformpreamble, e.g. 'C1' or 'CH1', depending on scope brand or type.
        self.vdiv                   = None #the amount of vertical displacement per division of the screen.
        self.probe                  = None #the probe (attenuation) factor, e.g. 0.1x , 1x or 1000x
        self.bwLimit                = None #Indicites the bw of the scope due to (additional) filtering
        self.recordType             = None #Indicates the semantical content of the waveform acquired. Viable options are: 'SingleSweep, Spectrum, Histogram'. It's not
                                            # a critical parameter, it just add some more info about the meaning of possible purpose of this data.(Siglent)
        self.processing             = None #Indicates pre or post signalprocessing, such as fir, interpolation etc. (Siglent) 


    def toString(self):
        #https://flexiple.com/python/print-object-attributes-python
        """
        vars() maakt een dict (of iets wat er op lijkt type(vars) is een of ander proxyding ) van alle datamembers en alle 
        functies van een object. Het is een van de built-in introspectie functies van Python. 
        De functies van het object beginnen met 2 underscores, dus moet je alle keys van de dict waar een twee underscores 
        achter elkaar in staan, eruit gooien. De waardes in de datamembers kun je opvragen met vars()[key]
        """
        resStr = ""
        dundrscr = "__"
        dictOfWFP = vars(self)
        for member in dictOfWFP:
            if dundrscr not in member:
                memVal = dictOfWFP[member]
                resStr += f"{member},\t{memVal}`n"
        return resStr
    
    def toString(self, otherWFP: 'BaseWaveFormPreample'):
        """Method to convert this WaveFormPreample and the otherWPF to a string representatie, which can be saved to disk or
        might be send by a stream."""
        #TODO: check which WFP is chan1 and check if both WFP has same elements.
        resStr = ""
        dundrscr = "__"
        dictOfWFP1 = vars(self)
        dictofWFP2 = vars(otherWFP)
        for member in dictOfWFP1:
            if dundrscr not in member:
                resStr += f"{member},\t{dictOfWFP1[member]},\t{member},\t{dictofWFP2[member]}.\n"
        return resStr
    
    def queryPreamble(self):
        """Method for getting the preamble of the scope and set the correct data members
        of a preamble. This baseclass has no implementation."""
        pass
        
######################################## BASEWAVEFORM #########################################################
class BaseWaveForm(object):
    """BaseWaveForm: a base class for holding a channels waveform data.
    Implementation of real scopes have to subclass their waveform implementations from this class. Reason for
    doing so:
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO implement the getWaveFormClass method of this class.
    3. Be sure BasewaveForm's constructor has access to the inheriting subclass during instantion. If not, 
    registration of the subclass will fail and the correct supply object won't be instantiated. 
    """
    
    WaveFormList = list()

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseWaveForm subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.WaveFormList.append(cls)

    @classmethod
    def getWaveFormClass(cls):
        pass
        
    def __init__(self):
        """Class for holding waveform data of a channel capture and the methods to transform raw sample data into soming fysical meaningful, such as voltage."""
        self.rawYdata       = None #data without any conversion or scaling taken from scope
        self.rawXdata       = None #just an integer array
        self.scaledYdata    = None #data converted to correct scale e.g units
        self.scaledXdata    = None #An integer array representing the fysical instants of the scaledYData.
        #Horizontal data settings of scope
        self.chanstr        = None
        self.couplingstr    = None
        self.timeDiv        = None # see TDS prog.guide table2-17: (horizontal)scale = (horizontal) secdev 
        self.vDiv           = None # probably the same as Ymult.
        self.xzero          = None # Horizontal Position value. Definition: xzero = 0 => horizontal center of screen.
        self.xUnitStr       = None # unit of X-as/xdata
        self.xincr          = None # multiplier for scaling time data, time between two sample points.
        self.nrOfSamples    = None # the number of points of trace.
        self.yzero          = None 
        self.ymult          = None # vertical step scaling factor. Needed to translate binary value of sample to real stuff.
        self.yoff           = None # vertical offset in V for calculating voltage
        self.yUnitStr       = None
    
    def setWaveForm(self, wfp: BaseWaveFormPreample):
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
    
    def toString(self):
        #https://flexiple.com/python/print-object-attributes-python
        """
        vars() maakt een dict (of iets wat er op lijkt type(vars) is een of ander proxyding ) van alle datamembers en alle 
        functies van een object. Het is een van de built-in introspectie functies van Python. 
        De functies van het object beginnen met 2 underscores, dus moet je alle keys van de dict waar een twee underscores 
        achter elkaar in staan, eruit gooien. De waardes in de datamembers kun je opvragen met vars()[key]
        """
        resStr = ""
        dundrscr = "__"
        dictOfWFP = vars(self)
        for member in dictOfWFP:
            if dundrscr not in member:
                memVal = dictOfWFP[member]
                resStr += f"{member},\t{memVal}\n"
        return resStr
    
    def toDict(self):
        """ chan1Settings = {
        chan1Settings : {"xzero":0}
        }"""
        resStr = ""
        dundrscr = "__"
        dictOfWFP = vars(self)
        myWFSettingsDict = dict()
        for member in dictOfWFP:
            if dundrscr not in member:
                memVal = dictOfWFP[member]
                addDict = dict(member, memVal)
                myWFSettingsDict.update(addDict)
        return myWFSettingsDict
    
    def toDF(self):
        dundrscr = "__"
        dictOfWFP = vars(self)
        myWFSettingsDict = dict()
        for member in dictOfWFP:
            if dundrscr not in member:
                addDict = dict(member, dictOfWFP[member])
                myWFSettingsDict.update(addDict)
        df = pd.DataFrame(myWFSettingsDict)
        return df

    def preamble2DF(self, otherWFP: BaseWaveFormPreample):
        dundrscr = "__"
        dictOfWFP1 = vars(self)
        dictOfWFP2 = vars(otherWFP)
        valList = list()
        myWFSettingsDict = dict()
        for member in dictOfWFP1:
            valList.clear()
            if dundrscr not in member:
                valList.append(dictOfWFP1[member])
                valList.append(dictOfWFP2[member])
                addDict = dict(member, valList)
                myWFSettingsDict.update(addDict)
        df = pd.DataFrame(myWFSettingsDict)
        return df
    
    def toSeries(self, select = "raw"):
        """Converts the samples of this waveform to a Pandas Series object.
        A Series object is a one dimensional np.ndarray, which integrates very nicely within Pandas.
        Parameter select: "raw" (default) or "scaled". 
         raw = only sample sequence numbers and unconverted sample data
         scaled = converted sample data, according the content of the companion WFP. """
        # conversion below should be unnecessary
        xraw = np.array(self.rawXdata)
        yraw = np.array(self.rawYdata)
        scaledx = np.array(self.scaledXdata)
        scaledy = np.array(self.scaledYdata)
        ser = None
        if select == "raw":
            ser = pd.Series(data=self.rawYdata, index=self.rawXdata)
        else:
            ser = pd.Series(data=self.scaledYdata, index=self.scaledXdata)
        
        return ser
    
    def data2DF(self):
        columnNames = ["xraw", "yraw", "xscaled", "yscaled"]
        # conversion below should be unnecessary
        xraw = np.array(self.rawXdata)
        yraw = np.array(self.rawYdata)
        scaledx = np.array(self.scaledXdata)
        scaledy = np.array(self.scaledYdata)
        df = pd.DataFrame(xraw, yraw, scaledx, scaledy, columns=columnNames)
        return df
    
    def WF2DF(self):
        frames = [self.preamble2DF, self.data2DF]
        result = pd.concat(frames)
        return result
    
    def WF2file(self, fullFileName):
        df2Save:pd.DataFrame = self.WF2DF()
        df2Save.to_hdf(fullFileName)

    def toString(self, otherWFP: BaseWaveFormPreample):
        """Method to convert this WaveFormPreample and the otherWPF to a string representatie, which can be saved to disk or
        might be send by a stream."""
        #TODO: check which WFP is chan1 and check if both WFP has same elements.
        resStr = ""
        dundrscr = "__"
        dictOfWFP1 = vars(self)
        dictofWFP2 = vars(otherWFP)
        for member in dictOfWFP1:
            if dundrscr not in member:
                resStr += f"{member},\t{dictOfWFP1[member]},\t{member},\t{dictofWFP2[member]}.\n"
        return resStr
    
###################################### BASETRIGGERUNIT #########################################################
class BaseTriggerUnit(object):
    """New: creation of an object, or instance. 
    Only BaseTriggerUnit may call this new method for creating an object based on the correct type, as a kind
    of factory pattern. To get the right type __new__ will call getTriggerUnitClass methods from every subclass
    known to BaseTriggerUnit
    See also: https://mathspp.com/blog/customising-object-creation-with-__new__ 
    This coding scheme requires (automatic) registration of subclasses according pep487:
    see: https://peps.python.org/pep-0487/      
    """
    triggerUnitList = []

    @classmethod
    def getTriggerUnitClass(cls, vertical:BaseVertical,visaInstr:pyvisa.resources.MessageBasedResource=None):
        """Method for getting the right Python type, or the proper subclass of BaseTriggerUnit, based on parameters
        passed. 
            """
        pass
    
    def __init_subclass__(cls, **kwargs):
        """Method for autoregistration of BaseTriggerUnit subclasses. Don't alter and don't override. Be sure this
        the"""
        super().__init_subclass__(**kwargs)
        cls.triggerUnitList.append(cls)
        
    def __init__(self, vertical:BaseVertical=None, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """This method takes care of the intialisation of a BaseTriggerUnit object. Subclasses must override this 
        method, by initialising the datamembers needed. Remark: if the subclass relies on the intialisation done 
        below, don't forget to call the subcalss' super().__init()__ !"""
        self.vertical :pyvisa.resources.MessageBasedResource = vertical
        self.visaInstr = visaInstr
        self.source = None #the channel to trigger on.
        self.level =None
        
    def level(self):
        pass
        
    def level(self, level):
        pass 
    
    def setSource(self, chanNr):
        pass

    def getEdge(self):
        pass
    
    def setCoupling(self, coup:str):
        pass

    def setSlope(self, slope:str):
        pass
        
    def getFrequency(self):
        pass
        
    def getholdOff(self): #Trigger holdoff blz 215 TRIGger:MAIn:HOLDOff:VALue?
        pass

    def mode(self): #trigger mode blz 216 TRIGger:MAIn:MODe?
        pass

    def mode(self, modeVal):
        pass

    def getState(self): #tigger state zie blz 223 TRIGger:STATE?
        pass

class BaseDisplay(object):
    """BaseDisplay: a baseclass for the abstraction of a Display unit of an oscilloscope.
    All display implementations have to inherit from this baseclass.
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO fully implement the getChannelClass method of this class.
    3. Be sure this BaseChannel implementation has access to all inheriting subclasses during creation. If not, 
    the subclass won't be registered and creating the needed channel object(s) will fail."""

    displayList = []

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseChannel subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.displayList.append(cls)
    
    @classmethod
    def getDisplayClass(cls, dev):
        """getChannelClass: factory method for scope channel objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass

    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        """Method voor initialising this Channel object.
        Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr = visaInstr

    def format(self):
        pass

    def format(self, mode):
        pass

    def persist(self):
        pass
    
    def persist(self, persmode):
        pass

    
class BaseAcquisition(object):
    """BaseDisplay: a baseclass for the abstraction of a Display unit of an oscilloscope.
    All display implementations have to inherit from this baseclass.
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO fully implement the getChannelClass method of this class.
    3. Be sure this BaseChannel implementation has access to all inheriting subclasses during creation. If not, 
    the subclass won't be registered and creating the needed channel object(s) will fail."""

    acquisitionList = []

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseChannel subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.acquisitionList.append(cls)
    
    @classmethod
    def getAcquisitionClass(cls, dev):
        """getChannelClass: factory method for scope channel objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass

    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        """Method voor initialising this Channel object.
        Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr = visaInstr

    def mode(self):
        pass

    def mode(self, acqMode):
        pass

    def getNumOfAcquisition(self):
        pass

    def averaging(self):
        pass

    def averaging(self, nrOfAvg):
        pass

    def state(self):
        pass

    def state(self, runMode):
        pass