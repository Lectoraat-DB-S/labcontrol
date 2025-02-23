import numpy as np
import pyvisa

testUrlSDG = "USB0::0xF4ED::0xEE3A::SDG00002140803::INSTR"
urlSDS = "USB0::0xF4ED::0xEE3A::SDS1EEFX6R6638::INSTR"

"""
copy paste from sdg programming manual:
RESPONSE FORMAT
Format 1: \*IDN, <device id>,<model>,<serial number>,<firmware version>, <hardware version>
Format 2: <manufacturer>,<model>,<serial number>,<firmware version>, <device id> := “SDG”.
<manufacturer> := “Siglent Technologies”.
<model> := A model identifier less than 14 characters, should not contain the word “MODEL”.
<serial number> := The serial number.
<firmware version> := The firmware version number.
<hardware version> := The hardware level field, containing information about all separately revisable subsystems.
"""
class TestClass():
    dummystr_frmt1 = "*IDN, devidxxxx,SDG6052X, SDG6XBAX1R0034, 6.01.01.28, 00000.x.x"
    dummystr_frmt2 = "Siglent Technologies,SDG6052X, SDG6XBAX1R0034, 6.01.01.28, 00000.x.x"
    def __init__(self):
        self.myIDN = IDN()
class IDN():
    def __init__(self):
        self._frmt = None
        self._manufacturer = None
        self._model= None
        self._serialNr = None
        self._firmwareVer = None
        self._deviceId = None
        self._hardwareVer = None

    def decodeIDN(self, desc: str):
        if desc.find("*IDN") > -1: # it is a format 1 type of response
            self.decodeFrmt1(desc)
            return self
           # buffer = np.fromstring(desc, sep=',')
        else:                       # it is a format 2 type of unknown response
            self.decodeFrmt2(desc)
            return self
    def decodeFrmt1(self, desc: str):
        result = desc.split(",")
        length = len(result)
        self._manufacturer = None  # not available in this format
        self._frmt = 1
        match length:
            case 0:
                pass
            case 1:
                pass
            case 2:
                self._deviceId = result[1]
            case 3:
                self._deviceId = result[1]
                self._model = result[2]
            case 4:
                self._deviceId = result[1]
                self._model = result[2]
                self._serialNr = result[3]
            case 5:
                self._deviceId = result[1]
                self._model = result[2]
                self._serialNr = result[3]
                self._firmwareVer = result[4]
            case 6:
                self._deviceId = result[1]
                self._model = result[2]
                self._serialNr = result[3]
                self._firmwareVer = result[4]
                self._hardwareVer = result[5]
            case _:
                pass #strange situation.

    def decodeFrmt2(self, desc: str):
        result = desc.split(",")
        length = len(result)
        self._frmt = 2
        match length:
            case 0:
                pass
            case 1:
                self._manufacturer = result[0]
            case 2:
                self._manufacturer = result[0]
                self._model = result[1]
            case 3:
                self._manufacturer = result[0]
                self._model = result[1]
                self._serialNr = result[2]
            case 4:
                self._manufacturer = result[0]
                self._model = result[1]
                self._serialNr = result[2]
                self._firmwareVer = result[3]
            case _:
                self._manufacturer = result[0]
                self._model = result[1]
                self._serialNr = result[2]
                self._firmwareVer = result[3]
                self._deviceId = result[4]
        self._hardwareVer = None    # not available in this format

    def printIDN(self):
        retString = ""
        if self._manufacturer is not None:
            retString += " "+self._manufacturer
        if self._model is not None:
            retString += " " + self._model
        if self._deviceId is not None:
            retString += " " + self._deviceId
        if self._serialNr is not None:
            retString += " " + self._serialNr
        if self._hardwareVer is not None:
            retString += " " + self._hardwareVer

        return retString
class LabDevice():
    def __init__(self):
        self._resourcelist = None
        # try to find connected stuff with native Visa
        rm = pyvisa.ResourceManager()

"""
Dit zijn antwoorden op de call resourcemanager.list_resources() in Python:
‘USB0::0x0483::0x7540::SPD3XGB4150080::INSTR’ – This is a power supply (SPD3X) connected via USB (USB0)

‘USB0::0xF4EC::0x1301::SVA1XEAX2R0073::INSTR’ – This is a vector network analyzer (SVA1X) connected via USB (USB0)

‘TCPIP0::192.168.55.122::inst0::INSTR’ – This is an instrument connected via LAN using a TCPIP connection at IP address 192.168.55.122

"""
        
"""
Reactie resourcemanager.list_resources() in Python wanneer je via een USB hub een siglent scope en een siglent generator hebt 
aangesloten:

('USB0::0xF4ED::0xEE3A::SDG00002140803::INSTR', 
'USB0::0xF4ED::0xEE3A::SDS1EEFX6R6638::INSTR', 
'ASRL3::INSTR', 'ASRL4::INSTR', 'ASRL5::INSTR')
"""
#pattern = "SDG"
#if pattern in testUrlSDG:
#    print("het is een functiegenerator")
#else:
#    print("het is Geen functiegenerator")
#test = decodeIDN(dummystr_frmt1)
#test = TestClass()
#test2= test.myIDN.getIDN(test.dummystr_frmt1)

#print(test2)
