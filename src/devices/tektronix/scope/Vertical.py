import pyvisa as visa
import numpy as np
from devices.BaseScope import BaseVertical

class TekVertical(BaseVertical):
         
    @classmethod
    def getVertical(cls, nrOfChan, dev):
        """ Tries to get (instantiate) the device, based on the url"""
        if cls is TekVertical:
            cls.__init__(cls, 2, dev)
            return cls
        else:
            return None            
        

    def __init__(self, nrOfChan = 0, dev = None):
        self._channels = list()           
        self._nrOfChan = nrOfChan      
        self._visaDev = dev             # default value = None, see param
    
    @property
    def channels(self):
        """Getter for retrieving the available channels of this oscilloscope"""
        return self._channels
    
    @property
    def nrOfChan(self):
        """Getter for retrieving number of the available channels of this oscilloscope"""
        return self._nrOfChan
    