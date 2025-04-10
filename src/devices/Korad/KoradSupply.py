import pyvisa
from devices.BaseSupply import BaseSupply, BaseChannel
import socket
import serial
import time


class KoradChannel(BaseChannel):
    def __init__(self, chan_no, dev):
        self.name = f"{chan_no}"
        self.visaInstr:pyvisa.resources.MessageBasedResource = dev
        
    
    def voltage(self, value):
        """Sets the output voltage of this channel"""
        self.visaInstr.write(f"VSET{self.name}:{value}")

    def voltage(self):
        """Gets the current output voltage setting of this channel"""
        return self.visaInstr.query(f"VSET{self.name}?")
    
    def getVoltage(self):
        """Measures actual output voltage delivered by this channel"""  
        return self.visaInstr.query(f"VOUT{self.name}?")
    
    def current(self, value):
        self.visaInstr.write(f"ISET{self.name}:{value}")
        
    def current(self):
        return self.visaInstr.query(f"ISET{self.name}?")

    def getCurrent(self):
        """Measures actual output current delivered by this channel"""  
        return self.visaInstr.query(f"IOUT{self.name}?")
    
    def enable(self, flag: bool):
        if flag:
            self.visaInstr.write(f"OUTCH{self.name} :1")
        else:
            self.visaInstr.write(f"OUTCH{self.name} :0")

    def OCP(self, value):
        self.visaInstr.write(f"OCPSET{self.name}: {value}")

    def OCP(self):
        return self.visaInstr.query(f"OCPSET{self.name}?")
    
    def OVP(self, value):
        self.visaInstr.write(f"OVPSET{self.name}: {value}")

    def OVP(self):
        return self.visaInstr.query(f"OVPSET{self.name}?")
    
    def vRamp(self, start, stop, vstep, tstep):
        self.visaInstr.write(f"VASTEP{self.name}:{start},{stop},{vstep},{tstep}")

    def vStop(self):
        self.visaInstr.write(f"VASTOP{self.name}")
    
    def iRamp(self, start, stop, istep, tstep):
        self.visaInstr.write(f"IASTEP{self.name}:{start},{stop},{istep},{tstep}")

    def iStop(self):
        self.visaInstr.write(f"IASTOP{self.name}")

    def vStep(self, value):
        self.visaInstr.write(f"VSTEP{self.name}:{value}")

    def vUp(self):
        self.visaInstr.write(f"VUP{self.name}")    

    def vDown(self):
        self.visaInstr.write(f"VDOWN{self.name}")    
    
    def iStep(self, value):
        self.visaInstr.write(f"ISTEP{self.name}:{value}")

    def iUp(self):
        self.visaInstr.write(f"IUP{self.name}")    

    def iDown(self):
        self.visaInstr.write(f"IDOWN{self.name}")    

"""
VI_ERROR_SYSTEM_ERROR (-1073807360): Unknown system error (miscellaneous error).

"""

class Korad3305P(BaseSupply):

        
    @classmethod
    def getDevice(cls, rm, urls, host):
        """ Tries to get (instantiate) the device, based on the url"""
        #The KORAD3305P supply only supports serial communication.
        mydev = None
        serialUrlPattern = "ASRL"
        targetCom = "COM10"
        for url in urls: # traverse al urls
            if serialUrlPattern in url:
                try:
                    mydev = rm.open_resource(url)
                    if targetCom!=mydev.resource_info.alias:
                        mydev.close() #keep going
                        mydev = None
                    else:
                        break # stop searching.
                except pyvisa.errors.Error as pyerr:
                    print(f"VISA Error")
                    mydev = None #let's go for the next one.
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    raise

        if  mydev == None:
            return None  
        mydev.timeout = 5000  # ms
        mydev.read_termination = '\n'
        mydev.write_termination = '\n'
        desc = mydev.query("*IDN?")
        if desc.find("KA3305P") > -1: #Korad 3305 device found in IDN response.
            if cls is Korad3305P:
                cls.__init__(cls,mydev)
                return cls
            else:
                return None        
        
    
    def __init__(self, dev= None, host=None, nrOfChan=2):
        self.visaInstr : pyvisa.Resource = dev
        self.host = host
        self.nrOfChan = nrOfChan
        for i in range(1, self.nrOfChan+1):
            self.channels.append({i:KoradChannel(i, dev)})

    def idn(self):
        return self.visaInstr.query("*IDN?")
    
    def OCP(self, flag: bool):
        if flag == True:
            self.visaInstr.write(f"OCP1")
        else:
            self.visaInstr.write(f"OCP0")

    def OVP(self, flag: bool):
        if flag == True:
            self.visaInstr.write(f"OVP1")
        else:
            self.visaInstr.write(f"OVP0")

    def enable(self, flag: bool):
        if flag == True:
            self.visaInstr.write(f"OUT1")
        else:
            self.visaInstr.write(f"OUT0")

    def mode(self, modeVal):
        if modeVal == 1 or modeVal == 2 or modeVal == 3:
            self.visaInstr.write(f"TRACK{modeVal}")

    def status(self):
        return int(self.visaInstr.query("STATUS?")) 
    
    def strStatus(self):
        resp = ""
        val = self.status()
        bit0 = val & 0x01
        bit1 = val & 0x02
        bit23 = val & 0x0C
        bit4 = val & 0x10
        bit5 = val & 0x20
        bit6 = val & 0x40
        bit7 = val & 0x80
        
        if bit0: resp+="CH1: Constant Voltage Control\n"
        elif ~bit0: resp+="CH1: Constant Current Control\n"
        else: resp+="Error Status bit 0\n"

        if bit1: resp+="CH2: Constant Voltage Control\n"
        elif ~bit1: resp+="CH2: Constant Current Control\n"
        else: resp+="Error Status bit 1\n"

        match bit23:
            case 0: resp+="Independent Channels\n"
            case 1: resp+="Series Channels\n"
            case 2: resp+="Parallel Channels\n"
            case _: resp+="Error status bit 2 and 3\n"
        
        if bit4: resp+="OVP: ON\n"
        elif ~bit4: resp+="OVP: OFF\n"
        else: resp+="Error Status bit 4\n"

        if bit5: resp+="OCP: ON\n"
        elif ~bit5: resp+="OCP: OFF\n"
        else: resp+="Error Status bi5 4\n"
        
        if bit6: resp+="CH1 OUT: ON\n"
        elif ~bit6: resp+="CH1 OUT: OFF\n"
        else: resp+="Error Status bit 6\n"

        if bit7: resp+="CH2 OUT: ON\n"
        elif ~bit7: resp+="CH2 OUT: OFF\n"
        else: resp+="Error Status bit 7\n"

        return resp