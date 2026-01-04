import socket
import pyvisa
import math
import numpy as np
from devices.BaseConfig import LabcontrolConfig, BaseGeneratorConfig
from devices.visa_cache import get_visa_resources

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
    def getGeneratorClass(cls, rm, urls, host=None, myConfig: BaseGeneratorConfig = None):
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
        rm, urls = get_visa_resources()
        myconfig = LabcontrolConfig().find(cls)

        for generator in cls.GeneratorList:
            generatortype, nrOfChannels, dev = generator.getGeneratorClass(rm, urls, host, myconfig)
            if generatortype != None:
                cls = generatortype
                return cls(nrOfChannels, dev)
            
        return None # if getDevice can't find an instrument, return None.
    
    @classmethod
    def SocketConnect(cls, rm:pyvisa.ResourceManager = None, scopeConfig: BaseGeneratorConfig = None,
                timeOut = 10000, readTerm = '\n', writeTerm = '\n')->pyvisa.resources.MessageBasedResource:
        myConfig: BaseGeneratorConfig = scopeConfig
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
            
            mydev.timeout = timeOut  # ms
            mydev.read_termination = readTerm
            mydev.write_termination = writeTerm
            return mydev
        #No return needed here. Every path within function returns None or resource.
    


    def __init__(self, nrOfChan: int=0, instr:pyvisa.resources.MessageBasedResource=None, 
                 myConfig: BaseGeneratorConfig = None):
        """This method takes care of the intialisation of a BaseGenerator object. This implementation leaves most
        datamembers uninitialised. A subclass should therefore override this function, by initialising the datamembers 
        needed. Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr: pyvisa.resources.MessageBasedResource = instr
        self.nrOfChan = nrOfChan
        self._genConfig = myConfig

    def chan(self, chanNr): 
        """Gets a channel, based on its index: 1, 2 etc."""
        pass     

    def createFreqArray(self, start=1, stop=1000, nrOfSteps=10, type='LIN'):
        """"Creates an array of frequencies for AC sweep. Default type is linear ('LIN'). Other valid types are
         octave ('OCT') or decade ('DEC')."""
        #TODO: move to an util kind of library or package?
        if start >= stop:
            return
        if start < 0 or stop < 0 or nrOfSteps < 1:
            return
        
        myFreqArray = None
        match type:
            case 'LIN':
                myFreqArray = np.arange(start, stop, nrOfSteps)
            case 'OCT':
                mystart = math.log2(start) # if start = 10 than mystart = 1
                mystop = math.log2(stop)   # if stop = 100 than mystop = 2
                if mystart >= mystop:
                    return
                mystep = 1.0/nrOfSteps
                powArray = np.arange(mystart,mystop, mystep)
                roundPowArr = np.around(powArray, decimals=1) 
                myFreqArray = np.float_power(2.0, roundPowArr)
                myFreqArray = np.around(myFreqArray, decimals=1) 
               
            case 'DEC':
                mystart = math.log10(start) # if start = 10 than mystart = 1
                mystop = math.log10(stop)   # if stop = 100 than mystop = 2
                if mystart >= mystop:
                    return
                mystep = 1.0/nrOfSteps
                powArray = np.arange(mystart,mystop, mystep)
                roundPowArr = np.around(powArray, decimals=1) 
                myFreqArray = np.float_power(10.0, roundPowArr)
                myFreqArray = np.around(myFreqArray, decimals=1) 
               
        return myFreqArray


