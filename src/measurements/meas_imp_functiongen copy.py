import pyvisa

#import src.devices.tektronix.scope.TekScopes as test
import devices.tektronix.scope.TekScopes as test

#from devices.tektronix.scope.TekScopes import TekScope
from devices.siglent.sdg.Generator import SiglentGenerator
from devices.siglent.sds.Scopes import SiglentScope

#from siglent.sdg.Generator import SiglentGenerator

#from siglent.sdg.Generator import SiglentGenerator

def functie():
    piemels = test.TekScope()
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
