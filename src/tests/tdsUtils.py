import numpy as np
import struct
from devices.tektronix.scope.Channel import TekWaveFormPreamble


def genFakeSineWave(starttime = 0, fs = 1.0e4, nrOfSamples = 2500, nrOfPer = 2, A=1, offset=0, noise=(None,None,None), preamble: TekWaveFormPreamble = None):
    timestep = 1/fs
    endtime = timestep*(nrOfSamples-1) - starttime
    totalTime = endtime -starttime
    period = totalTime/nrOfPer
    f = 1/period
    
    tstep = np.linspace(starttime,endtime,nrOfSamples)
    y = np.array(A* np.sin(2.0*np.pi*(f)*tstep) + offset)
    y=y*127
    y=np.round(y)
    amp, mu, sigma =noise
    if amp != None and mu != None and sigma != None:
        s = np.random.normal(mu, sigma, nrOfSamples)
        y=y+s
    if preamble != None:
        #use the preamble to scale the sine wave
        
        voltrange = preamble.vertGridsize * preamble.vdiv/2
        print(f"max val voltrange: {voltrange}")
        y = y/voltrange
    y[(y>127)]=127
    y[(y<-128)]=-128
    #plt.plot(y)
    #plt.show()
    res = np.array(y, dtype=np.dtype('b'))
    return res

def createTDSPreamble(preamble: TekWaveFormPreamble = None):
        
    if preamble == None:
        fs = 1.0e6
        preamble = TekWaveFormPreamble(None)
        
        preamble.nrOfSamples = 2500
        preamble.vdiv      = 5.0
        preamble.yoff      = 0.5
        preamble.timeDiv   = 1.0e-4
        preamble.xincr     = 1/fs
        preamble.xzero     = 0
        
        PT_OFF = 0 # see programming manual. Value is always zero.
    """For Y format, the time (absolute coordinate) of a point, relative to the trigger, can
        be calculated using the following formula. N ranges from 0 to 2499.
        
            Xn = XZEro + XINcr (n - PT_OFf)

        For Y format, the magnitude (usually voltage, relative to ground) (absolute
        coordinate) of a point can be calculated:
            Yn = YZEro + YMUIty (yn - YOFf)
    """


    preambleStr=f"""1;8;BIN;RI;MSB;{preamble.nrOfSamples};"Ch1, DC coupling, {preamble.vdiv} V/div,
                 {preamble.tdiv} s/div, {preamble.nrOfSamples} points, Sample mode";Y;{preamble.xincr};{PT_OFF};{preamble.xzero};
                 "s";{preamble.ymult};{preamble.yzero};{preamble.yoff};'Volts'"""
    return preambleStr.encode()
