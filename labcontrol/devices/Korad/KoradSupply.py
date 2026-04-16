from ast import literal_eval
import pyvisa
from devices.BaseSupply import BaseSupply,BaseSupplyChannel
from devices.BaseConfig import BaseSupplyConfig
import socket
import serial
import time
from serial.tools.list_ports import comports
import configparser
import os



class KoradChannel(BaseSupplyChannel):
    def __init__(self, chan_no, dev):
        super().__init__(chan_no, dev=dev)
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

class Korad3305P(BaseSupply):
    VISAInterface = "ASRL"
    targetCom = "COM10"
    prefMethod = None
    
    @classmethod
    def readConfig(cls):
        config = configparser.ConfigParser()
        print(os.getcwd())
        #TODO: onderstaand path algemeen maken dit is niet ok zo.
        config.read(CONFIGPARSERPATH = '.\\src\\labcontrol.ini')
        config.read('.\\src\\labcontrol.ini')
        if "Korad3305P" in config.sections():
                if 'VisaInterface' in config['Korad3305P']:
                    Korad3305P.VISAInterface=literal_eval(config['Korad3305P']  ['VisaInterface'])
                if 'ComPort' in config['Korad3305P']:
                    Korad3305P.targetCom=literal_eval(config['Korad3305P']['ComPort'])
                if 'PrefSearchMethod' in config['Korad3305P']:
                    Korad3305P.prefMethod = literal_eval(config['Korad3305P']['PrefSearchMethod'])
        else:
            Korad3305P.VISAInterface = "ASRL"
            Korad3305P.prefMethod = "IDN"

    @classmethod
    def findVISADeviceOnComPortNr(cls, rm, urls):

        for url in urls: # traverse al urls
            if cls.VISAInterface in url: #select only applicable interface for this device
                try: # the open_resource might fail therefore a try/exept clause.
                    mydev = rm.open_resource(url)
                    if cls.targetCom!=mydev.resource_info.alias: #if alias is not the desired comport value, skip it.
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

        #if search has been ended, two option: found a possible Korad device or found None.
        # When found an option: check the idn and if ok: find 
        if  mydev == None:
            return None 
        else: 
            try: # the query call might fail therefore a try/exept clause.
                mydev.timeout = 2000  # ms
                mydev.read_termination = '\n'
                mydev.write_termination = '\n'
                desc = mydev.query("*IDN?")
                if desc.find("KA3305P") > -1: #Korad KA3305P device found in IDN response.
                    if cls is Korad3305P:
                        return (cls, 2, mydev)
                    return (None, None, None)
                else:
                    mydev.close()
                    mydev = None
                    return None

            except pyvisa.errors.Error as pyerr:
                print(f"VISA Error")
                mydev = None #let's go for the next one.
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                return None

    @classmethod
    def findDeviceOnIDN(cls, rm, urls):
        mydev = None
        for url in urls: # traverse al urls
            if cls.VISAInterface in url: #select only applicable interface for this device
                try: # the open_resource might fail therefore a try/exept clause.
                    mydev = rm.open_resource(url)
                    mydev.timeout = 5000  # ms
                    mydev.read_termination = '\n'
                    mydev.write_termination = '\n'
                    desc = mydev.query("*IDN?")
                    if desc.find("KA3305P") > -1: #Korad 3305 device found in IDN response.
                        if cls is Korad3305P:
                            return (cls, 2, mydev)
                        return (None, None, None)
                    else:
                        mydev.close()
                        mydev = None    
                except pyvisa.errors.Error as pyerr:
                    print(f"VISA Error")
                    mydev = None #let's go for the next one.
                    return (None, None, None)
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    return (None, None, None)
        
    
        
    @classmethod
    def getSupplyClass(cls, rm, urls, host,supplyConfigs: list = None):
        """ Tries to get (instantiate) the device, based on the url"""
        #The KORAD3305P supply only supports serial communication.
        #11-4-25:
        #code for listing comports in Pyhton:
        #for port in comports():
        #    print(port)
        #cls.readConfig()
        retval = None
        if Korad3305P.prefMethod == "IDN" or Korad3305P.prefMethod == None:
            retval = cls.findDeviceOnIDN(rm, urls)
        else:
            retval = Korad3305P.findVISADeviceOnComPortNr(rm, urls)

        return retval
        
    def __init__(self, dev= None, host=None, nrOfChan=2):
        self.visaInstr : pyvisa.Resource = dev
        self.host = host
        self.nrOfChan = nrOfChan
        self.channels = list()
        for i in range(1, self.nrOfChan+1):
            self.channels.append({i:KoradChannel(i, dev)})

    def chan(self, chanNr:int)-> KoradChannel:
        """Gets a channel, based on its index: 1, 2 etc."""
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None     
    

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