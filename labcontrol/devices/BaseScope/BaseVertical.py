import pyvisa
from devices.BaseScope.BaseFunctions import ScopeFunction, ScopeMath
from devices.BaseScope.BaseChannel import Channel

########## BASEVERTICAL ###########
    
class Vertical(object):
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
        self.math:ScopeMath = ScopeMath()         

    def addMath(self, newFunction: ScopeFunction):
        self.math.add(newFunction)
    
    
    def getMath(self, functionStr:str = None, oper1 = None, oper2 = None):
        if functionStr == None:
            return self.math
        elif oper1 != None and oper2 == None:
            return self.math.get("FFT",oper1)
        else:
            return self.math.get(functionStr, oper1, oper2)

    #def chan(self, chanNr:int):          
    #def chan(self, chanNr)->BaseChannel: 
    #    """Get the channel object based on the number. This method should be overridden by the 
    #    inherting subclass, as this BaseVertical implementation is empty."""
    #    return None
    
    def chan(self, chanNr)->Channel: 
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
                chan:Channel  = self.chan(i+1)
                chan.setProcMode(mode)

