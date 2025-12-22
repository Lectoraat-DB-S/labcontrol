import pyvisa
import numpy as np
from devices.BaseScope import BaseDisplay

class SDSDisplay(BaseDisplay):
    """"Subclass of BaseDisplay for Tektronix TDS1k en 2k scope series. This class implements the BaseDisplay baseclass."""

    @classmethod
    def getDisplayClass(cls):
        """ Tries to get (instantiate) the device"""
        if cls is SDSDisplay:
            return (cls)
        else:
            return None   
        
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        super().__init__(visaInstr)

    def format(self):
        
        return self.visaInstr.query("XY_DISplay?")

    def format(self, mode):
        if mode == "YT":
            #XY_DISPLAY <state>
            self.visaInstr.write(f"XY_DISPLAY OFF")
        elif mode == "XY":
            self.visaInstr.write(f"XY_DISPLAY ON")
        return
    
    def persist(self):
        return self.visaInstr.query("PERSist?")
    
    def persist(self, persmode):
        #valid setups are 1，5，10，30,Infinite
        if persmode == "OFF" or persmode == 0:
            self.visaInstr.write(f"PERSist OFF")
        elif  persmode == "ON" or persmode == 1:
            self.visaInstr.write(f"PERSist ON")
        elif persmode == "Infinite":
            self.visaInstr.write(f"PESU Infinite")
            self.visaInstr.write(f"PERS ON")
        elif persmode == 1 or persmode == 5 or persmode == 10 or persmode == 30:
            self.visaInstr.write(f"PESU {persmode}")
            self.visaInstr.write(f"PERS ON")
        return
        
