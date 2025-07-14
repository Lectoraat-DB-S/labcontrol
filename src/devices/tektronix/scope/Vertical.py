import pyvisa as visa
import numpy as np
from devices.BaseScope import BaseVertical
from devices.tektronix.scope.Channel import TekChannel

class TekVertical(BaseVertical):
    """"Subclass of BaseVertical for Tektronix TDS1000 scope series. This class implements the baseclass."""

    @classmethod
    def getVerticalClass(cls, dev):
        """ Tries to get (instantiate) the device, based on the url"""
        if cls is TekVertical:
            return (cls, 2)
        else:
            return None   

    def __init__(self, nrOfChan, dev):
        super().__init__(nrOfChan, dev) # visa dev will be initted by the Baseclass
        self.nrOfChan = nrOfChan
        self.channels =list()
        
        for i in range(1, nrOfChan+1):
            self.channels.append({i:TekChannel(i, dev)})
            
    def chan(self, chanNr): 
        """Gets a channel, based on its index: 1, 2 etc."""
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None     
        
    def getMathSettings(self):
        """
        queries the current math setting of a TDS.
        MATH? will response will look like:
        MATH:DEFINE "FFT(CH1,HANNING)";
        VERTICAL:POSITION 0.0E0;SCALE 1.0E0;
        :MATH:FFT:HORIZONTAL:POSITION 5.0E1;SCALE1.0E0;
        :MATH:FFT:VERTICAL:POSITION 0.0E0;SCALE 1.0E0"""
        return self.visaInstr.query("MATH?")
