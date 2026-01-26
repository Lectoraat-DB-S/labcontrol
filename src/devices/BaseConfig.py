import configparser
import os
from ast import literal_eval

class ConfigReader(object):

    MY_CONFIG_PATH = '.\\devices\\labdevices.ini'
    BASE_TYPE_CONFIG_STR = 'BaseClassName'
    DERIVED_TYPE_CONFIG_STR = 'DerivedClassName'
    AV_VISA_INTERFACES_CONFIG_STR = 'VisaInterfaces'
    CURR_VISA_INTERFACE_CONFIG_STR = 'VisaInterface'
    CURR_SEARCH_METHOD_CONFIG_STR = 'IDN' 
    IP_ADRESS_CONFIG_STR = 'IPAdress'
    VNC_PORTNR_CONFIG_STR = 'VNCPort'
    BASESCOPE_HORIZONTAL_CONFIG_STR ='HorizontalGrid'
    BASESCOPE_VIS_HORIZONTAL_CONFIG_STR ='VisibleHorizontalGrid'
    BASESCOPE_VERTICAL_CONFIG_STR ='VerticalGrid'
    BASESCOPE_VIS_VERTICAL_CONFIG_STR ='VisibleVerticalGrid'
    BASESCOPE_NROFCHAN_CONFIG_STR = 'nrOfChan'
    
    #Old stuff
    DEV_TYPE_SCOPE      = "Oscilloscope"
    DEV_TYPE_SUPPLY     = "Supply"
    DEV_TYPE_GENERATOR  = "Generator"
    DEV_TYPE_DMM        = "DMM"


    def __init__(self):
        self._parser:configparser.ConfigParser = configparser.ConfigParser()
        self._parser.read(ConfigReader.MY_CONFIG_PATH)
        self._devConfigList= None # the list with all known Labdevice config objects
        self.allSections()

    @property
    def devConfigList(self):
        return self._devConfigList

    def allSections(self):
        return self._parser.sections()
    
    def getSection(self, section):
        return literal_eval(self._parser[section])
    
    def getProperty(self, devName, prop):
        if self._parser.has_option(devName, prop):
            return literal_eval(self._parser[devName][prop])
        else:
            return None

