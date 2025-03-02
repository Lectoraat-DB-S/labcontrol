import socket
import pyvisa as visa
#import devices.tektronix.scope.TekScopes #Gives circular import problem

class BaseSupply(object):
    """
        BaseSupply: base class for power supply.
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487,
            See:  https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
            class @classmethod
            def getDevice(cls, url):
        4. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
            subclass will not be registated and the correct supply object won't be instantiated. 
        3. Use Python's properties, for the getter-setter mechanisme, See: https://realpython.com/python-property/
    """
    supplyList = list()
    
    def __init_subclass__(cls, **kwargs):
        """ 
            Method for automatic registration of subclasses that have defined in Labcontrol (or will be defined)
            This way of registration requires Python version >= 3.6.
            For more info about this subject, see: https://peps.python.org/pep-0487/
        """
        super().__init_subclass__(**kwargs) #TODO: research if Python will only call the corresponding init_subclass
                                            # and not all base and subclass which uses this PEP487 scheme
                                            # See how Metaclasses of python < 3.6 were used: in that scheme
                                            # the new method checks if the correct object type is calling.
                                            # Apparently Python otherwise might take the wrong class/object
                                            # during construction.
        cls.supplyList.append(cls)
         
    @classmethod
    def getDevice(cls, url):
        """ Tries to get (instantiate) the device, based on the url"""
        return None #Base class implementation: return None, because this class can't do shit.
    
        
    def __new__(cls, host=None):
        """
        Only BaseSupply may call this new methond as the first step in creation of a scope object. 
        This is a way to controll if an object will be returned from a new method and if so, which type of object
        it will have to return, as a form of factory pattern. 
        See also:https://mathspp.com/blog/customising-object-creation-with-__new__ 
        
        This coding scheme relies on the (automatic) registration of subclasses according pep487:
        see: https://peps.python.org/pep-0487/
        
        """
        rm = visa.ResourceManager()
        devUrls = rm.list_resources()
        for supply in cls.supplyList:
            dev = supply.getDevice(devUrls, host)
            if dev != None:
                return dev
        
        return None     
        
    def __init__(self, host=None, nrOfChan=1): #For now, init should get the nrOfChan for this scope as a param.
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self._visaInstr : visa.Resource = None
        self._host = None
        self._nrOfChan = nrOfChan
    
class BaseChannel(object):
    def __init__(self):
        pass
    
        
    def enable(self, state):
        """
            Turns this channel on or off
        """
        pass    
    
    def setOCP(self, val):
        pass
    
    def setOVP(self, val):
        pass
    
    def measV(self):
        return None
    
    def measI(self):
        return None
    
    def setV(self, val):
        pass
    
    def setI(self, val):
        pass
    