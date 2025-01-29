from typing import Any
import pyvisa as visa

"""
 een labapparaat wordt geindentificeerd door een modelnr => object
 resourcelist -> lijst met url -> lijst met idn strings -> lijst met modelnr
 
 initting van factory: drivers registreren zich bij de factory
   
 
"""
class LabDevice(object):
    
    @staticmethod
    def decodeIDN(idnStr) -> str:
        return "1234"
    
    
    def __init__(self) -> None:
        self._modelNr = None
        self._instance = None
        
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self._instance = LabDevice()
        return self._instance

class LabDeviceBuilder(object):
    def __init__(self):
        self._labdevices = None
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            #for labdev in self._labdevices:
            #    if labdev.decodeIDN(idnstr) == modelNo:
            self._instance = LabDevice()
        return self._instance  

"""
    LabDeviceFactory: instantiate the proper scope object based on the resourcelist and idn response.
    
    I/F: 
        when an application start, 
        1. it must first instatiate a LabDeviceFactory object
        2. it must add all the available implemented LabDevices by calling register_labdevice. 
            Every labdevice will register itself with its modeltypenumber (as the key), its nature
            (scope, generator, ...),  and idn.
        3. the Factory creates a url list of all found VISA instruments.
        4. the list will be traversed, every time:
            a. the current item of the list  will be opened and 
            b. the factory will call idnDecode() for every LabDevice in de registed LabDevices list.
            c. the idnDecode method will return true if decode was successfull, false otherwise
            d. if false, next LabDevice will try to decode the idn, until all Devices had their shot.
                if true, the Factory will return a LabDevice object.
            e. next element of the VISA instruments will be opened.   
"""


"""
see:https://realpython.com/factory-method-python/

class ObjectFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder): in geval van labdevice is idn de key.
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)

class PandoraService:
    def __init__(self, consumer_key, consumer_secret):
        self._key = consumer_key
        self._secret = consumer_secret

    def test_connection(self):
        print(f'Accessing Pandora with {self._key} and {self._secret}')

        
class PandoraServiceBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, pandora_client_key, pandora_client_secret, **_ignored):
        if not self._instance:
            consumer_key, consumer_secret = self.authorize(
                pandora_client_key, pandora_client_secret)
            self._instance = PandoraService(consumer_key, consumer_secret)
        return self._instance
        
        What must be the datastructure to hold the labdevice data
        1. {idn:{modelno, labdevtype, .....}}

"""
class LabDeviceFactory(object):
    def __init__(self) -> None:
        self._labdevices = {}
        
    def lab_start(self):
        #rm = visa.ResourceManager()
        #theList = rm.list_resources()
        #for url in theList:
            #mydev = rm.open_resource(url)
            #desc = mydev.query("*idn?")
        desc = "1122"
            #decode the response
        for modelId in self._labdevices:
            dev = self._labdevices.get(modelId)
            modelNo=dev.decodeIDN(desc)
                
            self.create(modelNo)
                   
        
    def register_labdevice(self, modelNo, builder):
        self._labdevices[modelNo] = builder
    
    def create(self, key, **kwargs):
        builder = self._labdevices.get(key)
        if not builder:
            print("modelno unkown!!")
        return builder(**kwargs)
    
    def idnDecode(self):
        pass
    
    def getInstrument(self):
        pass
        

class Channel(object):
    chanIDStr = "CH"
    
    @staticmethod
    def setChanIDstr(channelIdString="CH"):
        Channel.chanIDStr = str(channelIdString)
    @staticmethod
    def getChanIDstr():
        return str(Channel.chanIDStr)
    
    def __init__(self, chan_no, visaInstr) -> None:
        self._name = Channel.getChanIDstr() + str(chan_no)
        self._dev = visaInstr
        self._visible = False
    
    def setVisible(self, state:bool):
         pass
     
    def setTimeDiv(self):
        pass
    
    def setVoltsDiv(self):
        pass
    
    def capture(self):
        pass
    
    def queryWaveFormPreamble(self):
        pass
    
    def queryNrOfSamples(self):
        pass
    
    def isVisible(self):
        return self._isVisible

