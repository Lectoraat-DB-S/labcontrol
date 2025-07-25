import libusb_package
import usb.core
import usb.backend.libusb1
import time



from tm_devices import DeviceManager
from tm_devices.drivers import MSO4B
from tm_devices.helpers import PYVISA_PY_BACKEND, SYSTEM_DEFAULT_VISA_BACKEND
import logging
import serial
import configparser
import pyvisa
import threading
from multiprocessing import Process
import libusb_package

#import measurements.weerstandsmetingDMM as measurement
import measurements.transistorcurve as curfje
from devices.Korad.KoradSupply import Korad3305P

#import tests.testSDG as sigTest
#import tests.testSDS as scopeTest
#import control.gutter as gootje
from devices.BaseScope import BaseChannel, BaseScope, BaseHorizontal, BaseVertical, BaseWaveForm, BaseWaveFormPreample
from devices.BaseGenerator import BaseGenerator
from devices.siglent.sds.Scopes import  SiglentScope
from devices.tektronix.scope.TekScopes import TekScope, TekHorizontal, TekTrigger

import matplotlib.pyplot as plt
import numpy as np
import unittest

#from src.tests.MockResMan import MockerRM
from unittest.mock import call, patch, MagicMock
from pyvisa import ResourceManager
from pyvisa import ResourceManager as rm
#from devices.Hantek import ServerGui

from tests import checkTDS
from measurements.frequencyResponse import doACSweep

import usbtmc
def testUSBTMC():
    
    for dev in libusb_package.find(find_all=True):
        print(dev)

    backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\Users\\p78511225\\.pyenv\\pyenv-win\\versions\\3.13.3\\Scripts\\libusb-1.0.dll")
    #dev = usb.core.find(idVendor=0x0699, idProduct=0x03A1, backend=backend)
    #libusb1_backend = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)
    #print(list(usb.core.find(find_all=True, backend=libusb1_backend)))
    #VID_0699&PID_03A1\C012743 
    #parent: VID_0BDA&PID_5411
    #instr =  usbtmc.Instrument("USB::0x0699::0x03A1::INSTR")
    instr =  usbtmc.Instrument(idVendor=0x0699, idProduct=0x03A1)
    #print(instr.ask("*IDN?"))
    instr.write_raw("CURVE?")
    #dev.write(endpoint=0x6, data="*IDN?")

def testTekTm():
    with DeviceManager(verbose=True) as device_manager:
        # Explicitly specify to use the system VISA backend, this is the default,
        # **this code is not required** to use the system default.
        device_manager.visa_library = SYSTEM_DEFAULT_VISA_BACKEND
        # The above code can also be replaced by:
        device_manager.visa_library = "@ivi"

        # To use the PyVISA-py backend
        #device_manager.visa_library = PYVISA_PY_BACKEND
        # The above code can also be replaced by:
        #device_manager.visa_library = "@py"
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()
        print(urls)
        myscope = device_manager.add_scope("USB::0x0699::0x03A1::C012743::INSTR")
        print(myscope)

def testTekVisa():
    scope: BaseScope = BaseScope.getDevice()
    scopeVert: BaseVertical = scope.vertical
    scopeChan1: BaseChannel = scopeVert.chan(1)
    scopeChan2: BaseChannel = scopeVert.chan(2)
    start = time.time()
    scopeChan1.capture()
    end = time.time()
    print(f"1 maal een capture kost: {end-start}")
    

def testHantek():
    ServerGui.createApp()
    


def readConfig():
    config = configparser.ConfigParser()
    config.sections()
    config.read('labcontrol.ini')

def initLog():
    logging.basicConfig(filename='labcontrol.log',
                            format='%(asctime)s %(module)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')

def dummyUse():
    scope = BaseScope.getDevice()
    #gen: BaseGenerator = BaseGenerator.getDevice()
    scope.horizontal.setTimeDiv(0.5e-3) #1ms/div
    chan1 = scope.vertical.chan(1)
    chan1.capture()
    #trig = scope.trigger
    #trig.setSource(2)
    #chan1 = gen.chan(1)
    #chan1.setfreq(100000)
    #chan1.enableOutput(True)
    #
#def testSiglent():
#    sigTest.doTheTest()

def performTransCurve():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    curfje.createTransCurve()
    

def testKorad():
    #ser = serial.Serial('COM10', 9600, timeout=0, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8)
    #ser.write(b"*IDN?\r")
    #ser.write(b"OUT0\r")
    supply = Korad3305P()
    #line = ser.readline()
    #print(line)
    #USB\VID_5345&PID_1235 (libwdi autogenerated)

if __name__ == "__main__":
    #rc = ResourceManager(visa_library="@mock")
    
    #testUSBTMC()
    #testTekTm()

    #gen = BaseGenerator.getDevice()
    #checkTDS.checkMathFunctions()
    #print(rm.list_resources_info())  
    #testHantek()
    testTekVisa()
    #dummyUse()
    #testKorad()
    #performTransCurve()
    #logger = logging.getLogger(__name__)
    #logger.setLevel(logging.DEBUG)

    #testPickle(logger)
    #initLog()0
    #logging.info('Main Started')
  
    #scope = BaseScope()
    #vertie = scope.vertical
    #print(vertie)
    
    #vertie.chan()
    #chan1 = scope.vertical.getchan(1)
    #chan1.capture()
    #print(myList)
    #mydev = rm.open_resource(myList[0])
    #print(mydev.timeout)
    #dev=rm.open_resource("USB0::0x5345::0x1235::23390166::INSTR")
    #print(dev.query("*IDN?"))
    #print(dev.query("MMEMory:CATalog?"))
    #plt.figure(1)
    #trace=gootje.aquireSampl-esFromDistSensor()
    #np.save("sanyo_dump.dat",trace)
    #plt.plot(trace)
    #plt.show()
    #testSiglent()
    #measurement.meetInterneWeerstandGenerator()
    #curfje.createTransCurve()
    #scopeTest.testTheSDS()
    #dmmtest.testDMM()
    #logging.info('Finished') 