import pyvisa
#import labcontrol
#import devices.tektronix.scope.TekScopes #Gives circular import problem

class BaseScope(object):
    """BaseScope: base class for oscilloscope implementation.
    This code of this class also reflects the learning curve on Python.
        https://realpython.com/python-property/"""
    scopeList = []
    
    def __init_subclass__(cls, **kwargs):
        """BaseScope: base class for oscilloscope implementation.
        Implementations for oscilloscopes have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getDevice(cls, url):
        3. Be sure BaseScope's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. """
        super().__init_subclass__(**kwargs)
        cls.scopeList.append(cls)
         
    @classmethod
    def getDevice(cls, rm, urls, host):
        """ Tries to get (instantiate) the device, based on the url"""
        return None #Base class implementation: return None, because this class can't do shit.
    
        
    def __new__(cls, host=None):
        """New: creation of object. 
        Only BaseScope may call this new methond as the first step in creation of a scope object. 
        This is a way to controll if an object will be returned from a new method and if so, which type of object
        it will have to return, as a form of factory pattern. 
        See also: https://mathspp.com/blog/customising-object-creation-with-__new__ 
        This coding scheme requires (automatic) registration of subclasses according pep487:
        see: https://peps.python.org/pep-0487/      
        """
        instance = super().__new__(cls) #to have Pylance detect the proper type of a variable, call this!

        
        #rm = visa.ResourceManager("@sim")
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()
        print(rm.session)
        host = None

        for scope in cls.scopeList:
            dev = scope.getDevice(rm, urls, host)
            if dev != None:
                return dev
        
        return instance     
        
    def __init__(self, dev=None):
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self.visaInstr : pyvisa.Resource = dev
        self.horizontal = None
        self.vertical = None
        self.trigger = None
        self.utility = None
        self.host = None
        
    #@property 
    def visaInstr(self) -> pyvisa.Resource: 
        """The reference to a visaInstrument object has to be created during creation of the object @init, which is a reason for the 
        programmer not to implement this as immutable property and not implement any kind of setter method for this property, nor in this class,
        nor in any derived class.
            """
        return self.visaInstr
    
        
########## BASEVERTICAL ###########
    
class BaseVertical(object):
    VerticalList = list()
    type ChanList = list[BaseChannel]

    
    def __init_subclass__(cls, **kwargs):
        """BaseScope: base class for oscilloscope implementation.
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod 
        def getDevice(cls, url):
        4. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        3. Use Python's properties, for the getter-setter mechanisme, See: https://realpython.com/python-property/"""
        super().__init_subclass__(**kwargs)
        cls.VerticalList.append(cls)
         
    
    def __init__(self, nrOfChan = 0, dev = None):
        self.channels = list()           
        self.nrOfChan = nrOfChan       # A virtual Baseclass: so no channels available.
        self.visaInstr = dev             # default value = None, see param
              
    def chan(self, chanNr): 
        """Get the channel obejct based on the number. This method should be overridden by the 
        inherting subclass, as this BaseVertical implementation is empty."""
        pass
    
############ BaseHorizontal ###########
class BaseHorizontal(object):
    HorizontalList = list()
    
    def __init_subclass__(cls, **kwargs):
        """BaseHorizontal: base class for oscilloscope implementation.
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod 
        def getDevice(cls, url):
        4. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        3. Use Python's properties, for the getter-setter mechanisme, See: https://realpython.com/python-property/"""
        super().__init_subclass__(**kwargs)
        cls.HorizontalList.append(cls)
    
    @classmethod
    def getHorizontal(cls, dev):
        return cls
        
    def __new__(cls,dev):
        instance = super().__new__(cls) #to have Pylance detect the proper type of a variable, call this!
        
        for hori in cls.HorizontalList:
            dev = hori.getHorizontal(dev)
            if dev != None:
                return dev
        
        return instance     
          
    def __init__(self, dev = None):
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

###################################### BASECHANNEL #########################################################
class BaseChannel(object):
    def __init__(self, visaInstr):
        self.visaInstr = visaInstr
        self.WF = BaseWaveForm()            # the waveform ojbect of this channel
        self.WFP = BaseWaveFormPreample(visaInstr) # the waveformpreamble object for this channel
        
        
    def capture(self):
        """Gets the waveform from the oscilloscope, by initiating a new aqquisition. This BaseChannel implementation is empty.  
        An inheriting subclass wil have to implement this method by sending the proper SCPI commands 
        in order need to a. get waveform descriptors, b. get the raw data and take care for store it into the proper datastructures"""
        pass

    def getAvailableMeasurements(self):
        pass
    
    def getMean(self):
        pass

    def getMax(self):
        pass
######################################## BASEWAVEFORM #########################################################
class BaseWaveForm(object):
    
    def __init__(self):
        """Class for holding waveform data of a channel capture and the methods to transform raw sample data into soming fysical meaningful, such as voltage."""
        
###################################### BASECWAVEFORMPREAMBLE ###################################################
class BaseWaveFormPreample(object):
    """A WaveFormPreamble (WFP) is a kind of struct which holds relevant data about a channel capture. Based on WFP data, the WaveForm object is able to convert raw samples to
    measured voltages (vertical data) and samplenumbers to time of frequency instances. (x, t or f data)"""
    def __init__(self, dev):
        self.visaInstr = dev
        

###################################### BASETRIGGERUNIT #########################################################
class BaseTriggerUnit(object):
    """The base software representation of a triggerunit. This class has an empty implementation. An inheriting subclass will have to implement desired behaviour"""
    triggerUnitList = []
    
    def __init_subclass__(cls, **kwargs):
        """BaseScope: base class for oscilloscope implementation.
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod 
        def getDevice(cls, url):
        4. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        3. Use Python's properties, for the getter-setter mechanisme, See: https://realpython.com/python-property/"""
        super().__init_subclass__(**kwargs)
        cls.triggerUnitList.append(cls)
    
    def __new__(cls, vertical=None, dev=None):
        """New: creation of object. 
        Only BaseScope may call this new methond as the first step in creation of a scope object. 
        This is a way to controll if an object will be returned from a new method and if so, which type of object
        it will have to return, as a form of factory pattern. 
        See also: https://mathspp.com/blog/customising-object-creation-with-__new__ 
        This coding scheme requires (automatic) registration of subclasses according pep487:
        see: https://peps.python.org/pep-0487/      
        """
        instance = super().__new__(cls) #to have Pylance detect the proper type of a variable, call this!
        
        return instance

    
    def __init__(self, vertical=None, dev=None):
        self.vertical = vertical
        self.visaInstr = dev
        self.source = None #the channel to trigger on.
        self.level =None
        
    