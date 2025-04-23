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

    
    #def __new__(cls):
    #    instance = super().__new__(cls) #to have Pylance detect the proper type of a variable, call this!
    #    if cls is BaseSupplyChannel:
    #TODO: 22 april, gerealiseerd dat ik de volgorde van calls bij creatie van objecten nog niet helemaal gesnopen heb.
    # De vraag: wie, waar en wanneer wordt __init__ aangeroepen? Doet Python dat? Moet de programmeur doen: in de init van de 
    # overgeorven klasse door __super__ te gebruiken? 
    # Nu doe ik maar wat. Bij autoregistratie, roept de baseclass in zijn __new__ functie de getDevice functie aan van de 
    # subklassen. Deze functie roept de init aan van de bijbehorende subklasse. Maar ik roep niet altijd __super__ aan in de 
    # init functie van de subklasse. En aangezien de testunit niet helemaal lekker werkt (resetting en/of verdwijnen van 
    # datamembers) vraag ik mij af of ik ook niet __new__ consequent moet implementeren en wat daar dan (minimaal) in moet 
    # komen en waarom. En ook wat de invloed is van de eis: python => 3.6

    
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
    def getDevice(cls, rm, urls, host):
        """ Tries to get (instantiate) the device, based on the url. REMARK: this baseclass implementation is empty.
        Inheriting subclasses must implement this functionality."""
        return None #Base class implementation: return None, because this class can't do shit.
    
        
    def __new__(cls, host=None):
        """__new__ : method for creation of a new BaseSupply object
        Don't override this method when inheriting: this method implements the logic which takes care of instantiating
        the correct subclass for controlling the actual connect power supply. In this way labcontrol is able to provide its 
        users with a transparent interface for every VISA device.
        
        Implemented logic: this method traverses a list of know subclasses and will call the getDevice implementation of 
        each registered subclass, which works like a kind of factory pattern. 
        
        This coding scheme relies on the (automatic) registration of subclasses according to pep487:
        see: https://peps.python.org/pep-0487/
        
        """
        instance = super().__new__(cls) #to have Pylance detect the proper type of a variable, call this!

        rm = pyvisa.ResourceManager()
        devUrls = rm.list_resources()
        for supply in cls.supplyList:
            dev = supply.getDevice(rm, devUrls, host)
            if dev != None:
                return dev
        
        return instance   #needed for codecompletion by Pylance  
        
    def __init__(self, dev=None, host=None, nrOfChan=1): #For now, init should get the nrOfChan for this scope as a param.
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self.visaInstr : pyvisa.Resource = dev
        self.host = None
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
    

