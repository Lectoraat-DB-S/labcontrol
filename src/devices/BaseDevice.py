import pyvisa

class BaseInstrument(object):
    instrumentList = []        
    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseInstrument subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.instrumentList.append(cls)
         
    @classmethod
    def getInstrumentClass(cls, rm, urls, host=None):
        """Method for getting the right type of instrument, so it can be created by the runtime.
        This BaseInstrument implementation does nothing other than returning the BaseInstrument type. The inheriting
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

        for instrument in cls.instrumentList:
            instrtype, dev = instrument.getInstrumentClass(rm, urls, host)
            if instrtype != None:
                cls = instrtype # check if the type of this class corresponds with the identiy of the instrument.
                return cls(dev)
            
        return None # if getDevice can't find an instrument, return None.

    def __init__(self, instr:pyvisa.resources.MessageBasedResource=None):
        self.visaInstr: pyvisa.resources.MessageBasedResource = instr

class LabEnvironment(object):
    visa_error_resp      = ["error"]
    visa_sim_error_resp  = ["error"]
    VISA_DEVICE_IDN_ERROR = "IDN_ERROR"
    VISA_DEVICE_OPEN_ERROR = "ERROR_CONNECTING_VISADEVICE"
    VISA_DEVICE_QUERY_ERROR = "ERROR_QUERING_VISADEVICE"
    
    simulationMode = False
    pyvisaResMan = None
    pyvisaResUrls = None
    pyvisaIsdns = None
    
    @classmethod
    def setSimulation(cls, simulate=False):
        cls.simulationMode = simulate
        
    
    @classmethod
    def getVisaRM(cls):
        if cls.simulationMode:
            cls.pyvisaResMan = pyvisa.ResourceManager("@sim")
        else:
            cls.pyvisaResMan = pyvisa.ResourceManager()
        return cls.pyvisaResMan
    
    @classmethod
    def getVisaUrls(cls):
        
        cls.getVisaRM()

        cls.pyvisaResUrls = cls.pyvisaResMan.list_resources()
        return cls.pyvisaResUrls
    
    @classmethod
    def getVisaIsdns(cls):
        
        cls.pyvisaIsdns = list()
        cls.getVisaUrls()
        for url in cls.pyvisaResUrls:
            rm = cls.getVisaRM()
            try:
                dev = rm.open_resource(url, open_timeout=500)
                if dev != None:
                    try:
                        idn = dev.query("*IDN?")
                        if idn in LabEnvironment.visa_error_resp:
                            cls.pyvisaIsdns.append({url, LabEnvironment.VISA_DEVICE_IDN_ERROR})
                        elif idn in LabEnvironment.visa_sim_error_resp: 
                            cls.pyvisaIsdns.append({url, LabEnvironment.VISA_DEVICE_IDN_ERROR})
                        elif idn == "" or idn == None:
                            cls.pyvisaIsdns.append({url, LabEnvironment.VISA_DEVICE_IDN_ERROR})
                        else:
                            cls.pyvisaIsdns.append({url,idn}) #a succesfull open + idn
                    except:
                        #url can be openened but idn query failed, skip the url
                        cls.pyvisaIsdns.append({url,LabEnvironment.VISA_DEVICE_QUERY_ERROR})        
                #dev.close()   #Q?        
            except:
                #skip this url
                cls.pyvisaIsdns.append({url,LabEnvironment.VISA_DEVICE_OPEN_ERROR})
    
        cls.pyvisaResMan.close()
        cls.pyvisaResMan = None
        return cls.pyvisaIsdns
    
    
    
    def __init__(self, debug=False, simulate=False):
        self._idns = None
        self._sim = simulate
        self._debug = debug
        self._rm = self.resourceManager(simulate)
        self._urls = self.urls()
        if self._urls == None:
            return
        
        self._idns = list()
        self._idns = self.idns()
             
    @property
    def resourceManager(self):
        if self._rm != None:
            try:
                self._rm.close()
                self._rm = None
            except:
                self._rm = None
        if self._sim:
            self._rm = pyvisa.ResourceManager("@sim")
        else:
            self._rm = pyvisa.ResourceManager()
        return self._rm
    
    @property
    def idns(self):
        return self._urls

    @property
    def urls(self):
        if self._rm == None:
            self.resourceManager()
        else:
            self._urls = self._rm.list_resources()
        return self._urls
    
    @property
    def idns(self):
        #self.resourceManager()
        #self.urls()
        self._idns = list()
        if self._rm == None:
            self.resourceManager()
            self.urls()
        for url in self._urls:
            try:
                dev = self._rm.open_resource(url)
                if dev != None:
                    try:
                        idn = dev.query("*IDN?")
                        if idn in LabEnvironment.visa_error_resp:
                            self._idns.append({url, LabEnvironment.VISA_DEVICE_IDN_ERROR})
                        elif idn in LabEnvironment.visa_sim_error_resp: 
                            self._idns.append({url, LabEnvironment.VISA_DEVICE_IDN_ERROR})
                        elif idn == "" or idn == None:
                            self._idns.append({url, LabEnvironment.VISA_DEVICE_IDN_ERROR})
                        else:
                            self._idns.append({url,idn}) #a succesfull open + idn
                    except:
                        #url can be openened but idn query failed, skip the url
                        self._idns.append({url,LabEnvironment.VISA_DEVICE_QUERY_ERROR})        
                #dev.close()   #Q?        
            except:
                #skip this url
                self._idns.append({url,LabEnvironment.VISA_DEVICE_OPEN_ERROR})
    
        self._rm.close() 
            
        