import usb.core
import usb.util
from pyvisa import ResourceManager as rm
import unittest
from unittest.mock import patch, MagicMock
#from tests.testKorad import TestKoradSupply
from tests.testTDS import TestTDSCase
from tests.testTDS import suite
import math
import numpy as np
#from tests.testSDS import TestSDSCase
#from tests.testSDS import suite    
from devices.siglent.sds.SDS2000.commands_full import SCPI
from devices.siglent.sds.SDS2000.params import PARAM
from devices.BaseScope import BaseScope, SCPICommand,SCPIParam

if __name__ == "__main__":
    #rc = ResourceManager(visa_library="@mock")
    #rm=pyvisa.ResourceManager()
    #print(rm.list_resources())  
    #dummyUse()
    #performTransCurve()
    #myscipi:SCPICommand = SCPICommand(SCPI, PARAM) 
    myparm = SCPIParam(PARAM)
    myscpi = SCPICommand()

    #testcomm = [ "TRIGGER","run"]
    #testcomm = [ "CHANNEL","impedance"]
    testcomm = [ "TRIGGER","EDGE","coupling"]
    #str = SCPI[testcomm[0]][testcomm[1]]()
    myparm.setIndex(testcomm)
    commParam = myparm.list2CommandParams()
    #paramin = "DC"
    #paramin = "FIFTY"
    #paramin = "LFREJect"
    paramin = "LFReJect"
    #paramin = "FIFTy"
    checked = myparm.checkParam(paramin)
    
    #onderstaande werkt alleen als matrix vierkant is, anders een error.
    #toAnumpy = np.asarray(testparam)
    #listShape = toAnumpy.shape
    #print(type(listShape))
    #print(len(listShape))
    #print(testparam[0][1])
    #mylist = PARAM[testparam[0]][testparam[1]]
    #print(mylist)
    #print("Start testing.")
    #unittest.main()
    #runner = unittest.TextTestRunner()
    #runner.run(suite())
    #print("Finished testing.")

#DeviceName = "HantekDSO6022BE"
#VendorID = "VID_04B5"
#ProductID = "PID_602A"
#DeviceClassGUID = "{36fc9e60-c465-11cf-8056-444553540000}"
#Date MUST be in MM/DD/YYYY format
#Date = "08/12/2017"

#def probeer1():

    #dev = usb.core.find(idVendor=VendorID, idProduct=ProductID,DeviceClassGUID=DeviceClassGUID)  # Vervang met jouw USB VID/PID
    #if dev is None:
    #    raise ValueError('Device not found')

    #dev.set_configuration()
    # Stuur USBTMC-commando’s
    
# Vervang VID en PID met de waarden van jouw Hantek 6022
#dev = usb.core.find(idVendor=VendorID, idProduct=ProductID)


#if dev is None:
#    print("Hantek 6022 niet gevonden")
#else:
#    print(f"Hantek 6022 gevonden: {dev}")

