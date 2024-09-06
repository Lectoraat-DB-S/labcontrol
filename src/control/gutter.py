import pyvisa

from devices.siglent.sds import Scopes
from devices.siglent.sdg import Generator
from devices.siglent.sdg.Commands import WaVeformTyPe
from devices.siglent.sdg.Commands import WaveformParam

def controlBall():
    #scoop = Scopes.SiglentScope("192.168.0.32")
    scoop = Scopes.SiglentScope()
    #gen = Generator.SiglentGenerator("192.168.0.100")
    gen = Generator.SiglentGenerator()
    print(scoop.query("*IDN?"))
    print(gen.query("*IDN?"))
    parampje=WaveformParam()
    parampje.frequency=500
    parampje.amp=5
    parampje.offset=2.5
    parampje.pulWidth=1.34e-3
    #gen.CH1.setPulse(parampje)
    print(gen.CH1.getBasicWaveParam())
    #with SiglentScope.ethernet_device("192.168.0.32") as dev:
    #    print(dev.query("*IDN?"))
    #scopie.CH1.getAmplitude()
