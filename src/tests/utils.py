import numpy as np
import struct
from devices.siglent.sds.Channel import SDSWaveFormPreamble

def genFakeSineWave(starttime = 0, endtime = 2e-3, aantal_stappen = 2500, f=200):
    tstep = np.linspace(starttime,endtime,aantal_stappen)
    y = np.sin(2.0*np.pi*(f)*tstep)
    y=y*127
    y=np.round(y)
    #plt.plot(y)
    #plt.show()
    return np.array(y, dtype=np.dtype('b'))

def createSDSPreambleStruct():
    """DESC: Return descriptor. The length of descriptor is 346 bytes.
    This includes the information necessary to reconstitute the display of the waveform from the data, 
    including: your oscilloscope name and serial number, 
    the encoding format used for the data blocks, and miscellaneous constants."""
    buf = bytearray(446)
    pream = SDSWaveFormPreamble(None)
    
    DESCRIPTOR_NAME = "WAVEDESC"
    descr_bytes = DESCRIPTOR_NAME.encode()
    pream.nrOfSamples = 7000
    pream.probeAtt  = 1.0
    pream.vdiv      = 5.0
    pream.yoff      = 0.0
    
    
    instrumentStr = "SDS1202XESCOPESERIES"
    print(len(instrumentStr))
    
    #perform the bytepacking.
    
    buf[0:15] = descr_bytes
    instrumentBytes = instrumentStr.encode()
    instrumentBytes = instrumentBytes[0:15]
    buf[100:115]=instrumentBytes
    buf[116:120] = pream.nrOfSamples.to_bytes(4)
    buf[328:331] = bytearray(struct.pack("f", pream.probeAtt))  
    buf[156:159] = bytearray(struct.pack("f", pream.vdiv))  
    buf[160:163] = bytearray(struct.pack("f", pream.yoff)) 
    return buf

