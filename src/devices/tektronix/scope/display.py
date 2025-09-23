import pyvisa
import numpy as np
from devices.BaseScope import BaseDisplay

class TekDisplay(BaseDisplay):
    """"Subclass of BaseDisplay for Tektronix TDS1k en 2k scope series. This class implements the BaseDisplay baseclass."""

    @classmethod
    def getDisplayClass(cls):
        """ Tries to get (instantiate) the device"""
        if cls is TekDisplay:
            return (cls)
        else:
            return None   
        
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        super().__init__(visaInstr)

    def format(self):
        
        return self.visaInstr.query("DISplay:FORMat?")

    def format(self, mode):
        if mode == "YT" or mode == "XY":
            self.visaInstr.write(f"DISPLAY:FORMAT {mode}")
        return
    
    def persist(self):
        return self.visaInstr.query("DISplay:PERSistence?")
    
    def persist(self, persmode):
        if persmode == "OFF" or persmode == "INF" or persmode == 1 or persmode == 2 or persmode == 5:
            self.visaInstr.write(f"DISPLAY:FORMAT {persmode}")
        elif persmode == 0:
            self.visaInstr.write(f"DISPLAY:FORMAT OFF")
        else:
            self.visaInstr.write(f"DISPLAY:FORMAT INF")
        return
        
