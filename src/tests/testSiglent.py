import pyvisa
from devices.siglent.sds.Scopes import SiglentScope

def testAllParam():
    
    scope = SiglentScope()
    print(scope.CH1.getAllParam())
    print(scope.CH1.getAmplitude())
    print(scope.CH1.getPKPK())
    print(scope.CH1.getFrequency())