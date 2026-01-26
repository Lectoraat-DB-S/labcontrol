import pyvisa as visa
import numpy as np

from devices.BaseScope import BaseHorizontal
from devices.siglent.sds.SDS2000.commands_full import SCPI
#commands_full import SCPI

class SDS2kHorizontal(BaseHorizontal):
    """Subclass of BaseHorizontal. Implements horizontal functionalities of the Siglent SDS2000X-E series oscilloscope.
    Horizontal functions are querying en setting the timebase, horizontal axis position and zoom factor.
    Avaialble Timebase functions according to Programming Guide EN11D:
     :TIMebase:DELay
     TIMebase REFerence
     TIMebase:REFerence:POSition
     :TIMebase:SCALe
     :TIMebase:WINDow
     :TIMebase:WINDow:DELay
     :TIMebase:WINDow:SCALe
    
    """
    #Timebases have to be converted to siglent, current values are tektronix.
    TIMEBASE_HASHMAP = {
                    "0":"5e-9","1": "10e-9", "2":"25e-9","3":"50E-9",
                    "4":"100e-9","5":"250e-9","6":"500e-9",
                    "7":"1e-6","8":"2.5e-6","9":"5e-6",
                    "10":"10e-6","11":"25e-6","12":"50e-6",
                    
                    "13":"100e-6","14":"250e-6","15":"500e-6",
                    "16": "1e-3", "17": "2.5e-3", "18": "5e-3",
                    "19": "10e-3", "20": "25e-3", "21": "50e-3",
                    "22": "100e-3", "23": "250e-3", "24": "500e-3",
                    "25": "1", "26": "2.5", "27": "5"
                    }
    
    @classmethod
    def getHorizontalClass(cls, dev):
        """
            Tries to get (instantiate) this device, based on matched cls
            This method will ONLY be called by the BaseScope class or other Scope related Baseclasses, 
            to instantiate the proper object during creation by the __new__ method according to PEP487.     
        """    
        if cls is SDS2kHorizontal:
            return cls
        else:
            return None   
         
    def __init__(self, dev = None):
        #super().__init__(dev)
        self.visaInstr = dev
        self.TB = 0.0                  # current value of timebase, unit sec/div
        self.SR = 0                    # samplerate
        self.POS = 0                   # Horizontal position in screen (of the waveforms)
        self.ZOOM = 0                  # Horizontal magnifying. 
    
    def setRoll(self, flag:bool):
        """Not implemented yet."""
        pass       


    def setIimeBase(self, value):
        """Set the time per devision for this oscilloscoop. The sds1k scope isn't as flexible as a Tektronix TDS. This scope
        seems/appears to have the same flexibility as the Tektronix TDS. But is not yet tested. Therefore, is method used the
        old sds1k way of doing. TODO: check out whether or not sds2k has coarse/fine timebase control.
        """
        
        strValue = str(value)
        if strValue in SDS2kHorizontal.TIMEBASE_HASHMAP:
            val2Set = value
        else: # no corresponding setting available for value. Find nearest option.
            hulp = SDS2kHorizontal.TIMEBASE_HASHMAP
            hulp2 = np.array(hulp.values())
            print(hulp2[hulp2>value])
            print(hulp2[hulp2>value])
            
        self.visaInstr.write(SCPI["TIMEBASE"]["scale"](val2Set))

    def getTimeBase(self):
        return self.visaInstr.query(SCPI["TIMEBASE"]["scale?"]())
        
    def setTimeDiv(self, value):
        self.setIimeBase(value)

    def setDelay(self, val):
        """Sets the main timebase delay. This delay is the time between the trigger event and the 
        delay reference point on the screen. The range of the value is 5000div timebase, 5div timebase]."""
        #TODO: check if value of val falls within range.
        self.visaInstr.write(SCPI["TIMEBASE"]["delay"](val))

    def getDelay(self):
        """Method for getting the current set delay of the timebase."""
        return self.visaInstr.query(SCPI["TIMEBASE"]["delay?"]())

    def setRefPos(self, value:int):
        """Method for setting the reference, or zero point, in case of a timebasedelay."""
        if value > 0 and value <101:
            self.visaInstr.write(SCPI["TIMEBASE"]["reference"](value))

    def getRefPos(self):
        """Method for getting the reference, or zero point, in case of a timebasedelay."""
        return self.visaInstr.query(SCPI["TIMEBASE"]["reference?"]())
        

    def setWindowZoom(self, state:bool):
        """Method for setting the state of the timebase zoom funcion. """
        newState = "ON"
        if state or state == "ON" or state == "1":
            newState = "ON"
        else:
            newState = "OFF"            
        self.visaInstr.write(SCPI["TIMEBASE"]["window"](newState))

    def getWindowZoom(self, state:bool):
        """Gets the current state of the zoomed timebase window: on or off."""
        return self.visaInstr.query(SCPI["TIMEBASE"]["window?"]())

    def setWindowDelay(self, val):
        """Sets the horizontal position in the zoomed view of the main sweep."""
        #TODO: check the validity of val.
        self.visaInstr.write(SCPI["TIMEBASE"]["windelay"](val))
        
    def getWindowDelay(self):
        """Gets the amount of delay set in the Timebase delay window."""
        return self.visaInstr.query(SCPI["TIMEBASE"]["windelay?"]())


    def setWindowScale(self, val):
        """Method for setting the zoomed window horizontal scale (sec/div)"""
        self.visaInstr.write(SCPI["TIMEBASE"]["winscale"](val))
    
    def getWindowScale(self, val):
        """Gets the amount of time/division set for the zoomed timebase."""
        return self.visaInstr.query(SCPI["TIMEBASE"]["winscale?"]())