class BaseDeviceConfig(object):
    VISA_INTERFACE_TCPIP_IF_STR = "USB INSTR"
    VISA_INTERFACE_SOCKET_IF_STR = "TCPIP INSTR"
    VISA_INTERFACE_USB_IF_STR = "TCPIP SOCKET"
    
    configClassList = []
    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseChannel subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.configClassList.append(cls)    

    @classmethod
    def getConfig(cls, devName, baseType, derivedType):
        """Method for handling the creation of the correct config object, by implementing a factory process. 
        1.This method calls getConfigClass() for getting the right BaseDeviceConfig derived type. If succesfull,
        2. This method, secondly, returns this (class)type together with the necessary parameters, to enable
        the Python runtime to create and initialise the object correctly.
        DON'T  CALL THE CONSTRUCTOR OF THIS CLASS DIRECTLY"""
        # twee opties van logica voor deze functie:
        # 1. affietsen van deviceList en dan alle sectiesnamen (sectietitels) doorfietsen, waarbij er 
        #   gezocht wordt op het juiste apparaatsoort en merknaam (eventueel modelnummer)
        """Pseudo code 1
        
        for configClass in cls.configClassList:
            if configClass.getDevType() in scopeClassType
        """
        # 2. Eerst alle secties opzoeken in labcontrol.ini en dan pas de lijst met configSubClasses doorfietsen.
        
        # eerst maar eens 1. proberen:

        for configClassName in cls.configClassList:
            configType, dev = configClassName.getConfigClass(devName, baseType, derivedType)
            if configType != None:
                return cls(devName, baseType, derivedType)
                    
        return None # if getDevice can't find an instrument, return None.

    @classmethod
    def getConfigClass(cls, devName, baseType, derivedType):
        """getConfigClass: factory method for config objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass

    def __init__(self, devName, baseType, derivedType): #TODO: use param!
        self._name = devName #section name
        self._configParser = ConfigReader()
        self._visaInterfaces = None#["USB INSTR","TCPIP INSTR","TCPIP SOCKET"]#TODO: find all possible VISA interface options on internet.
        self._currVisaIF = None
        self._currSearchMethod = "IDN"
        self._baseType = baseType
        self._derivedType = derivedType
        self._ipAddress = None
        self._vncPort = None
        self.fill()

    def fill(self):
        self._ipAddress = self._configParser.getProperty(self._name, ConfigReader.IP_ADRESS_CONFIG_STR)
        self._visaInterfaces =self._configParser.getProperty(self._name, ConfigReader.AV_VISA_INTERFACES_CONFIG_STR)
        self._currVisaIF = self._configParser.getProperty(self._name, ConfigReader.CURR_VISA_INTERFACE_CONFIG_STR)
        self._currSearchMethod = self._configParser.getProperty(self._name, ConfigReader.CURR_SEARCH_METHOD_CONFIG_STR)
        self._vncPort = self._configParser.getProperty(self._name, ConfigReader.VNC_PORTNR_CONFIG_STR)

    @property
    def baseType(self):
        return self._baseType
    
    @property
    def VNCPort(self):
        return self._vncPort

    @property
    def IPAddress(self):
        return self._ipAddress
    
    @property
    def devName(self):
        return self._name
    
    @property
    def visaInterfaces(self, name):
        return  self._visaInterfaces

    @property
    def currVisaIF(self, name):
        return self._currVisaIF
         
    @property
    def currSearchMethod(self, name):
        return self._currSearchMethod


class BaseScopeConfig(BaseDeviceConfig):
    #TODO: maybe should this move to BaseScope.py?
    @classmethod
    def getConfigClass(cls, devName, baseType, derivedType):
        """ Tries to get (instantiate) the config object"""
        if baseType == "BaseScope":
            return (cls, devName)
        else:
            return (None, None)

    def __init__(self, devName, baseType, derivedType):
        super().__init__(devName, baseType, derivedType)
        self._horizontalGrid = self._configParser.getProperty(self._name, ConfigReader.BASESCOPE_HORIZONTAL_CONFIG_STR)
        self._visibleHorizontalGrid = self._configParser.getProperty(self._name, ConfigReader.BASESCOPE_VIS_HORIZONTAL_CONFIG_STR)
        self._verticalGrid = self._configParser.getProperty(self._name ,ConfigReader.BASESCOPE_VERTICAL_CONFIG_STR)
        self._visibleVerticalGrid = self._configParser.getProperty(self._name, ConfigReader.BASESCOPE_VIS_VERTICAL_CONFIG_STR)
        self._nrOfChan = self._configParser.getProperty(self._name, ConfigReader.BASESCOPE_NROFCHAN_CONFIG_STR)
        
    @property
    def visibleHorizontalGrid(self):
        return self._visibleHorizontalGrid

    @property
    def visibleVerticalGrid(self):
        return self._visibleVerticalGrid
    
    @property
    def verticalGrid(self):
        return self._verticalGrid
    
    @property
    def horizontalGrid(self):
        return self._horizontalGrid

class BaseGeneratorConfig(BaseDeviceConfig):
    #TODO: maybe should this move to BaseScope.py?
    @classmethod
    def getConfigClass(cls, devName, baseType, derivedType):
        """ Tries to get (instantiate) the config object"""
        if baseType == "BaseGenerator":
            return (cls, devName)
        else:
            return (None, None)

    def __init__(self, devName, baseType, derivedType):
        super().__init__(devName, baseType, derivedType)

class BaseDMMConfig(BaseDeviceConfig):
    @classmethod
    def getConfigClass(cls, devName, baseType, derivedType):
        """ Tries to get (instantiate) the config object"""
        if baseType == "BaseDMM":
            return (cls, devName)
        else:
            return (None, None)

class BaseSupplyConfig(BaseDeviceConfig):
    @classmethod
    def getConfigClass(cls, devName, baseType, derivedType):
        """ Tries to get (instantiate) the config object"""
        if baseType == "BaseSupply":
            return (cls, devName)
        else:
            return (None, None)




    def __init__(self, devName, baseType, derivedType):
        super().__init__(devName, baseType, derivedType)
        
    

class LabcontrolConfig(object):
    """Class for managing the labcontrol.ini contents.
    Reading of labcontrol.ini: this class reads labcontrol.ini fully and creates a BaseDeviceConfig object
    for every entry (section) found in the ini file.
    Usage of LabcontrolConfig: every implementation of the baseclass of an instrument driver class, BaseScope 
    for instance, will query this class, if a config section is available for it. 
    If so, LabcontrolConfig will instantiate the proper BaseDeviceConfig derived object and return the handle
    to the quering instrument driver object.
    
    Description of internal operation:
    1. creation of LabcontrolConfig object -> traversal of labcontrol.ini and creation of an list 
    of BaseDeviceConfig Objects.
    2. Looking for suitable BaseDeviceConfig objects when asked for. Matching based on derived class type of
        the querying object.
        Return: a list of BaseDeviceConfig objects, or None if no match was found. 
    """
    def __init__(self):
        self._devConfigList = list()
        self._config = ConfigReader()
        self.readDevConfigs()

    def readDevConfigs(self):
        
        for devName in self._config.allSections():
            baseType = self._config.getProperty(devName=devName, prop=ConfigReader.BASE_TYPE_CONFIG_STR)
            derivedType = self._config.getProperty(devName=devName, prop=ConfigReader.DERIVED_TYPE_CONFIG_STR)
            newConfig = BaseDeviceConfig.getConfig(devName, baseType, derivedType)
            if newConfig != None:
                self._devConfigList.append(newConfig)

    def all_members(self, aClass):   
        try: 
            # Try getting all relevant classes in method-resolution order
            mro = list(aClass.__mro__)
        except AttributeError:
        # If a class has no _ _mro_ _, then it's a classic class
            def getmro(aClass, recurse):
                mro = [aClass]
                for base in aClass.__bases__: mro.extend(recurse(base, recurse))
                return mro
            mro = getmro(aClass, getmro)
        mro.reverse(  )
        members = {}
        for someClass in mro: members.update(vars(someClass))
        return members

    def find(self, classtype)->list:
        myList = list()
        for dev in self._devConfigList:
            mydev:BaseDeviceConfig = dev
            if classtype.__name__ == mydev._baseType:
                myList.append(dev)
        return myList
    

        
    