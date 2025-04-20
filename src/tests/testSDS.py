import pyvisa
from devices.siglent.sds.Scopes import SiglentScope
from devices.siglent.sdg.Commands import WaveformParam 
from devices.siglent.sdg.Commands import WVTP 
from matplotlib import pyplot as plt 

def testTheSDS():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    scope = SiglentScope()
    print(scope.CH1.getMean())
    
    print(scope.CH1.getPKPK())
    scope.CH1.capture()
    waveformTrace = scope.CH1.getTrace()
    timeAx = scope.CH1.getTimeAxis()
    plt.plot(timeAx, waveformTrace)
    plt.show()