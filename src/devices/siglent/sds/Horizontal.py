import pyvisa as visa
import numpy as np

from devices.BaseScope import BaseHorizontal

class SDSHorizontal(BaseHorizontal):
    """Subclass of BaseHorizontal. Implements horizontal functionalities of the Tektronix TDS2002x oscilloscope. Horizontal functions are
    querying en setting the timebase, horizontal axis position and zoom factor."""
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
        if cls is SDSHorizontal:
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
    
    def setIimeBase(self, value):
        """The query returns the parameters of the source using by the command
        :WAVeform:SOURce.
        See text output from a Siglent scope for reference. See Repo.
        """
        self.visaInstr.write(f"Time_DIV {value}")
        
    def setTimeDiv(self, value):
        self.setIimeBase(value)