class IDN(object):
    def __init__(self) -> None:
        self._brand = None
        self._model = None
        self._serial = None
        self._firmware = None
        
    def decode(self, idnstr):
        pass

class Vertical(object):
    """
    Position
    Coupling: DC, AC, and GND
    Bandwidth: Limit and Enhancement
    Termination: 1M ohm and 50 ohm
    Offset
    Invert: On/Off
    Scale: Fixed Steps and Variable
    probe?
"""
    def __init__(self):
        pass
    
    def setVDiv(self, vdiv):
        pass
    
class Horizontal(object):
    """

    Acquisition
        Sample Mode: This is the simplest acquisition mode. The oscilloscope creates a waveform point by saving one sample point during each waveform interval.
        Peak Detect Mode
        Envelope Mode
        Average Mode
    Sample Rate
    Position and Seconds per Division
    Time Base
    Zoom/Pan
    Search
    XY Mode

"""
    def __init__(self):
        pass
    
    def setSecDiv(self, tdiv):
        pass
    
    def setSampleRate(self, srate):
        pass
    
class Trigger(object):
    """
        Trigger mode: normal, auto
        Trigger position
        Trigger level
        Trigger slope
        Trigger source
        Trigger Coupling
    """
    def __init__(self):
        pass
    
    

class Scope(LabDevice):
    def __init__(self, nrOfChan = 2) -> None:
        super().__init__()
        self._channels = []
        self._nrOfChan = nrOfChan
        self._visaInstr = None
        #Contains the first or first two letters designating a channel
        # We've two brands @ Elektrotechniek:  Tektronix and  Siglent
        #the tektonix has CH as first letters, but the Siglent has C
        #Therefore, the implementing class must overrid the channelID string
        self._chanIdStr = None 
        for chanNr in range(nrOfChan):
            self._channels.append(Channel(chanNr, self._visaInstr))
    
    
        
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self._instance = Scope()
        return self._instance
       
    def setTimeDiv(self):
        pass
    
    def setVoltsDiv(self):
        pass
    
    def queryWaveFormPreamble(self):
        pass
    
class FakeScope1(Scope):
    @staticmethod
    def decodeIDN(idnStr) -> str:
        return "FakeScope1122"
    
    def __init__(self, nrOfChan=2) -> None:
        super().__init__(nrOfChan)
        self._modelNr = "1122"
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self._instance = FakeScope1()
        return self._instance
        
    def __call__(self, idnstr, modelNo, **_ignored):
        return super().__call__(idnstr, modelNo, **_ignored)
        
    def setTimeDiv(self):
        print("Fake setTimeDiv")
    
    def setVoltsDiv(self):
        print("Fake setVoltsDiv")
    
    def queryWaveFormPreamble(self):
        print("Fake preamble")
    
        

class FakeScope2(Scope):
    @staticmethod
    def decodeIDN(idnStr) -> str:
        return "2211"
    
    def __init__(self, nrOfChan=2) -> None:
        super().__init__(nrOfChan)
        self._modelnr = "2211"
        
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self._instance = FakeScope2()
        return self._instance
        
    def setTimeDiv(self):
        print("Fake setTimeDiv")
    
    def setVoltsDiv(self):
        print("Fake setVoltsDiv")
    
    def queryWaveFormPreamble(self):
        print("Fake preamble")
    
      
factory = LabDeviceFactory()
factory.register_labdevice("1234",LabDevice())
factory.register_labdevice("1111", Scope())
factory.register_labdevice("2211", FakeScope2())

ding = factory.create("1234")
ding2 = factory.create("1111")
ding3 = factory.create("1111")
ding4 = factory.create("2211")

factory.lab_start()

print(ding)
print(ding2)
print(ding3)
print(ding4)  
    
    
"""
        Class for creating a set of Labdevices
        1. Traversing all subirs and reading all classes of __init__.py files
        2. Class which holds the interface will be loaded into the factory
        3. Then the rescourcemanager will look for VISA devices on the USB or network.
        4. Depending match real devices and available drivers, Labdevices will be returned
        5. Labdevices will be casted to their final class type.
"""
