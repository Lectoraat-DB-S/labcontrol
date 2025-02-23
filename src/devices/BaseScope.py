import socket
import pyvisa as visa
#import devices.tektronix.scope.TekScopes #Gives circular import problem

class BaseScope(object):
    """BaseScope: base class for oscilloscope.
        try to implement Python's properties.
        https://realpython.com/python-property/
    
    """
    scopeList = list()
    
    def __init_subclass__(cls, **kwargs):
        """ Method for automatic registration of subclasses that have defined in Labcontrol (or will be defined)
            This way of registration requires Python version >= 3.6.
            For more info about this subject, see: https://peps.python.org/pep-0487/
        """
        super().__init_subclass__(**kwargs)
        cls.scopeList.append(cls)
         
    @classmethod
    def getDevice(cls, url):
        """ Tries to get (instantiate) the device, based on the url"""
        return None #Base class implementation: return None, because this class can't do shit.
    
        
    def __new__(cls, host=None):
        """
        Only BaseScope may call this new methond as the first step in creation of a scope object. 
        This is a way to controll if an object will be returned from a new method and if so, which type of object
        it will have to return, as a form of factory pattern. 
        See also:https://mathspp.com/blog/customising-object-creation-with-__new__ 
        
        This coding scheme requires (automatic) registration of subclasses according pep487:
        see: https://peps.python.org/pep-0487/
        
        """
        rm = visa.ResourceManager()
        devUrls = rm.list_resources()
        for scope in cls.scopeList:
            dev = scope.getDevice(devUrls, host)
            if dev != None:
                return dev
        
        return None     
        
    def __init__(self, host=None):
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self._visaInstr : visa.Resource = None
        self._trigger = None
        self._horizontal = None
        self._vertical = None
        self._utility = None
        self._host = None
        
    @property 
    def visaInstr(self) -> visa.Resource: 
        """The reference to a visaInstrument object has to be created during creation of the object @init, which is a reason for the 
            programmer ot implement this as immutable property and not implement any kind of setter method for this property, nor in this class,
            nor in any derived class.
            """
        return self._visaInstr
    
        
    @property 
    def horizontal(self):
        """A horizontal is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._horizontal
        
    @property 
    def vertical(self):
        """A vertical is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._vertical
    
    @property 
    def trigger(self):
        """A trigger unit is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._trigger
    
    @property 
    def utility(self):
        """A utility provision is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._utility
    
class BaseVertical(object):
    def __init__(self):
        self._channels = None # channels wordt een dict, array of vectorachtig ding.
    
    @property
    def channels(self):
        """Getter for retrieving the available channels of this oscilloscope"""
        return self._channels
    

class BaseChannel(object):
    def __init__(self):
        self._waveform = None # the waveform of this channel
        self._vdiv = None
    @property
    def vdiv(self):
        """Getter for vdiv"""
        return self._vdiv
    
    @vdiv.setter
    def vdiv(self, value):
        self._vdiv = value
            
class BaseTriggerUnit(object):
    def __init__(self):
        pass
    
    
    
class FakeScopie(BaseScope):
    
    @classmethod
    def getDevice(cls, url, host):
        """ Tries to get (instantiate) the device, based on the url"""
        return None
        
    def __init__(self, host=None):
        super().__init__(host)
    
    
    