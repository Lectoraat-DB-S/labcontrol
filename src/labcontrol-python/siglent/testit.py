#requirements
#pyvisa
#python-vxi11
#matplotlib
"""
UserWarning: TCPIP:instr resource discovery is limited to the default interface.
Install psutil: pip install psutil if you want to scan all interfaces.

 UserWarning: TCPIP::hislip resource discovery requires the zeroconf
 package to be installed... try 'pip install zeroconf'
"""
import pyvisa
import time

from sds.Scopes import SiglentScope
from sdg.Generator import SiglentGenerator
from sdg.Commands import WaVeformTyPe
from sds.Scopes import EthernetDevice
import matplotlib.pyplot as plt
import numpy as np
#from bitarray import bitarray
#import bitstring

""""
vall = 234
bin_a = bin(vall)
print(bin_a)
bitarray(bin=bin_a).int
"""
#teststr = 'TRDL 7.00E-04S\n'
#teststr = teststr.strip("S\n")
#teststr = teststr.strip("TRDL")
#teststr = teststr.strip()
#myfloat = float(teststr)
rm = pyvisa.ResourceManager()
print(rm.list_resources())
#supply = rm.open_resource('ASRL7::INSTR')
#supply.read_termination = '\n'
#supply.write_termination = '\n'
#supply.baud_rate = 115200
#print(supply.query('*IDN?'))
#supply.write('*IDN?')

#lijstje=rm.list_resources()
#print(lijstje)
HOST = '192.168.2.100'
#generator = rm.open_resource('USB0::0xF4ED::0xEE3A::SDG00002140803::INSTR')
""""
with SiglentGenerator.usb_device() as dev1:
    print(dev1.idn)
#generator.CH1.setBasicWaveFormType(WaVeformTyPe.SQUARE)
#generator.CH1.setBasicWaveFormFreq(100)
#with SiglentScope.ethernet_device("192.168.0.32")  as dev:
with SiglentScope.ethernet_device("192.168.2.100") as dev:
    print(dev.query("*IDN?"))
    print(dev.idn)
    #outp=dev._inst.query_binary_values("C1:WaveForm? DESC", datatype='B', container=np.ndarray)
    #print(outp)

    #waarde =dev.timebase_scale
    #print(waarde)
    #memdiepte = dev.memory_depth
    #print(memdiepte)
    #test = dev.CH1.get_waveform_preamble()
    #print(test)
    #print(dev.CH1.getTRDL())
    #print(dev.CH1.getTimeAxisRange())
    trace1 = dev.CH1.capture()
    trace2 = dev.CH2.capture()
    maxVC1=max(trace1)
    maxVC2 = max(trace2)
    print(f"C1 max = {max(trace1)}")
    print(f"C2 max = {max(trace2)}")
    print(f"verhouding C2/C1= {maxVC2/maxVC1}")

    #print(trace)
    ##plt.plot(trace)
    timeAxis = np.linspace(2.0, 3.0, num=5)
    startT, StopT = dev.CH1.getTimeAxisRange()
    timeAxis = np.linspace(startT, StopT, num=dev.CH1._WFP._total_points)
    #print(timeAxis)
    plt.plot(timeAxis, trace1, timeAxis, trace2)
    #plt.xlim(dev.CH1.getTimeAxisRange())
    plt.show()

"""
scope = SiglentScope()
waarde = "1V"
scope.CH1.setVoltDiv(waarde)
#waarde = 100e-6
#scope.CH1.setIimeBase(waarde)


scope.CH1.capture()
