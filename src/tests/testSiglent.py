import pyvisa
import time
import logging
from devices.siglent.sds.Scopes import SiglentScope
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM

def testAllParam():
    
    scope = SiglentScope()
    print(scope.CH1.getAllParam())
    print(scope.CH1.getAmplitude())
    print(scope.CH1.getPKPK())
    print(scope.CH1.getFrequency())
    
def testDMM():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.info('Test starting')
    dmm = SiglentDMM()
    #dmm.setNumberOfMeas(10)
    #dmm.set_autorange_volt()
    dmm.setTimeOut(2000)
    #mm.setQueryDelay(1.2)
    for x in range(0,3):
        print(dmm.get_voltage())
        time.sleep(0.01)
    
    print(dmm.fetch_voltage())