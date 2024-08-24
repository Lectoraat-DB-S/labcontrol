import pyvisa
from siglent.sdg.Commands import WaVeformTyPe
from siglent.sdg.Generator import SiglentGenerator
from siglent.sdg.Commands import BasicWaveCommandTypes
from siglent.sdg.Commands import WaVeformTyPe
from siglent.sdg.Commands import WaveForm
"""
SDG_ADDRESS = '192.168.0.100'
with (SiglentGenerator.ethernet_device("192.168.0.100") as dev):
    #print(dev.query("C1:BSWV?"))
    dev.CH1.setBasicWaveFormType(WaVeformTyPe.RAMP)
    dev.CH1.setOutputOn(True)
    dev.CH1.setSweep(True,500,30000,25)
    #dev.CH1.setSweep(False)
"""
rm = pyvisa.ResourceManager()
print(rm.list_resources())
generator = SiglentGenerator()
print(generator.getIDN())
generator.CH1.setBasicWaveFormType(WaVeformTyPe.RAMP)