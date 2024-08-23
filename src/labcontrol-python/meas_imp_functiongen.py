import pyvisa
#from siglent.sdm.DigitalMultiMeter import SiglentDMM
from siglent.sdg.Generator import SiglentGenerator

rm = pyvisa.ResourceManager()
print(rm.list_resources())
