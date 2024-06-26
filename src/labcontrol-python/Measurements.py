import time
from tektronix.scope.TekScopes import TekScope
from siglent.sdg.Generator import SiglentGenerator
#from siglent.sds.Scopes import SiglentScope

import matplotlib.pyplot as plt
import numpy as np
import pyvisa as visa

welcomeMsg = "Welcome to Labcontrol. Select a measurement."
instructMsg = "Please connect Siglent SDS en Siglent SDG via USB. Press key when ready"
rm = visa.ResourceManager()
theList = rm.list_resources()
print(theList) 
scope = TekScope()
generator = SiglentGenerator()

scope.CH1.setAsSource()

startFreq = 10
stopFreq = 100e3
nrOfMeasPoints = 1000
amplitude = 2
phase =0
generator.CH1.setType("SIN")
generator.CH1.setAmp(amplitude)
generator.CH1.setOutputOn(True)
#scope.CH1.setVoltDiv(0.5)

freq_list=[10, 100, 1000, 10000]
amp_in_list=[]
amp_out_list=[]

for freq in freq_list:
    print(freq)
    timebase=0.1/(freq)
    scope.setTimeBase(timebase)
    generator.CH1.setFreq(freq)
    time.sleep(0.5)
    trace1 = scope.capture()
    #trace2 = scope.CH2.capture()
    #print(scope.CH1.getMaxOfTrace())
    #startT, StopT = scope.CH1.getTimeAxisRange()
    #timeAxis = np.linspace(startT, StopT, num=scope.CH1._WFP._total_points)
    #plt.plot(timeAxis, trace1)
    #plt.show()
    #time.sleep(0.1)
    #scope.aquire()
    #amp_in_list.append(scope.CH1.getAbsMaxValAcq())
    #amp_out_list.append(scope.CH2.getAbsMaxValAcq())
#plot
#figure(1)
#plot(freq_list,amp_in_list)
#figure(2)
#plot(freq_list,amp_out_list)
#figure(3)
#plot(freq_list,amp_out_list/amp_in_list)
#"""