import pyvisa
import socket
import logging

from devices.BaseConfig import LabcontrolConfig, BaseScopeConfig
from devices.BaseLabDeviceUtils import SCPICommand
from devices.BaseScope.BaseVertical import Vertical
from devices.BaseScope.BaseHorizontal import Horizontal
from devices.BaseScope.BaseTrigger import TriggerUnit
from devices.BaseScope.BaseAcquisition import Acquisition
from devices.BaseScope.BaseDisplay import Display


logger = logging.getLogger(__name__)
        
class Scope(object):
    """BaseScope: base class for oscilloscope implementation.
        Implementations for oscilloscopes have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getScopeClass.
        3. Be sure BaseScope's constructor has access to the inheriting subclasses during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        4. Instantion must be done by calling the getDevice method. This method implements a factory kind of scheme. 
    """
    scopeList = []        
    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseScope subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.scopeList.append(cls)
         
    @classmethod
    def getScopeClass(cls, rm, urls, host=None, scopeConfigs: list = None):
        """Method for getting the right type of scope, so it can be created by the runtime.
        This Basescope implementation does nothing other the return the BaseScope type. The inheriting
        subclass should implement the needed logic"""
        pass
    
    @classmethod
    def getDevice(cls,host=None):
        """Method for handling the creation of the correct Scope object, by implementing a factory process. 
        Firstly, this method calls getScopeClass() for getting the right BaseScope derived type. If succesfull, this 
        method, secondly, returns this (class)type together with the needed parameters, to enable
        the Python runtime to create and initialise the object correctly.
        DON'T TRY TO CALL THE CONSTRUCTOR OF THIS CLASS DIRECTLY"""
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()
        myconfigs = LabcontrolConfig().find(cls) # myconfig is a list of config 

        for scope in cls.scopeList:
            scopetype, dev, theConfig = scope.getScopeClass(rm, urls, host, myconfigs)
            if scopetype != None:
                cls = scopetype
                return cls(dev, theConfig)
        logger.warning("Geen oscilloscoop gevonden!")    
        return None # if getDevice can't find an instrument, return None.

    @classmethod
    def SocketConnect(cls, rm:pyvisa.ResourceManager = None, scopeConfig: BaseScopeConfig = None,
                timeOut = 10000, readTerm = '\n', writeTerm = '\n')->pyvisa.resources.MessageBasedResource:
        myConfig: BaseScopeConfig = scopeConfig
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
            
            mydev = rm.open_resource("TCPIP::"+str(ip_addr)+"::INSTR")
            mydev.timeout = timeOut  # ms
            mydev.read_termination = readTerm
            mydev.write_termination = writeTerm
            return mydev
        #No return needed here. Every path within function returns None or resource.

    
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource=None, scopeConfig: BaseScopeConfig = None):
        """This method takes care of the intialisation of a BaseScope object. This implementation leaves most
        datamembers uninitialised. A subclass should therefore override this function and initialise the datamembers. 
        Remark: don't forget to call super().__init()__ if needed!"""
        self.brand = None
        self.model = None
        self.serial = None
        self.firmware = None
        self.visaInstr : pyvisa.resources.MessageBasedResource = visaInstr
        self.horizontal : Horizontal = None
        self.vertical : Vertical = None
        self.trigger : TriggerUnit = None
        self.display : Display = None
        self.acquisition : Acquisition = None
        self.utility = None
        self.host = None
        self.scpiCommand = None # this member is a ref to a dict() containing all commands known to a device.
        
        self.nrOfHoriDivs = None# maximum number of divs horizontally
        self.nrOfVertDivs = None # maximum number of divs vertically 
        self.visibleHoriDivs = None# number of visible divs on screen
        self.visibleVertDivs = None # number of visible divs on screen
        

        #self.nrOfHoriDivs = scopeConfig.horizontalGrid # maximum number of divs horizontally
        #self.nrOfVertDivs = scopeConfig.verticalGrid # maximum number of divs vertically 
        #self.visibleHoriDivs = scopeConfig.visibleHorizontalGrid # number of visible divs on screen
        #self.visibleVertDivs = scopeConfig.visibleVerticalGrid # number of visible divs on screen
        self.mode = "SW"  #default setting for the data processing, when doing measurements with this scope.
        self._scopeConfig = scopeConfig

    def OPC(self):
        """Method for sending an *OPC? query to the instrument. This query places an ASCII "1" in the output queue when 
        all pending device operations have completed. The interface hangs until this query returns."""
        resp =self.visaInstr.query("*OPC?")
        print("OPC query response")
        print(resp)
        return self.visaInstr.query("*OPC?")
    
    def INR(self):
        pass

    def STB(self):
        pass

    def SRE(self):
        pass

    def ESE(self):
        pass

    def CMR(self):
        pass
    
    def CLS(self):
        pass

    def DDR(self):
        pass

    def EXR(self):
        pass
    #@property 
    def visaInstr(self) -> pyvisa.resources.MessageBasedResource: 
        """Method for getting the reference to this objects VISA resource. 
        The reference to a visaInstrument object will be set by init only. 
        Please don't alter this method or override it when deriving this class.
        """
        return self.visaInstr
    
    def setSCPICommand(self, SCPICommandDict: dict = None, PARAMDict: dict = None):
        self.scpiCommand = SCPICommand(SCPICommandDict, PARAMDict)
    
    def acquire(self):
        pass
    
    def acquire(self, state, mode=None, nrOfAvg=None, stopAfter=None):
        pass

    def setProcMode(self, mode):
        """Sets the processing or measurement mode of this channel to "SW" or "HW". When set to "SW", every subsequent measurement
        request made by this scope or it sibling object will be done in software. 
        When set "HW", the request will be done by the oscilloscope (the hardware). If the actual connected scope doesn't not offer 
        the measurement function requested, the operation will be done in software, to maintain functional consistency for every scopes.
        """
        if mode == "SW" or mode == "HW":
            self.mode = mode    
            self.vertical.setProcMode(self.mode)
    

 


