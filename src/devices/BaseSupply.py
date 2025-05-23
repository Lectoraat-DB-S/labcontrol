import socket
import pyvisa

#Korad heeft volgende interface
#iset(value), iset(), iout()
#vset(value), vset(), vout()
#OCP => aan/uit, ocp set, ocp read. idem voor V
#Alternatief OCP is klasse. OCP.on/OCP.off OCP.set

class BaseSupplyChannel(object):
    """BaseSupplyChannel: a base abstraction of a controllable channel of a power supply. Problably, an inheriting subclass
    will override all methods of this baseclass, as this baseclass hasn't got any functional implementation. 
    """
    supplyChannelList = list()

    def __init_subclass__(cls, **kwargs):
        """ __init_subclass__: method for autoregistration, according to pep487, See:  
        https://peps.python.org/pep-0487/. This way of registration requires a Python environment with version >= 3.6.
        
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, 
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getDevice(cls, url):
        3. Be sure BaseScope's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. """
        super().__init_subclass__(**kwargs) 
        cls.supplyChannelList.append(cls)
    
    def __init__(self, chanNr : int = None, dev : pyvisa.resources.Resource = None):
        """__init__: This method will be called after creation of a channel object. 
        Parameters: 
            chanNr:     an integer index number representing this channelobject.
            visaInstr:  a VISA reference to an succesfully opened VISA instrument"""
        self.visaInstr = dev
        self.name = chanNr
    
        
    def enable(self, state: bool):
        """
            Turns this channel on or off. Remark: empty method. To be implemented by subclass
        """
        pass    
    
    def OCP(self, val):
        """
            Sets this channel's over current protection (OCP), if available. Remark: empty method. 
            To be implemented by the subclass.
        """
        pass

    def OCP(self):
        """
            Gets the current OCP setting for this channel. To be implemented by the subclass.
        """ 
        pass
    
    def OVP(self, val):
        """
            Sets this channel's over voltage protection (OVP), if available. To be implemented by the subclass.
        """
        pass
    
    def OVP(self):
        """
        Gets the current OVP setting for this channel. To be implemented by the subclass.
        """ 
        pass
    

    def measV(self):
        """
            Measures this channel's actual output voltage. To be implemented by the subclass.
        """
        return None
    
    def measI(self):
        """
            Measures this channel's actual output current. To be implemented by the subclass.
        """
        return None
    
    def setV(self, val):
        """
            Sets this channel's output voltage setpoint. To be implemented by the subclass.
        """
    
    def setV(self):
        """
            Gets this channel's output voltage setpoint. To be implemented by the subclass.
        """

    def setI(self, val):
         """
            Sets this channel's output current setpoint. To be implemented by the subclass.
        """
    def setI(self):
         """
            Gets this channel's output current setpoint. To be implemented by the subclass.
        """
    


class BaseSupply(object):
    """
        BaseSupply: base class for power supply.
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487,
            See:  https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
            class @classmethod
            def getDevice(cls, url):
        3. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
            subclass will not be registated and the correct supply object won't be instantiated. 
    """
    supplyList = list()
    
    def __init_subclass__(cls, **kwargs):
        """ __init_subclass__: method for autoregistration, according to pep487, See:  
        https://peps.python.org/pep-0487/. This way of registration requires a Python environment with version >= 3.6.
        
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, 
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getDevice(cls, url):
        3. Be sure BaseScope's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. """
        super().__init_subclass__(**kwargs) 
        cls.supplyList.append(cls)
         
    @classmethod
    def getSupplyClass(cls, rm, urls, host=None):
        """Method for getting the right type of supply, so it can be created by the runtime.
        This method only returns BaseSupply's baseclass type (e.g. it returns the BaseSupply type). The inheriting
        subclass should implement the needed logic to return the neede derived subtype."""
        return cls
    
    @classmethod
    def getDevice(cls,host=None):
        """Method for handling the creation of the correct Supply object, by implementing a factory process. 
        Firstly, this method calls getSupplyClass() for getting the right BaseSupply derived type. If succesfull, 
        this method, secondly, returns this (class)type together with the needed parameters, to enable Python's 
        runtime to create and initialise the object correctly.
        DON'T TRY TO CALL THE CONSTRUCTOR OF THIS CLASS DIRECTLY"""
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()

        for supply in cls.supplyList:
            supplyType, nrOfChan, dev = supply.getSupplyClass(rm, urls, host)
            if supplyType != None:
                cls = supplyType
                return cls(nrOfChan, dev)
    
        return None # if getDevice can't find an instrument, return None.    
        
    def __init__(self, nrOfChan : int = None, visaInstr : pyvisa.resources.MessageBasedResource = None): 
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self.visaInstr : pyvisa.Resource = visaInstr
        self.nrOfChan = nrOfChan
        self.channels = None

    #def chan(self, chanNr:int)->BaseSupplyChannel:
    #    """Method for getting the channel based on index 1, 2 etc. REMARK: this is an empty baseclass
    #    implementation. Subclass implementations will have to provide this kind of functionality."""
    #    pass

    def idn(self):
        """Method for retrieving the indentification string of the GPIB instrument. REMARK: this is an empty baseclass
        implementation. Subclass implementation will have to provide this functionality."""
        pass
    
    def __exit__(self, *args):
        """Method for closing the visa instrument handle at deletion of this object. It shouldn't be necessary to override
        this in case of inheritance, ony if the subclass opens rescoures other than pyvisa. """
        if self.visaInstr != None:
            self.visaInstr.close()
    

