import pyvisa as visa
import numpy as np
import time
import struct

from devices.BaseScope import BaseHorizontal

from devices.tektronix.scope.Acquisitions import TekTrace, WaveformPreamble

from devices.tektronix.scope.TekLogger import TekLog
from devices.tektronix.scope.Acquisitions import TekScopeEncodings

class TekHorizontal(BaseHorizontal):
    
    TIMEBASE_HASHMAP = {
                    "0":"200e-12","1": "500e-12", "2":"1e-9","3":"2E-9",
                    "4":"5e-9","5":"10e-9","6":"20e-9","7":"50e-9",
                    "8":"100e-9","9":"200e-9","10":"500e-9",
                    "11":"1e-6","12":"2e-6","13":"5e-6",
                    "14":"10e-6","15":"20e-6","16":"50e-6",
                    "17":"100e-6","18":"200e-6","19":"500e-6",
                    "20": "1e-3", "21": "2e-3", "22": "5e-3",
                    "23": "10e-3", "24": "20e-3", "25": "50e-3",
                    "26": "100e-3", "27": "200e-3", "28": "500e-3",
                    "29": "1", "30": "2", "31": "5",
                    "32": "10", "33": "20", "34": "50",
                    "35": "100"
                    }
    
    # @classmethod
    # def getHorizontal(cls, dev):
    #     """
    #         Tries to get (instantiate) this device, based on matched cls
    #         This method will ONLY be called by the BaseScope class or other Scope related Baseclasses, 
    #         to instantiate the proper object during creation by the __new__ method according to PEP487.     
    #     """    
    #     if cls is TekHorizontal:
    #         cls.__init__(cls, dev)
    #         return cls
    #     else:
    #         return None   
    # def __new__(cls):
    #     return super().__new__()     
         
    def __init__(self, dev = None):
        super().__init__(dev)
    
    def getTimeDivs(self):
        return TekHorizontal.TIMEBASE_HASHMAP
    
    def setRoll(self, flag:bool):
        print("Let's Roll")
        return None