import socket
import pyvisa as visa
from  devices.siglent.sds.Scopes import SiglentScope

class BaseScope(object):
    """BaseScope: base class for oscilloscope.
        try to implement Python's properties.
        https://realpython.com/python-property/
    
    """
    scopeList = list()
    
    @classmethod
    def register(cls, newScopeClass):
        if newScopeClass != None:
            cls.scopeList.append(newScopeClass)
    
    @classmethod
    def getRegisteredDevices(cls):
        pass
    
    @classmethod
    def getDevice(cls, url):
        """ Tries to get (instantiate) the device, based on the url"""
        return None
    
        
    def __new__(cls, host=None):
        """The new will be called first during object creation. It can be used to controll if an object will be
        returned and if so, which type of object. See:
        https://mathspp.com/blog/customising-object-creation-with-__new__ """
        rm = visa.ResourceManager()
        devUrls = rm.list_resources()
        #deviceList = Devices.getRegisteredDevices()
        for scope in cls.scopeList:
            dev = scope.getDevice(devUrls)
        #   dev = device.getDevice(devUrls, host) 
        #   if device.getDevice(devUrls, host)
        #       cls = device.__class__
        ##  the deviceFound functions tries to match tokens of the url returned bij list_resources or tries to indentify
        ## the divice bij issuing a "*idn" request.
        if host is None:
            theList = rm.list_resources()
            #code below is applicable voor siglent sds, but for Tektronix, one must first check "USB" on the URL
            #and the use the idn call. Maybe a single call to idn would be sufficient. 
            pattern = "SDS"
            for url in theList:
                if pattern in url:
                    mydev = rm.open_resource(url)
                    if cls is BaseScope:
                        cls = SiglentScope
                        return super().__new__(cls)
                    break
                else:
                    return None
        else:
            try:
                #logger.info(f"Trying to resolve host {self._host}")
                ip_addr = socket.gethostbyname(host)
                mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                if cls is BaseScope:
                        cls = SiglentScope
                        return super().__new__(cls)
            except socket.gaierror:
                #logger.error(f"Couldn't resolve host {self._host}")
                return None
        
        
    def __init__(self, host=None):
        """abstract init function. A subclass should be override this function, which wil intitialize object below"""
        self._visaInstr : visa.Resource = None
        self._urlPattern = None
        self._trigger = None
        self._horizontal = None
        self._vertical = None
        self._utility = None
        self._host = None
        
    @property 
    def visaInstr(self) -> visa.Resource: 
        """The reference to a visaInstrument object has to be created during creation of the object @init, which is a reason for the 
            programmer ot implement this as immutable property and not implement any kind of setter method for this property, nor in this class,
            nor in any derived class.
            The advisible logic is:
                if _visaInstrument == None:
                    theList = rm.list_resources()
                    pattern = derivedClass.PATTERN
                    for url in theList:
                    if pattern in url:
                        self._visaInstr = rm.open_resource(url)
                        break
            """
        return self._visaInstr
    
        
    @property 
    def horizontal(self):
        """A horizontal is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._horizontal
        
    @property 
    def vertical(self):
        """A vertical is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._vertical
    
    @property 
    def trigger(self):
        """A trigger unit is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._trigger
    
    @property 
    def utility(self):
        """A utility provision is an immutable property of an oscilloscope. Therefore this class, but also inheriting classes should 
            not implement a setter method  """
        return self._utility
    
class BaseVertical(object):
    def __init__(self):
        self._channels = None # channels wordt een dict, array of vectorachtig ding.
    
    @property
    def channels(self):
        """Getter for retrieving the available channels of this oscilloscope"""
        return self._channels
    

class BaseChannel(object):
    def __init__(self):
        self._waveform = None # the waveform of this channel
        self._vdiv = None
    @property
    def vdiv(self):
        """Getter for vdiv"""
        return self._vdiv
    
    @vdiv.setter
    def vdiv(self, value):
        self._vdiv = value
            
class BaseTriggerUnit(object):
    def __init__(self):
        pass
    
    
    
class FakeScopie(BaseScope):
    
    @classmethod
    def getDevice(cls, url):
        """ Tries to get (instantiate) the device, based on the url"""
        return cls
        
    def __init__(self, host=None):
        super().__init__(host)
    
    
    