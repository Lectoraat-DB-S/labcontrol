import pyvisa as visa
import numpy as np
from prefixed import Float   

from devices.BaseScope import BaseHorizontal

class SDSHorizontal(BaseHorizontal):
    """Subclass of BaseHorizontal. Implements horizontal functionalities of the Siglen SDS1202X-E oscilloscope. Horizontal functions are
    querying en setting the timebase, horizontal axis position and zoom factor."""
    
    TIMEBASE_HASHMAP = {
                    "0":1e-9,"1":2e-9,"2": 5e-9,
                    "3":10e-9,"4":20e-9,"5": 50e-9,
                    "6":100e-9,"7":200e-9,"8": 500e-9,
                    "9":1e-6,"10":2e-6,"11":5e-6,
                    "12":10e-6,"13":20e-6,"14":50e-6,
                    
                    "15":100e-6,"16":250e-6,"17":500e-6,
                    "18": 1e-3, "19": 2e-3, "20": 5e-3,
                    "21": 10e-3, "22": 2e-3, "23": 50e-3,
                    "24": 100e-3, "25": 200e-3, "26": 500e-3,
                    "27": 1, "28": 2, "29": 5,
                    "30": 10, "31": 20, "32": 50
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
        """Set the time per devision for this oscilloscoop. This scope isn't as flexible as a Tektronix TDS.
        The TDS has a coarse and a fine mode on setting tdiv. Siglent only accepts the predefined values of the range.
        It seems the scope ignores a value if it is above a predefined value.
        """
        myValArray = np.array((list(SDSHorizontal.TIMEBASE_HASHMAP.values())))
        
        if value in myValArray:
            val2Set = value
        else: # no corresponding setting available for value. Find nearest, first bigger option.
            
            myIndices = ( (myValArray>value).nonzero()[0])
            if len(myIndices)==0:
                val2Set = myValArray[-1]

            else:    
                val2Set = myValArray[myIndices[0]]
           
            
        self.visaInstr.write(f"Time_DIV {val2Set}")
        
    def setTimeDiv(self, value):
        self.setIimeBase(value)
