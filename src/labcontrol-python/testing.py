import pyvisa
from tektronix.scope.TekScopes import TekScope
from siglent.sdg.Generator import SiglentGenerator
from siglent.spd.PowerSupply import SiglentPowerSupply
from siglent.sdm.DigitalMultiMeter import SiglentDMM

rm = pyvisa.ResourceManager()
print(rm.list_resources())
dmm= SiglentDMM()
power = SiglentPowerSupply()
scope = TekScope()

power.CH1.set_output(True)
power.CH1.set_current(0.1)
power.CH1.set_voltage(1)
print(dmm.get_current())
print(power.CH1.measure_voltage())
print(scope.CH1.getVoltage())
print(scope.CH2.getVoltage())
curr_dmm = float(dmm.get_current())
curr_powsupply=float(power.CH1.measure_current())
volt_powsupply=float(power.CH1.measure_voltage())
scope_V1=float(scope.CH1.getVoltage())
scope_V2=float(scope.CH2.getVoltage())
power.CH1.set_output(False)
totalRes =scope_V1/curr_dmm
print("totale weerstand = "+str(totalRes)+ " Ohm")
R1 = scope_V2/curr_dmm
print("waarde weerstand R1= "+str(R1)+ " Ohm")
R2 = (scope_V1-scope_V2)/curr_dmm
print("waarde weerstand R2 = "+str(R2)+ " Ohm")
#trace1 = scope.capture()
#scope = TekScope()
#outdata = scope.capture()
#scope.setTimeBase(1.0e-2)
#scope.setVertGain(1e-1)