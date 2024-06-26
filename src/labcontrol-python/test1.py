import pyvisa
import logging
import matplotlib.pyplot as plt
from tektronix.scope.TekScopes import TekScope
#from siglent.sdg.Generator import SiglentGenerator
#from siglent.spd.PowerSupply import SiglentPowerSupply
import time
#from tektronix.scope.Acquisitions import TekScopeEncodings
#from tektronix.scope.TekLogger import TekLog

"""
def testfunc(encoding: TekScopeEncodings):
    if isinstance(encoding, TekScopeEncodings):
        print("Correct type")
    else:
        print("verkeerd type")
    if (encoding==TekScopeEncodings.RIBinary or encoding==TekScopeEncodings.ASCII or 
            encoding==TekScopeEncodings.RPBinary or
            encoding==TekScopeEncodings.SRPbinary):
        print(encoding.value)
    else:
        print("no value!!")
    
#a = TekScopeEncodings.RIBinary
#log = TekLog()
#log.addToLog("bericht")
"""
rm = pyvisa.ResourceManager()
print(rm.list_resources())
scope = TekScope()
scope.CH1.setVisible(True)
scope.CH2.setVisible(False)
scope.CH1.setAsSource()
scope.CH1.capture()
plt.plot(scope.CH1.getLastTrace().scaledXData, scope.CH1.getLastTrace().scaledYdata)
plt.show()
"""
powersup = SiglentPowerSupply()
#time.sleep(0.04) #Wait
powersup.CH1.set_voltage(1)
#time.sleep(3)
powersup.CH1.set_output(False)
#time.sleep(3)
powersup.CH1.set_current(1.5)
#scope = TekScope()
#outdata = scope.capture()
#scope.setTimeBase(1.0e-2)
#scope.setVertGain(1e-1)
"""
