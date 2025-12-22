import pyvisa
import numpy as np
from devices.BaseScope import BaseVertical
from devices.siglent.sds.SDS2000.Channel import SDS2kChannel



class SDS2kVertical(BaseVertical):
    """"Subclass of BaseVertical for Tektronix TDS1000 scope series. This class implements the baseclass."""

    @classmethod
    def getVerticalClass(cls, dev, nrOfChan = 4):
        """ Tries to get (instantiate) the device, based on the url"""
        if cls is SDS2kVertical:
            return (cls, nrOfChan)
        else:
            return None   

    def __init__(self, nrOfChan, dev:pyvisa.resources.MessageBasedResource):
        super().__init__()
        self.nrOfChan = nrOfChan
        self.channels = list()
        
        for i in range(1, nrOfChan+1):
            self.channels.append({i:SDS2kChannel(i, dev)})
            
    def chan(self, chanNr): 
        """Gets a channel, based on its index: 1, 2 etc."""
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None     
