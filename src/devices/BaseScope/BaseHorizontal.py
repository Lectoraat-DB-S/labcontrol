import pyvisa
############ BaseHorizontal ###########
class Horizontal(object):
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
    
    def getTimeDiv(self):
        """Method for getting available timebase setting. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""    
        pass

    def setTimeDiv(self, value):
        """Method for setting a timebase vaule. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""    
        pass

    def setDelay(self, val):
        """Sets the main timebase delay. This delay is the time between the trigger event and the 
        delay reference point on the screen. The range of the value is 5000div timebase, 5div timebase]. 
        This method should be overridden by the inherting subclass, as this BaseHorizontal implementation is empty."""
        pass

    def getDelay(self):
        """Method for getting the current set delay of the timebase. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass

    def setRefPos(self, value:int):
        """Method for setting the reference, or zero point, in case of a timebasedelay. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass

    def getRefPos(self):
        """Method for getting the reference, or zero point, in case of a timebasedelay. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass        

    def setWindowZoom(self, state:bool):
        """Method for setting the state of the timebase zoom funcion. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty. """
        pass

    def getWindowZoom(self, state:bool):
        """Gets the current state of the zoomed timebase window: on or off."""
        pass

    def setWindowDelay(self, val):
        """Sets the horizontal position in the zoomed view of the main sweep."""
        pass

    def getWindowDelay(self):
        """Gets the amount of delay set in the Timebase delay window."""
        pass

    def setWindowScale(self, val):
        """Method for setting the zoomed window horizontal scale (sec/div)"""
        pass

    def getWindowScale(self, val):
        """Gets the amount of time/division set for the zoomed timebase."""
        pass
            