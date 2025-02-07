import pyvisa

class BaseScope(object): # alt. VISA instrument.
    """BaseScope: base class for oscilloscope.
        try to implement Python's properties.
        https://realpython.com/python-property/
    
    """
    def __init__(self):
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self._visaInstr : pyvisa.Resource = None
        self._urlPattern = None
        self._trigger = None
        self._horizontal = None
        self._vertical = None
        self._utility = None
        
    @property 
    def visaInstr(self) -> pyvisa.Resource: 
        """The reference to a visaInstrument object has to be created during creation of the object @init, which is a reason for the 
            programmer ot implement this as immutable property and not implement any kind of setter method for this property, nor in this class,
            nor in any derived class.
            The advisible logic is:
                if _visaInstrument == None:
                    theList = rm.list_resources()
                    pattern = derivedClass.PATTERN
                    for url in theList:
                    if pattern in url:
                        self._visaInstr = rm.open_resource(url)
                        break
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
    
    
    
    
    
    
    