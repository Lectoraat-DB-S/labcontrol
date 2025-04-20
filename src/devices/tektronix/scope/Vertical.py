import pyvisa as visa
import numpy as np
from devices.BaseScope import BaseVertical
from devices.tektronix.scope.Channel import TekChannel

class TekVertical(BaseVertical):
    """"Subclass of BaseVertical for Tektronix TDS1000 scope series. This class implements the baseclass."""

    def __init__(self, nrOfChan, dev):
        super().__init__(nrOfChan, dev) # visa dev will be initted by the Baseclass
        self.nrOfChan = nrOfChan
        
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
