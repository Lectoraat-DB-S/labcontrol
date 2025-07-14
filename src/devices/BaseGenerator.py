import socket
import pyvisa

class BaseGenChannel(object):
    """BaseGenChannel: base class for channel implementation of a function generator.
        Implementations for functiongenerators have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getGeneratorClass.
        3. Be sure BaseGenerator's constructor has access to the inheriting subclasses during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        4. Instantion must be done by calling the getDevice method. This method implements a factory kind of scheme. 
    """
    GenChannelList = []        
    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseScope subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.GenChannelList.append(cls)
         
    @classmethod
    def getGenChannelClass(cls,  chan_no, dev):
        """getGenChannelClass: factory method for generator channel objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass
        
    def __init__(self, chan_no: int, instr:pyvisa.resources.MessageBasedResource=None):
        """This method takes care of the intialisation of a BaseGenerator object. This implementation leaves most
        datamembers uninitialised. A subclass should therefore override this function, by initialising the datamembers 
        needed. Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr: pyvisa.resources.MessageBasedResource = instr

    def setfreq(self, freq):
        pass

    def setAmp(self, amp):
        pass

    def setOffset(self, offset):
        pass
    def setSineWave(self,freq=None, amp=None):
        pass

    def setPulseWave(self, period, pulseWidth, rise, fall, delay=0):
        pass

    def setPulseWidth(self, pulseWidth):
        pass

    def enableSweep(self, val: bool):
        pass
    
    def setSweep(self, time, start, stop):  
        pass
    
    #short version call
    def setWaveType(self, type):
        pass

    def enableOutput(self,val: bool):
        pass
            
    ######### GET FUNCTIONS ########
    
    def getWaveParam(self):
        pass

    def getModulationParam(self):
        pass 

    def getSweepParam(self):
        pass

    def getBurstParam(self):
        pass
    

class BaseGenerator(object):
    """BaseGenerator: base class for generator implementation.
        Implementations for functiongenerators have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getGeneratorClass.
        3. Be sure BaseGenerator's constructor has access to the inheriting subclasses during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        4. Instantion must be done by calling the getDevice method. This method implements a factory kind of scheme. 
    """
    GeneratorList = []        
    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseScope subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.GeneratorList.append(cls)
         
    @classmethod
    def getGeneratorClass(cls, rm, urls, host=None):
        """Method for getting the right type of scope, so it can be created by the runtime.
        This Basescope implementation does nothing other the return the BaseScope type. The inheriting
        subclass should implement the needed logic"""
        return cls
    
    @classmethod
    def getDevice(cls,host=None):
        """Method for handling the creation of the correct Generator object, by implementing a factory process. 
        Firstly, this method calls getGeneratorClass() for getting the right Generator derived type. If succesfull, this 
        method, secondly, returns this (class)type together with the needed parameters, to enable
        the Python runtime to create and initialise the object correctly.
        DON'T TRY TO CALL THE CONSTRUCTOR OF THIS CLASS DIRECTLY"""
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()

        for generator in cls.GeneratorList:
            generatortype, nrOfChannels, dev = generator.getGeneratorClass(rm, urls, host)
            if generatortype != None:
                cls = generatortype
                return cls(nrOfChannels, dev)
            
        return None # if getDevice can't find an instrument, return None.


    def __init__(self, nrOfChan: int=0, instr:pyvisa.resources.MessageBasedResource=None):
        """This method takes care of the intialisation of a BaseGenerator object. This implementation leaves most
        datamembers uninitialised. A subclass should therefore override this function, by initialising the datamembers 
        needed. Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr: pyvisa.resources.MessageBasedResource = instr
        self.nrOfChan = nrOfChan

    def chan(self, chanNr): 
        """Gets a channel, based on its index: 1, 2 etc."""
        pass     
