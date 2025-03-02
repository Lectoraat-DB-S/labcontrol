import socket
import pyvisa as visa
#import devices.tektronix.scope.TekScopes #Gives circular import problem


class BaseScope(object):
    """BaseScope: base class for oscilloscope.
        try to implement Python's properties.
        https://realpython.com/python-property/"""
    scopeList = []
    
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
        cls.scopeList.append(cls)
         
    @classmethod
    def getDevice(cls, urls, host):
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
       
        rm = visa.ResourceManager()
        devUrls = rm.list_resources()

        for scope in cls.scopeList:
            dev = scope.getDevice(devUrls, host)
            if dev != None:
                return dev
        
        return instance     
        
    def __init__(self, host=None):
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self._visaInstr : visa.Resource = None
        self._trigger:BaseTriggerUnit = None
        self._horizontal:BaseHorizontal = BaseHorizontal()
        self._vertical:BaseVertical = None
        self._utility = None
        self._host = None
        
    #@property 
    def visaInstr(self) -> visa.Resource: 
        """The reference to a visaInstrument object has to be created during creation of the object @init, which is a reason for the 
            programmer ot implement this as immutable property and not implement any kind of setter method for this property, nor in this class,
            nor in any derived class.
            """
        return self._visaInstr
    
        
    @property 
    def horizontal(self)->BaseHorizontal:
        """A horizontal is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._horizontal
        
    #@property 
    def vertical(self):
        """A vertical is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._vertical
    
    #@property 
    def trigger(self):
        """A trigger unit is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._trigger
    
    #@property 
    def utility(self):
        """A utility provision is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._utility


########## BASEVERTICAL ###########
    
class BaseVertical(object):
    VerticalList = list()
    
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
         
    @classmethod
    def getVertical(cls,nrOfChan, dev):
        """ Tries to get (instantiate) the device, based on the url"""
        return None #Base class implementation: return None, because this class can't do shit.
    
        
    def __new__(cls, nrOfChan, dev=None):
        """New: creation of object. 
        Only BaseScope may call this new methond as the first step in creation of a scope object. 
        This is a way to controll if an object will be returned from a new method and if so, which type of object
        it will have to return, as a form of factory pattern. 
        See also: https://mathspp.com/blog/customising-object-creation-with-__new__ 
        This coding scheme requires (automatic) registration of subclasses according pep487:
        see: https://peps.python.org/pep-0487/      
        """
        for vertical in cls.VerticalList:
            dev = vertical.getVertical(nrOfChan,dev)
            if dev != None:
                return dev
    
        
        return None
    

    def __init__(self, nrOfChan = 0, dev = None):
        self._channels = list()           
        self._nrOfChan = nrOfChan       # A virtual Baseclass: so no channels available.
        self._visaDev = dev             # default value = None, see param
    
    #@property
    def channels(self):
        """Getter for retrieving the available channels of this oscilloscope"""
        return self._channels
    
    #@property
    def nrOfChan(self):
        """Getter for retrieving number of the available channels of this oscilloscope"""
        return self._nrOfChan
    
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
         
    def __init__(self, dev = None):
        self._visaDev = dev             # default value = None, see param
        self._TB = 0.0                  # current value of timebase, unit sec/div
        self._SR = 0                    # samplerate
        self._POS = 0                   # Horizontal position in screen (of the waveforms)
        self._ZOOM = 0                  # Horizontal magnifying.
        
    def getTimeDivs(self):
        """Method for getting available timebase, or samething, horizontal settings of the oscilloscope
        This method returns a dict containing valid time/div settings"""
        return None
    
    @property
    def timediv(self):
        """Property for getting the setting of the timebase in s/div. Must be implemented by the inheriting subclasses for querying the oscilloscope
        its timebase by sending the correct SCPI command(s)."""
        return self._TB
    
    @timediv.setter
    def timediv(self, value):
        """Setter for the timebase property of BaseHorizontal. Inheriting subclasses have to check the validity of value and construct  the proper
        SCPI command to the oscilloscope."""
        self._TB = value
    
    @property
    def samprate(self):
        """Getter for the samplerate propedrty of BaseHorizontal. Must be implemented by the inheriting subclasses for querying the oscilloscope
        its samplerate by sending the correct SCPI command(s)."""
        #TODO: move to vertical?
        return self._SR
    
    @samprate.setter
    def samprate(self, value):
        """Setter for the samplerate property of BaseHorizontal. Inheriting subclasses have to check the validity of value and construct the proper
        SCPI command to the oscilloscope."""
        self._SR = value
        
    @property
    def pos(self):
        """Getter for the horizontal position. Must be implemented by the inheriting subclasses for querying the oscilloscope
        its position by sending the correct SCPI command(s)."""
        return self._POS
    
    @pos.setter
    def pos(self, value):
        """Setter for the position property of BaseHorizontal. Inheriting subclasses have to check the validity of value and construct the proper
        SCPI command to the oscilloscope."""
        self._POS = value
    
    @property
    def zoom(self):
        """Getter for the horizontal zoom factor. Must be implemented by the inheriting subclasses for querying the oscilloscope
        its current zoomfactor by sending the correct SCPI command(s)."""
        return self._ZOOM
    
    @zoom.setter
    def zoom(self, value):
        """Setter for the zoom BaseHorizontal. Inheriting subclasses have to check the validity of value and construct the proper
        SCPI command to the oscilloscope."""
        self._ZOOM = value

class BaseChannel(object):
    def __init__(self):
        self._waveform = None # the waveform of this channel
        self._vdiv = None
    @property
    def vdiv(self):
        """Getter for vdiv. This BaseChannel implementation is empty. Must be implemented by subclass."""
        return self._vdiv
    
    @vdiv.setter
    def vdiv(self, value):
        """Getter for vdiv. This BaseChannel implementation is empty. Must be implemented by subclass."""
        self._vdiv = value
        
    def capture(self):
        """Gets the waveform from the oscilloscope. The scope will hereto have to perform a new acquisition. This BaseChannel implementation is empty.
        An inheriting subclass must send the SCPI commands needed tot get waveform descriptors, gets the data and store it in this channels waveform"""
        pass
            
class BaseTriggerUnit(object):
    def __init__(self):
        pass
    
    
"""    
class FakeScopie(BaseScope):
    
    @classmethod
    def getDevice(cls, url, host):
        return None
        
    def __init__(self, host=None):
        super().__init__(host)
    
"""    
    