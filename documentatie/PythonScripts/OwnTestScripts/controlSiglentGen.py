import usbtmc
import time
print(usbtmc.list_resources())
#sdg = usbtmc.Instrument('USB::62700::4355::SDG1XDCX6R3052::INSTR')
#print(sdg.ask("*IDN?"))

#sdg.write('C1:BSWV WVTP,SQUARE,FRQ,10000000,AMP,3.3V')
#sdg.write('C1:BSWV WVTP,SINE,FRQ,1000,AMP,1.3V')
#sdg.write('C1:OUTP ON')
#time.sleep(1)
#sdg.ask('C1:BSWV?')
#print()
