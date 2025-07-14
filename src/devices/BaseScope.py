import pyvisa
import matplotlib.pyplot as plt

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
    def getScopeClass(cls, rm, urls, host=None):
        """Method for getting the right type of scope, so it can be created by the runtime.
        This Basescope implementation does nothing other the return the BaseScope type. The inheriting
        subclass should implement the needed logic"""
        return cls
    
    @classmethod
    def getDevice(cls,host=None):
        """Method for handling the creation of the correct Scope object, by implementing a factory process. 
        Firstly, this method calls getScopeClass() for getting the right BaseScope derived type. If succesfull, this 
        method, secondly, returns this (class)type together with the needed parameters, to enable
        the Python runtime to create and initialise the object correctly.
        DON'T TRY TO CALL THE CONSTRUCTOR OF THIS CLASS DIRECTLY"""
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()

        for scope in cls.scopeList:
            scopetype, dev = scope.getScopeClass(rm, urls, host)
            if scopetype != None:
                cls = scopetype
                return cls(dev)
            
        return None # if getDevice can't find an instrument, return None.

    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource=None):
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
        self.utility = None
        self.host = None
        self.horiGridSize = None # Every scope has a horizontal grid, ie a number of divs. To plot, one need tdiv
        self.vertiGridSize = None # Every scope has a vertical grid or divisions. To plot vertically one need e.g. vdiv
        
    #@property 
    def visaInstr(self) -> pyvisa.resources.MessageBasedResource: 
        """The reference to a visaInstrument object will be stored by init. visaInstr is an immutable property. 
        Therefore no setter method has been defined for this property. Please don't alter this property or
        override in the derived class.
            """
        return self.visaInstr
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
        self.WF = BaseWaveForm()            # the waveform ojbect of this channel
        self.WFP = BaseWaveFormPreample(visaInstr) # the waveformpreamble object for this channel

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
        
    def capture(self):
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

    def getYzero(self):
        """Gets the vertical offset of this channel on display. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
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
        pass

    def getPhaseTo(self, input):
        """Calculates the phase difference of this channels last waveform with respect to the input parameter. The
        phase should be calculated by: self.phase - input.phase. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality of the physical scope, but, 
        if not present, by a software implementation of the derived class.
        """
        pass
    
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
        return None 

    
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
    
    #def chan(self, chanNr:int):          
    def chan(self, chanNr)->BaseChannel: 
        """Get the channel object based on the number. This method should be overridden by the 
        inherting subclass, as this BaseVertical implementation is empty."""
        return None
    
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
        return cls
        
          
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
        return cls
        
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
        self.xzero          = None # Horizontal Position value
        self.xUnitStr       = None # unit of X-as/xdata
        self.xincr          = None # multiplier for scaling time data, time between two sample points.
        self.nrOfSamples    = None # the number of points of trace.
        self.sampleStepTime = None # same as XINCR, Ts = time between to samples.
        self.yzero          = None 
        self.ymult          = None # vertical step scaling factor. Needed to translate binary value of sample to real stuff.
        self.yoff           = None # vertical offset in V for calculating voltage
        self.yUnitStr       = None
            
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
        #TODO: to prevent definition of a vast number of query-like method, it might be a good idea
        # to define some basic members of this preamble. A number of possible parameters will be defined, but 
        # if applicable, these parameters then must be incorporated into the subclasses.
        # These parameters should be the bare minimum of parameters to create a nice plot of the transferred
        # scope data.
        self.xzero      = None # The horizontal offset on screen
        self.yzero      = None # The vertical offset on screen
        self.ydiv       = None # The amount of vertical displacement per division   
        self.xdiv       = None # The amount of horizontal displacement per division
        self.vdiv       = None # same as ydiv
        self.tdiv       = None # same as xdiv
        self.xincr      = None # The amount of horizontal displacement between two subsequent samples.
        self.yincr      = None # The minimal amount of vertical displacement (compare resolution or number of bits, inverted)
        self.points     = None # The number of samples of the waveform
        self.vertMode   = None # Y, XY, or FFT.
        self.xUnitStr   = None # String, e.g. 's', 'f' or 'w'
        self.yUnitStr   = None # String, e.g. 'V' or 'DC'

    def queryPreamble(self):
        """Method for getting the preamble of the scope and set the correct data members
        of a preamble. This baseclass has no implementation."""
        pass
        

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
        return cls
    
    def __init_subclass__(cls, **kwargs):
        """Method for autoregistration of BaseTriggerUnit subclasses. Don't alter and don't override. Be sure this
        the"""
        super().__init_subclass__(**kwargs)
        cls.triggerUnitList.append(cls)
    
    
    def __init__(self, vertical:BaseVertical=None, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """This method takes care of the intialisation of a BaseTriggerUnit object. Subclasses must override this 
        method, by initialising the datamembers needed. Remark: if the subclass relies on the intialisation done 
        below, don't forget to call the subcalss' super().__init()__ !"""
        self.vertical = vertical
        self.visaInstr = visaInstr
        self.source = None #the channel to trigger on.
        self.level =None
        
    