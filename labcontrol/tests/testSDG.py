import pyvisa
from devices.siglent.sdg.Generator import SiglentGenerator 
from devices.siglent.sdg.Commands import WaveformParam 
from devices.siglent.sdg.Commands import WVTP 

def doTheTest():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())

    gen = SiglentGenerator()
    gen.CH1.setSineWave(10000)
    gen.CH1.setAmp(1)
    input("enter key")
    param = gen.CH1.getWaveParam()
    print(param.toString())
    gen.CH1.setAmp(7.5)
    input("enter key")
    gen.CH1.setfreq(123e3)
    input("enter key")
    gen.CH1.setPulseWave(10e-3,1e-3,0.1e-3,0.1e-3)
    input("enter key")
    gen.CH1.setSineWave(10,5)
    input("enter key")
    gen.CH1.enableOutput(True)
