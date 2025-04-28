import socket
import pyvisa as visa

class BaseDMM(object):
    """
        BaseDMM: base class for Digital Multi Meters (DMM).
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487,
            See:  https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
            class @classmethod
            def getDevice(cls, url): -> cls
        4. Be sure BaseDMM's constructor has access to the inheriting subclass during instantion. A preferable way doing 
            so, is to add the path/location of the subclass in the __init__.py file of folder which hold BaseDMM. 
            If the subclass is not visible to the __init_subclass__ method of this baseclass, it won't be registered 
            and therefore the correct device object won't be instantiated. 
        3. Remark: usage of Python's properties, for the getter-setter mechanisme, as discussed in
            https://realpython.com/python-property/, have been removed, because of some unexpected behaviour, which might 
            have its origin in Python's handling of properties. A property (and/or its behaviour) defined in a base class, 
            cannot be altered in a derived class. See: https://docs.python.org/3/reference/datamodel.html#invoking-descriptors,
              which states: he property() function is implemented as a data descriptor. Accordingly, instances cannot override the behavior of a property. 
    """
    supplyList = list()
    
    def __init_subclass__(cls, **kwargs):
        """ 
            Method for automatic registration of subclasses that have defined in Labcontrol (or will be defined)
            This way of registration requires Python version >= 3.6.
            For more info about this subject, see: https://peps.python.org/pep-0487/
        """
        super().__init_subclass__(**kwargs) 
        cls.supplyList.append(cls)
         
    @classmethod
    def getDevice(cls, rm, urls, host):
        """ Tries to get (instantiate) the device, based on the url. REMARK: this baseclass implementation is empty.
        Inheriting subclasses must implement this functionality."""
        return None #Base class implementation: return None, because this class can't do shit.
    
        
    def __new__(cls, host=None):
        """
        Only BaseSupply may call this new methond as the first step in creation of a scope object. 
        This is a way to controll if an object will be returned from a new method and if so, which type of object
        it will have to return, as a form of factory pattern. This method will call the getDevice implementation of each 
        registered subclass.
        See also:https://mathspp.com/blog/customising-object-creation-with-__new__ 
        
        This coding scheme relies on the (automatic) registration of subclasses according to pep487:
        see: https://peps.python.org/pep-0487/
        
        """
        instance = super().__new__(cls) #to have Pylance detect the proper type of a variable, call this!

        rm = visa.ResourceManager()
        devUrls = rm.list_resources()
        for supply in cls.supplyList:
            dev = supply.getDevice(rm, devUrls, host)
            if dev != None:
                return dev
        
        return instance  #needed for codecompletion by Pylance      
        
    def __init__(self, dev=None): #For now, init should get the nrOfChan for this scope as a param.
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self.visaInstr : visa.Resource = dev
        
    def idn(self):
        """Method for retrieving the indentification string of the GPIB instrument. REMARK: this is an empty baseclass
        implementation. Subclass will have to provide for the asked functionality."""
        pass
    
    def __exit__(self, *args):
        """Method for closing the visa instrument handle at deletion of this object."""
        if self.visaInstr != None:
            self.visaInstr.close()
    

