import pyvisa
from devices.siglent.sds.Scopes import SiglentScope
from devices.siglent.sdg.Commands import WaveformParam 
from devices.siglent.sdg.Commands import WVTP 

def testTheSDS():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    scope = SiglentScope()
    print(scope.CH1.getMean())
    
    print(scope.CH1.getPKPK())