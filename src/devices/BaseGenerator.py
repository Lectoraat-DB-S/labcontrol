import socket
import pyvisa

class BaseGenerator(object):
    """BaseGenerator: base class for oscilloscope implementation.
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
        """Method for handling the creation of the correct Scope object, by implementing a factory process. 
        Firstly, this method calls getScopeClass() for getting the right BaseScope derived type. If succesfull, this 
        method, secondly, returns this (class)type together with the needed parameters, to enable
        the Python runtime to create and initialise the object correctly.
        DON'T TRY TO CALL THE CONSTRUCTOR OF THIS CLASS DIRECTLY"""
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()

        for generator in cls.GeneratorList:
            generatortype, dev = generator.getScopeClass(rm, urls, host)
            if generatortype != None:
                cls = generatortype
                return cls(dev)
            
        return None # if getDevice can't find an instrument, return None.


    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """This method takes care of the intialisation of a BaseGenerator object. This implementation leaves most
        datamembers uninitialised. A subclass should therefore override this function, by initialising the datamembers 
        needed. Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
