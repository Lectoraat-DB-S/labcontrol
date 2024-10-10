import pyvisa
from devices.siglent.sds.Scopes import SiglentScope
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM

def testAllParam():
    
    scope = SiglentScope()
    print(scope.CH1.getAllParam())
    print(scope.CH1.getAmplitude())
    print(scope.CH1.getPKPK())
    print(scope.CH1.getFrequency())
    
def testDMM():
    dmm = SiglentDMM()
    #dmm.setNumberOfMeas(10)
    #dmm.set_autorange_volt()
    print(dmm.getTriggerDelay())
    dmm.setTriggerDelay(0.0)
    print(dmm.getTriggerDelay())
    
    print(dmm.fetch_voltage())