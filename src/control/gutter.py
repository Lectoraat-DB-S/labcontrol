import pyvisa

from devices.siglent.sds import Scopes
from devices.siglent.sdg import Generator
#from devices.siglent.sdg.Commands import WaVeformTyPe
#from devices.siglent.sdg.Commands import WaveformParam

#neutral position of servo is around 1.5 ms pulse time (https://en.wikipedia.org/wiki/Servo_control)
#minimal width is approx 1ms, max width is approx 2ms
#testing reveals horizontal position of servo is at 1.59 ms

def controlBall():
    startpos = 1.59e-3
    leftmost =1.13e-3
    rightmost = 2.06e-3
    #scoop = Scopes.SiglentScope("192.168.0.32")
    #scoop = Scopes.SiglentScope()
    #gen = Generator.SiglentGenerator("192.168.0.100")
    gen = Generator.SiglentGenerator()
    #print(scoop.query("*IDN?"))
    print(gen.query("*IDN?"))
    #gen.CH1.setPulse(parampje)
    gen.CH1.setAmp(5)
    gen.CH1.setOffset(2.5)
    gen.CH1.setPulseWave(10e-3, startpos,1e-6,1e-6,0)
    gen.CH1.enableOutput(True)
    
    #with SiglentScope.ethernet_device("192.168.0.32") as dev:
    #    print(dev.query("*IDN?"))
    #scopie.CH1.getAmplitude()
