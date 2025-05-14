import pyvisa
#from pyvisa import ResourceManager as resman
#import labcontrol
#import devices.tektronix.scope.TekScopes #Gives circular import problem

class BaseScope(object):
    """BaseScope: base class for oscilloscope implementation.
    This code of this class also reflects the learning curve on Python.
        https://realpython.com/python-property/"""
    scopeList = []        
    
    def __init_subclass__(cls, **kwargs):
        """BaseScope: base class for oscilloscope implementation.
        Implementations for oscilloscopes have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getDevice(cls, url):
        3. Be sure BaseScope's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. """
        super().__init_subclass__(**kwargs)
        cls.scopeList.append(cls)
         
    @classmethod
    def getScopeClass(cls, rm, urls, host=None):
        """ Tries to get (instantiate) the device, based on the url"""
        return None #Base class implementation: return None, because this class can't do shit.
    
        
    #def __new__(cls, host: str=None):
        """New: creation of object. 
        Only BaseScope may call this new methond as the first step in creation of a scope object. 
        This is a way to controll if an object will be returned from a new method and if so, which type of object
        it will have to return, as a form of factory pattern. 
        See also: https://mathspp.com/blog/customising-object-creation-with-__new__ 
        This coding scheme requires (automatic) registration of subclasses according pep487:
        see: https://peps.python.org/pep-0487/      
        """
        
        """
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()

        for scope in cls.scopeList:
            scopetype, dev = scope.getScopeClass(rm, urls, host)
            if scopetype != None:
                #return super().__new__(scopeobj, visaInstr = dev)
                scopeobj = super().__new__(scopetype)
                cls.__init__(cls, None, dev)
                scopeobj.__init__(scopeobj, None, dev)
                return scopeobj
                
            
        return super().__new__(cls)
        """
    @classmethod
    def getScope(cls,host=None):
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()

        for scope in cls.scopeList:
            scopetype, dev = scope.getScopeClass(rm, urls, host)
            if scopetype != None:
                cls = scopetype
                return cls(host, dev)


    def __init__(self, host: str=None, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """abstract init function. A subclass should be override this function, which wil intitialize the final object. Remark: if the subclass 
        wants to use intialisation done below, it must call super().__init()__ first!"""
        self.brand = None
        self.model = None
        self.serial = None
        self.firmware = None
        self.visaInstr : pyvisa.resources.MessageBasedResource = visaInstr
        self.horizontal = BaseHorizontal(visaInstr)
        self.vertical = BaseVertical(visaInstr)
        self.trigger = None
        self.utility = None
        self.host = None
        
    #@property 
    def visaInstr(self) -> pyvisa.resources.MessageBasedResource: 
        """The reference to a visaInstrument object has to be created during creation of the object @init, which is a reason for the 
        programmer not to implement this as immutable property and not implement any kind of setter method for this property, nor in this class,
        nor in any derived class.
            """
        return self.visaInstr
###################################### BASECHANNEL #########################################################
class BaseChannel(object):
    channelList = []

    def __init_subclass__(cls, **kwargs):
        """BaseChannel: baseclass for oscilloscope (vertical) channel implementation.
        Implementations for oscilloscopes channels have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getChannel method:
        3. Be sure BaseChannel's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. """
        super().__init_subclass__(**kwargs)
        cls.channelList.append(cls)
    
    @classmethod
    def getChannelClass(cls, dev):
        """getChannelObject: factory method for scope channel objects. Remark: this baseclass implementation is empty """
        pass

    def __new__(cls, chan_no: int, visaInstr:pyvisa.resources.MessageBasedResource):
        """New: creation of object. 
        """
        #to have Pylance detect the proper type of a variable, call this!

        for channel in cls.channelList:
            if channel is cls:
                chanObj = channel.getChannelClass(chan_no, visaInstr)
                if chanObj != None:
                    return super().__new__(chanObj)
        
        return super().__new__(cls)     

    def __init__(self, chan_no: int, visaInstr:pyvisa.resources.MessageBasedResource):
        self.visaInstr = visaInstr
        self.chanNr = chan_no
        self.WF = BaseWaveForm()            # the waveform ojbect of this channel
        self.WFP = BaseWaveFormPreample(visaInstr) # the waveformpreamble object for this channel
        
        
    def capture(self):
        """Gets the waveform from the oscilloscope, by initiating a new aqquisition. This BaseChannel implementation is empty.  
        An inheriting subclass wil have to implement this method by sending the proper SCPI commands 
        in order need to a. get waveform descriptors, b. get the raw data and take care for store it into the proper datastructures"""
        pass

    def getAvailableMeasurements(self):
        pass
    
    def getMean(self):
        pass

    def getMax(self):
        pass
    
        
########## BASEVERTICAL ###########
    
class BaseVertical(object):
    VerticalList = list()
    #type ChanList = list[BaseChannel]

    @classmethod
    def getVerticalClass(cls, dev):
        """ Tries to get (instantiate) the device, based on the url"""
        return None #Base class implementation: return None, because this class doesn't do any shit.

    
    def __init_subclass__(cls, **kwargs):
        """BaseScope: base class for oscilloscope implementation.
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod 
        def getDevice(cls, url):
        4. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        3. Use Python's properties, for the getter-setter mechanisme, See: https://realpython.com/python-property/"""
        super().__init_subclass__(**kwargs)
        cls.VerticalList.append(cls)

    def __new__(cls,nrOfChan=0, dev:pyvisa.resources.MessageBasedResource=None): 
        
        for verti in cls.VerticalList:
            if verti is cls:
                vertiObj, myNrOfChan = verti.getVerticalClass(dev)
                if vertiObj != None:
                    return super().__new__(vertiObj)
        
        return super().__new__(cls)  
    
    #def __set_name__(self, owner, name):
    #    self.key = name
         
    
    def __init__(self, nrOfChan: int = 0, dev:pyvisa.resources.MessageBasedResource = None):
        self.channels = []          
        self.nrOfChan = nrOfChan       # A virtual Baseclass: so no channels available.
        self.visaInstr = dev             # default value = None, see param
    
    #def chan(self, chanNr:int):          
    def chan(self, chanNr)->BaseChannel: 
        """Get the channel obejct based on the number. This method should be overridden by the 
        inherting subclass, as this BaseVertical implementation is empty."""
        pass
    
############ BaseHorizontal ###########
class BaseHorizontal(object):
    HorizontalList = list()
    
    def __init_subclass__(cls, **kwargs):
        """BaseHorizontal: base class for oscilloscope implementation.
        Implementation of real supplies have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod 
        def getDevice(cls, url):
        4. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        3. Use Python's properties, for the getter-setter mechanisme, See: https://realpython.com/python-property/"""
        super().__init_subclass__(**kwargs)
        cls.HorizontalList.append(cls)
    
    @classmethod
    def getHorizontalClass(cls, dev):
        return cls
        
    def __new__(cls,dev:pyvisa.resources.MessageBasedResource=None):
        
        for hori in cls.HorizontalList:
            if hori is cls:
                horiObj = hori.getHorizontalClass(dev)
                if horiObj != None:
                    #return super().__new__(horiObj, dev)
                    return super().__new__(horiObj)
        return super().__new__(cls)     
          
    def __init__(self, dev:pyvisa.resources.MessageBasedResource= None):
        self.visaInstr = dev             # default value = None, see param
        self.TB = 0.0                  # current value of timebase, unit sec/div
        self.SR = 0                    # samplerate
        self.POS = 0                   # Horizontal position in screen (of the waveforms)
        self.ZOOM = 0                  # Horizontal magnifying.

    def setRoll(self, flag:bool):
        """Method for setting horizontal roll (true/false). This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass       
    
    def getTimeDivs(self):
        """Method for getting available timebase setting. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""    
        pass

    def setTimeDiv(self, value):
        """Method for setting a timebase vaule. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""    
        pass

######################################## BASEWAVEFORM #########################################################
class BaseWaveForm(object):

    WaveFormList = list()

    def __init_subclass__(cls, **kwargs):
        """BaseWaveForm: a base class for holding a channels waveform data.
        Implementation of real scopes have to subclass their waveform implementations from this class. Reason for
        doing so:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod 
        def getDevice(cls, url):
        3. Be sure BasewaveForm's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        """
        super().__init_subclass__(**kwargs)
        cls.WaveFormList.append(cls)

    @classmethod
    def getWaveFormClass(cls):
        return cls
        
    def __new__(cls):
        
        for wave in cls.WaveFormList:
            if wave is cls:
                waveObj = wave.getWaveFormClass()
                if waveObj != None:
                    return  super().__new__(waveObj)
        
        return  super().__new__(cls)     
    
    def __init__(self):
        """Class for holding waveform data of a channel capture and the methods to transform raw sample data into soming fysical meaningful, such as voltage."""
        
###################################### BASECWAVEFORMPREAMBLE ###################################################
class BaseWaveFormPreample(object):
    """A WaveFormPreamble (WFP) is a kind of struct which holds relevant data about a channel capture. Based on WFP data, the WaveForm object is able to convert raw samples to
    measured voltages (vertical data) and samplenumbers to time of frequency instances. (x, t or f data)"""
    WaveFormPreambleList = list()

    @classmethod
    def getWaveFormPreableClass(cls, dev:pyvisa.resources.MessageBasedResource=None):
        pass

    def __init_subclass__(cls, **kwargs):
        """BaseWaveFormPreambel: a base class for holding a channels waveform Preambel data.
        Implementation of real scopes have to subclass their waveform implementations from this class. Reason for
        doing so:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod 
        def getWaveFormPreableObject(cls, dev):
        3. Be sure BasewaveForm's constructor has access to the inheriting subclass during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        """
        super().__init_subclass__(**kwargs)
        cls.WaveFormPreambleList.append(cls)
    
    def __new__(cls, dev:pyvisa.resources.MessageBasedResource=None):
        
        for preamble in cls.WaveFormPreambleList:
            if preamble is cls:
                wavePreObj = preamble.getWaveFormPreambleClass(dev)
                if wavePreObj != None:
                    return super().__new__(wavePreObj) 
        
        return super().__new__(cls) 

    def __init__(self, dev:pyvisa.resources.MessageBasedResource=None):
        self.visaInstr = dev

    def queryPreamble(self):
        """Method for getting the preamble of the scope and set the correct data members
        of a preamble. This baseclass has no implementation."""
        pass
        

###################################### BASETRIGGERUNIT #########################################################
class BaseTriggerUnit(object):
    """The base software representation of a triggerunit. This class has an empty implementation. An inheriting 
    subclass will have to implement desired behaviour"""
    triggerUnitList = []

    @classmethod
    def getTriggerUnitClass(cls, vertical:BaseVertical,visaInstr:pyvisa.resources.MessageBasedResource=None):
        """Method for getting the right Python type, or the proper subclass of BaseTriggerUnit, based on parameters
        passed. 
            """
        return cls
    
    def __init_subclass__(cls, **kwargs):
        """Method for autoregistration of BaseTriggerUnit subclasses. Don't alter and don't override. Be sure this
        the"""
        super().__init_subclass__(**kwargs)
        cls.triggerUnitList.append(cls)
    
    def __new__(cls, vertical:BaseVertical = None, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """New: creation of an object, or instance. 
        Only BaseTriggerUnit may call this new method for creating an object based on the correct type, as a kind
        of factory pattern. To get the right type __new__ will call getTriggerUnitClass methods from every subclass
        known to BaseTriggerUnit
        See also: https://mathspp.com/blog/customising-object-creation-with-__new__ 
        This coding scheme requires (automatic) registration of subclasses according pep487:
        see: https://peps.python.org/pep-0487/      
        """
        
        for trigger in cls.triggerUnitList:
            if trigger is cls:
                triggerUnitObj = trigger.getTriggerUnitClass(vertical, visaInstr)
                if triggerUnitObj != None:
                    return super().__new__(triggerUnitObj) 
        
        return super().__new__(cls)      

    
    def __init__(self, vertical:BaseVertical=None, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """"Method voor initialisation of the BaseTriggerUntit object."""
        self.vertical = vertical
        self.visaInstr = visaInstr
        self.source = None #the channel to trigger on.
        self.level =None
        
    