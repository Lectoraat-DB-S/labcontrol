import pyvisa as visa

class LabDevice(object):
    def __init__(self) -> None:
        pass
    
    def idnDecode(self):
        pass
    
    def getInstrument(self, dev):
        #create the instrument by passing the open Visainstrument handle to it.
        return self	
     

"""
    LabDeviceFactory: instantiate the proper scope object based on the resourcelist and idn response.
    
    I/F: 
        when an application start, 
        1. it must first instatiate a LabDeviceFactory object
        2. it must add all the available implemented LabDevices by calling register_labdevice
        3. the Factory creates a url list of all found VISA instruments.
        4. the list will be traversed, every time:
            a. the current item of the list  will be opened and 
            b. the factory will call idnDecode() for every LabDevice in de registed LabDevices list.
            c. the idnDecode method will return true if decode was successfull, false otherwise
            d. if false, next LabDevice will try to decode the idn, until all Devices had their shot.
                if true, the Factory will return a LabDevice object.
            e. next element of the VISA instruments will be opened.   
"""

class LabDeviceFactory(object):
    def __init__(self) -> None:
        self._labdevices = []
        rm = visa.ResourceManager()
        theList = rm.list_resources()
        for url in theList:
            mydev = rm.open_resource(url)
            desc = mydev.query("*idn?")
            #decode the response
            for dev in self._labdevices:
                result=dev.idnDecode(desc)
                if result:
                    return dev.getLabDevice(mydev)
                
        
    def register_labdevice(self):
        pass
    
    def idnDecode(self):
        pass
    
    def getInstrument(self):
        pass
        

class Channel(object):

    def setChanIDstr(channelIdString="CH"):
        chanIDStr = str(channelIdString)
    
    def __init__(self, chan_no, visaInstr) -> None:
        self._name = Channel.setChanIDstr + f"{chan_no}"
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

class Scope(object):
    
    def __init__(self, nrOfChan = 2) -> None:
        self._channels = []
        self._nrOfChan = nrOfChan
        #Contains the first or first two letters designating a channel
        # We've two brands @ Elektrotechniek:  Tektronix and  Siglent
        #the tektonix has CH as first letters, but the Siglent has C
        #Therefore, the implementing class must overrid the channelID string
        self._chanIdStr = None 
        for chanNr in range(nrOfChan):
            self._channels.append(Channel(chanNr))
        
        
    def setTimeDiv(self):
        pass
    
    def setVoltsDiv(self):
        pass
    
    def queryWaveFormPreamble(self):
        pass
    
class IDN(object):
    def __init__(self) -> None:
        self._brand = None
        self._model = None
        self._serial = None
        self._firmware = None
        
    def decode(self, idnstr):
        pass