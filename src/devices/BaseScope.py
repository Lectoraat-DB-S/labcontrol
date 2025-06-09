import pyvisa

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
        datamembers uninitialised. A subclass should therefore override this function, by initialising the datamembers 
        needed. Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.brand = None
        self.model = None
        self.serial = None
        self.firmware = None
        self.visaInstr : pyvisa.resources.MessageBasedResource = visaInstr
        self.horizontal = None
        self.vertical = None
        self.trigger = None
        self.utility = None
        self.host = None
        
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
        
        
    def capture(self):
        """Gets the waveform from the oscilloscope, by initiating a new aqquisition. This BaseChannel implementation 
        is empty. An inheriting subclass wil have to implement this method by sending the proper SCPI commands 
        in order need to a. get waveform descriptors, b. get the raw data and take care for store it into the proper
        datastructures for plotting or processing."""
        pass

    def getAvailableMeasurements(self):
        pass
    
    def getMean(self):
        pass

    def getMax(self):
        pass

    def getPhase(self, input):
        pass
    
    def getFrequency(self):
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
        
    