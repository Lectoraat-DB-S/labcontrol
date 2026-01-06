import usb.core
import usb.backend.libusb1
import numpy as np
#import devices.Hantek6022API.examples.realtime_qt
#USB\VID_5345&PID_1235
#backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\pyenv\\labcontrol\\Scripts\\libusb-1.0.dll")
#dev = usb.core.find(idVendor=0x5345, idProduct=0x1235, backend=backend)
#dev.write(1, "SOURce1:FUNCtion:SHAPe SINusoid")
#dev.write(1, "SOURce1:FREQuency:FIXed 5kHz")
#dev.write(1, "OUTPut1:STATe ON")
#print(dev)

valid_times_str = '1NS,2NS,5NS,10NS,20NS,50NS,100NS,200NS,500NS,1US,2US,5US,10US,20US,50US,100US,200US,500US,1MS,2MS,5MS,10MS,20MS,50MS,100MS,200MS,500MS,1S,2S,5S,10S,20S,50'

TIMEBASE_HASHMAP = {
                    "0":5e-9,"1": 10e-9, "2":25e-9,"3":50E-9,
                    "4":100e-9,"5":250e-9,"6":500e-9,
                    "7":1e-6,"8":2.5e-6,"9":5e-6,
                    "10":10e-6,"11":25e-6,"12":50e-6,
                    
                    "13":100e-6,"14":250e-6,"15":500e-6,
                    "16": 1e-3, "17": 2.5e-3, "18": 5e-3,
                    "19": 10e-3, "20": 25e-3, "21": 50e-3,
                    "22": 100e-3, "23": 250e-3, "24": 500e-3,
                    "25": 1, "26": 2.5, "27": 5
                    }

def setIimeBase( value):
        """Set the time per devision for this oscilloscoop. This scope isn't as flexible as a Tektronix TDS.
        The TDS has a coarse and a fine mode on setting tdiv. Siglent only accepts the predefined values of the range.
        It seems the scope ignores a value if it is above a predefined value.
        """
        
        myValArray = np.array((list(TIMEBASE_HASHMAP.values())))
        
        if value in myValArray:
            val2Set = value
        else: # no corresponding setting available for value. Find nearest, first bigger option.
            
            myIndices = ( (myValArray>value).nonzero()[0])
            if len(myIndices)==0:
                val2Set = myValArray[-1]

            else:    
                val2Set = myValArray[myIndices[0]]
           

import ast   
from prefixed import Float         

tijdjes = np.array(valid_times_str.split(","))
print(len(tijdjes))
print(type(tijdjes))
a = list()
for tijd in tijdjes:
    a.append(tijd[:-1])
print 

print(Float('1U'))