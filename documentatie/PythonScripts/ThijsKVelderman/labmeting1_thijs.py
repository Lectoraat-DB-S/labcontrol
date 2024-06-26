import pyvisa
import time                 #time gebruikt voor het toevoegen van een delay
import numpy as np          #numpy gebruikt om float bij for-loop range te kunnen gebruiken

# Setup PyVisa
# USB poorten koppelen aan leesbare namen voor in de code
# bij 'usbpoort' kun je zelf het gekopieërde usb adres invoegen
# USB adres kun je uitlezen door het programma USB-readout te laten draaien

rm = pyvisa.ResourceManager()
powersupply = rm.open_resource('USB0::0xF4EC::0x1430::SPD3XIDC5R1000::INSTR')
voltmeter = rm.open_resource('USB0::0xF4EC::0xEE38::SDM34FBD3R2488::INSTR')


# Setup voor de voltmeter
# Zet de multimeter op Volt en dan DC

voltmeter.write('CONF:VOLT:DC')


# Setup voor voeding
# Kiest Channel 1 van de voeding
# Zet vervolgens de stroomlimiet op 0.2 A
# Daarna wordt Channel 1 aangezet

powersupply.write ('INSTrument CH1')
powersupply.write ('CH1:CURRent 0.2')
powersupply.write ('OUTPut CH1,ON')


# Voltage van de voeding wordt telkens met 0.1 V verhoogd tot het 5,9V heeft bereikt. 

for voltage in np.arange(1, 6, 0.1):
    powersupply.write('CH1:VOLTage ',str(voltage) )             #voltage waarde schrijven naar powersupply
    time.sleep(300/1000)                                        #300ms delay
    signaal = float(voltmeter.query('MEAS:VOLT:DC?'))           #meet waarde opvragen van multimeter
    print("{}".format(signaal))                                 #waarde printen in debugger van Python


# Powersupply wordt weer op 0 Volt gezet
# Zet powersupply uit daarna, programma einde

powersupply.write('CH1:VOLTage 0')
powersupply.write('OUTPut CH1,OFF')
