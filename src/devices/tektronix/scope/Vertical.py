import pyvisa as visa
import numpy as np
from devices.BaseScope import BaseVertical
from devices.tektronix.scope.Channel import TekChannel

class TekVertical(BaseVertical):
    """"Subclass of BaseVertical for Tektronix TDS1000 scope series. This class implements the baseclass."""

    VDIV_HASHMAP = {
                    "0":"2e-3", "1":"5e-3", "2":"10e-3",
                    "3":"20e-3", "4":"50e-3", "5":"100e-3",
                    "6":"200e-3", "7":"500e-3", "8":"1.00",
                    "9":"2.00", "10":"5.00"
                    }
    @classmethod
    def getVerticalClass(cls, dev):
        """ Tries to get (instantiate) the device, based on the url"""
        if cls is TekVertical:
            return (cls, 2)
        else:
            return None   

    def __init__(self, nrOfChan, dev, nHDivs = 10, nVDivs = 10 , visHDivs = 10, visVDivs = 8):
        super().__init__(nrOfChan, dev) # visa dev will be initted by the Baseclass
        self.perMeasDict = {}
        self.nrOfChan = nrOfChan
        self.channels =list()
        self.nrOfHoriDivs = nHDivs # maximum number of divs horizontally
        self.nrOfVertDivs = nVDivs # maximum number of divs vertically 
        self.visibleHoriDivs = visHDivs # number of visible divs on screen
        self.visibleVertDivs = visVDivs # number of visible divs on screen
        
        for i in range(1, nrOfChan+1):
            self.channels.append({i:TekChannel(i, dev, self.perMeasDict)})
            
    def chan(self, chanNr): 
        """Gets a channel, based on its index: 1, 2 etc.
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None     
        """
        return super().chan(chanNr)
    
    def setProcMode(self, mode):
        super().setProcMode(mode)
        
    def getMathSettings(self):
        """
        queries the current math setting of a TDS.
        MATH? will response will look like:
        MATH:DEFINE "FFT(CH1,HANNING)";
        VERTICAL:POSITION 0.0E0;SCALE 1.0E0;
        :MATH:FFT:HORIZONTAL:POSITION 5.0E1;SCALE1.0E0;
        :MATH:FFT:VERTICAL:POSITION 0.0E0;SCALE 1.0E0"""
        return self.visaInstr.query("MATH?")
    
    def getVerticalSettings(self):
        queryResStr = ""
        channr = 1
        for channel in self.channels:
            if channr != 1:
                queryResStr += ";:"
            chan:TekChannel = channel[channr]
            chanQueryStr = self.visaInstr.query(f"{chan.name}?")
            queryResStr+=chanQueryStr
            channr=channr + 1
        return self.visaInstr.query(queryResStr)
            

