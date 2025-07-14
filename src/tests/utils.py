import numpy as np
import struct
from devices.siglent.sds.Channel import SDSWaveFormPreamble
from devices.siglent.sds.util import TIMEBASE_HASHMAP

def genFakeSineWave(starttime = 0, timediv = 1e-3, nrOfSamples = 2500, nrOfPer = 2, A=1, offset=0):
    endtime = timediv*(nrOfSamples-1) - starttime
    totalTime = endtime -starttime
    period = totalTime/nrOfPer
    f = 1/period
    tstep = np.linspace(starttime,endtime,nrOfSamples)
    y = np.array(A* np.sin(2.0*np.pi*(f)*tstep) + offset)
    y=y*127
    y=np.round(y)
    #plt.plot(y)
    #plt.show()
    res = np.array(y, dtype=np.dtype('b'))
    return res

def createSDSPreambleStruct():
    """DESC: Return descriptor. The length of descriptor is 346 bytes.
    This includes the information necessary to reconstitute the display of the waveform from the data, 
    including: your oscilloscope name and serial number, 
    the encoding format used for the data blocks, and miscellaneous constants."""
    
    buf =np.zeros(446,dtype=np.dtype('B'))
    pream = SDSWaveFormPreamble(None)
    fs = 1.0e6
    DESCRIPTOR_NAME = "WAVEDESC"
    descr_bytes = np.fromstring(DESCRIPTOR_NAME, dtype=np.dtype('B'))
    pream.nrOfSamples = 7000
    pream.probeAtt  = 1.0
    pream.vdiv      = 5.0
    pream.yoff      = 0.5
    pream.timeDiv   = 1.0e-4
    pream.trigDelay =  pream.timeDiv
    pream.xincr     = 1/fs
    
    
    instrumentStr = "SDS1202XESCOPESERIES"
    instrumentByteStr = np.fromstring(instrumentStr, dtype=np.dtype('B'))
    mem = memoryview(buf)
    #shallow_copy = original_array[:]
    nrOfBytes = len(descr_bytes)
    buf[0:nrOfBytes]= descr_bytes[0:nrOfBytes]
    buf[76:92]=instrumentByteStr[0:16]
    

    buf[119] = pream.nrOfSamples >> 24
    buf[118] = pream.nrOfSamples >> 16
    buf[117] = pream.nrOfSamples >> 8
    buf[116] = pream.nrOfSamples & 0x000000FF

    """Let op: de toevoeging van teken < is nodig, anders gaat decodering fout."""
    hulp = struct.pack("<f", pream.probeAtt)
    mem[328:332]=hulp[0:4]
    mem[156:160] = bytearray(struct.pack("f", pream.vdiv))  
    mem[160:164] = bytearray(struct.pack("f", pream.yoff)) 
    #struct.unpack('h', params[324:326])[0]
    #mem[324:326] = bytearray(struct.pack("f", pream.yoff)) 
    exp_number = '{:.2e}'.format(pream.timeDiv)
    lastVal = 0
    hashKey = None
    for key, strVal in TIMEBASE_HASHMAP.items():
        val = float(strVal)
        if val >= pream.timeDiv:
            hashKey = key
            break
        lastVal = val # interate to next item, but save previous process val
    if hashKey != None:
        hashKeyVal = int(hashKey)
    else:
        hashKeyVal = 0

    mem[324:326] = struct.pack('h', hashKeyVal)
    mem[180:188] = struct.pack('d', pream.trigDelay)
    mem[176:180] = struct.pack('f', pream.xincr)
        
    #for a capture:
    """
    in capture:
    self.rawXdata = np.linspace(0, self.WFP.nrOfSamples-1, num=int(self.WFP.nrOfSamples),endpoint=False)
    def rawYToVolts(self, vdiv, voffset):
         y = self.rawYdata
        voltfactor = vdiv/25
        tempVolt = np.multiply(y,voltfactor)
        res = np.subtract(tempVolt, voffset)
        self.scaledYdata = res

    def rawXtoTime(self, horOffset, sampleInterval, tdiv, nrOfPoints):
        
        FirstSampleTime = horOffset -tdiv*(self.hori_grid_size/2)
        lastSampleTime = FirstSampleTime + nrOfPoints*sampleInterval
        timeArr = np.arange(FirstSampleTime,lastSampleTime,sampleInterval)
        self.scaledXdata = timeArr
        
        return timeArr

    list of needed param:
    - TRDL (horizontal offset)
    - sampleinterval
    - sampleRate
    - number of sample points (check).
    - tdiv (check)
    - yoff or voffset (check)
    """

    return buf
