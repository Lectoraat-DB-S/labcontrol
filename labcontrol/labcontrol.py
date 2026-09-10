import libusb_package
import usb.core
import usb.backend.libusb1
import time

import logging
import serial
import configparser
import pyvisa
import threading
from multiprocessing import Process
import libusb_package

#import measurements.weerstandsmetingDMM as measurement
import measurements.transistorcurve as curfje
import measurements.IRLEDCurve as ledcurve
import measurements.frequencyResponse as freqResp
from devices.Korad.KoradSupply import Korad3305P

#import tests.testSDG as sigTest
#import tests.testSDS as scopeTest
#import control.gutter as gootje
from devices.BaseScope.BaseScope import Scope
from devices.BaseScope.BaseChannel import Channel
from devices.BaseScope.BaseVertical import Vertical
from devices.BaseScope.BaseFunctions import FFT
from devices.BaseGenerator import BaseGenerator, BaseGenChannel
from devices.BaseDMM import BaseDMM
#from devices.siglent.sds.SDS1000.SDS1k import  SiglentScope
#from devices.tektronix.scope.TekScopes import TekScope, TekHorizontal, TekTrigger
from devices.BaseSupply import BaseSupply, BaseSupplyChannel


import matplotlib.pyplot as plt
import numpy as np
import unittest

#from src.tests.MockResMan import MockerRM
from unittest.mock import call, patch, MagicMock
from pyvisa import ResourceManager
from pyvisa import ResourceManager as rm
#from devices.Hantek import ServerGui

#from tests import checkTDS
from measurements.frequencyResponse import doACSweep
import devices.BaseLabDeviceUtils as bu
from devices.siglent.sds.util import SiglentIDN
import usbtmc
from scipy.fft import fft
#from devices.BaseLabDeviceUtils import PhaseFittingProcess, PhaseFittingProcessProxy, FitProcessQueueData
#from devices.BaseScope.BaseFunctions import PhaseEstimator
from multiprocessing import Process, Queue
from devices.BaseScope.BaseChannel import WaveForm


logger = logging.getLogger(__name__)

def analyseerScopeKnoppies():
    """Een script van CHatGPT. Werkt voor geen meter."""
    import pyvisa
    import csv
    import time

    RESOURCE = "TCPIP0::192.168.1.240::INSTR"

    rm = pyvisa.ResourceManager()
    scope = rm.open_resource(RESOURCE)

    scope.write("*CLS")
    scope.write("*ESE 64")

    seen = {}

    with open("siglent_keys.csv", "w", newline="") as f:

        writer = csv.writer(f)
        writer.writerow(["timestamp", "urr"])

        print("Press buttons on the oscilloscope...")

        while True:

            esr = int(scope.query("*ESR?"))

            if esr & 0x40:

                urr = scope.query("URR?").strip()

                ts = time.time()

                writer.writerow([ts, urr])
                f.flush()

                if urr not in seen:
                    seen[urr] = 1
                    print(f"NEW KEYCODE: {urr}")
                else:
                    seen[urr] += 1
                    print(f"KEYCODE {urr} count={seen[urr]}")

            time.sleep(0.02)

def testEthConfig():
    bu.setEthernet()

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


def testTekVisa():
    scope: Scope = Scope.getDevice()
    scopeVert: Vertical = scope.vertical
    scopeChan1: Channel = scopeVert.chan(1)
    scopeChan2: Channel = scopeVert.chan(2)
    start = time.time()
    scopeChan1.capture()
    end = time.time()
    print(f"1 maal een capture kost: {end-start}")
    

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
    initLog()
    #dmm:BaseDMM = BaseDMM.getDevice()
    #print(dmm.get_current())
    #gen:BaseGenerator = BaseGenerator.getDevice()
    #mygenChan: BaseGenChannel = gen.chan(chanNr=1)
    #mygenChan.setAmp(1.2)
    scope:Scope = Scope.getDevice()
    #scope.trigger.mode('SINGLE')
    vert:Vertical = scope.vertical
    chan1: Channel = vert.chan(1)
    myfft:FFT = vert.getMath("FFT", chan1)
    xdat, ydat = myfft.get()
    #plt.figure()
    #plt.plot(xdat, abs(ydat))
    #plt.show()
    fig = myfft.plot(linear=True, autoRange=False)
    print(max(abs(ydat)))
    plt.show()
    #chan1:BaseSupplyChannel=supply.chan(1)
    #chan1.setV(10)
    #chan1.enable(True)
    #print("")
    
   
   
        #chan1.capture()
        #trig = scope.trigger
        #trig.setSource(2)
        #chan1 = gen.chan(1)
        #chan1.setfreq(100000)
        #chan1.enableOutput(True)
        #

#def testSiglent():
#    sigTest.doTheTest()

def maakIRLEDcurve():
    ledcurve.createCurve()

def performTransCurve():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    curfje.measHFECurve()
    

def testKorad():
    #ser = serial.Serial('COM10', 9600, timeout=0, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8)
    #ser.write(b"*IDN?\r")
    #ser.write(b"OUT0\r")
    supply = Korad3305P()
    #line = ser.readline()
    #print(line)
    #USB\VID_5345&PID_1235 (libwdi autogenerated)

def testmultiproc():
    queue1 = Queue()
    queue2 = Queue()    
    myprocdata = FitProcessQueueData(1, 2, 3, 4, [0,1,2,3,4,5], [0,1,2,3,4,5])
    p1 = PhaseFittingProcess(inQueue=queue1, outQueue=queue2)
    p1.start()
    
    queue1.put([myprocdata])
    print(queue2.get())
    print("send process message to stop")
    queue1.put("STOP")
    print("Wait for process to join")
    p1.join()
    print("Process joined. Bye, Bye......")

def testEstimator():
    inputWF: WaveForm = WaveForm()
    outputWF: WaveForm = WaveForm()
    print("testimator: creating data fitrun 1")
    inputWF.scaledXdata =  [0,1,2,3,4,5]
    inputWF.scaledYdata =  [0,1,2,3,4,5]
    outputWF.scaledXdata =  [0,1,2,3,4,5]
    outputWF.scaledYdata =  [0,1,2,3,4,5]
    pe = PhaseEstimator(inputWF=inputWF,outputWF=outputWF, debugPrint=True)
    #pe.create_mp_fit_workers()
    pe.setAPriori(1,1,2,0,1)
    #pe.startFitting()
    #pe.WaitForFitResult()
    print(pe.estimate())
    print("testimator: creating data fitrun 2")
    inputWF.scaledYdata =  [5,4,3,2,1,0]
    outputWF.scaledYdata =  [5,4,3,2,1,0]
    pe.setAPriori(3,1,1,1,-1)
    #pe.startFitting()
    #pe.WaitForFitResult()
    print(pe.estimate())
    
    
    pe.quit()
    
def testIEEEreg():
    #scope.visaInstr.write("C1:WF? DAT2")
    #print(scope.getEXR())
    
    #scope.visaInstr.write('INIT')
    #scope.visaInstr.write('*OPC')
    #print(scope.visaInstr.query('*ESR?'))
    #print(scope.visaInstr.query('*STB?'))
    #chan1:Channel = scope.vertical.chan(1)
    #print("Start capture")
    #chan1.capture()
    #scope.visaInstr.write("C1:WF? DAT2;*WAI")
    #print(scope.visaInstr.query('*ESR?'))
    
    waarde = scope.visaInstr.read_stb()
    #while waarde ==0:
    #    waarde = scope.visaInstr.read_stb()
    
    
    #scope.visaInstr.write("C1:WF? DAT2")
    #print("capture started")
    #print(scope.visaInstr.read_stb())
    #print("close instrument + exit")
    #scope.visaInstr.close()
    #scope.visaInstr.write("CLS")
    #"*RST;*OPC?\n"
    #scope.visaInstr.write("*RST;*OPC")
    #scope.visaInstr.write("*OPC")
    #while True:
        # Read the event status register
        #esr = int(scope.visaInstr.query('*ESR?'))
        #if (esr & 1):  # Check if Operation Complete (Bit 0) is true
        #    print("Operation complete!")
        #    break
    #print(scope.visaInstr.query("*OPC?"))
    
    
    scope:Scope = Scope.getDevice()
    vert: Vertical = scope.vertical
    mychan: Channel = vert.chan(1)
    if scope == None:
        print("geen scope gevonden!")
        exit()
    scope.write("*RST")
    print("scope resetted")
    msg = scope.getESE()  
    print(f"ESE resp = {msg}") 
    scope.write("*CLS")   
    scope.write("*ESE 73") #zie de prog SDS
    scope.write("*SRE 254")
    print("Getting ESE after setting ESE to 72")
    msg = scope.getESE()  
    print(f"ESE resp = {msg}") 
    msg = scope.query("*SRE?")
    print(f"SRE resp = {msg}")
    while True:
        msg = scope.getINR()
        print(f"INR resp = {msg}")
        mychan.capture()
        msg = scope.getESR()  
        print(f"ESR resp = {msg}")
        msg = scope.getEXR()
        print(f"EXR resp = {msg}")
        msg = scope.getCMR()
        print(f"CMR resp = {msg}")
        msg = scope.SRE()
        print(f"SRE resp = {msg}")
        msg = scope.getSTB()
        print(f"STB resp = {msg}")
        msg = scope.visaInstr.read_stb()
        print(f"stb function says {msg}")
        #msg = scope.URR()
        print(scope.visaInstr.query("ALL_STATUS?"))
        #print(f"URR resp = {msg}")
        time.sleep(5)
    
    

if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    urls = rm.list_resources()
    print(urls)
        
    
    #testEstimator()
    #VBB_array = np.array([1, 2, 3, 4, 5])
    #VBE_array = np.array([0, 0.2, 0.3, 0.4, 0.5])
    #RB=100e3
    #myiblist = curfje.berekenStroomDoor(RB, list(VBB_array),list(VBE_array))
    #print(myiblist)
    
    freqResp.doACSweep()
    
    #performTransCurve()
    #logging.basicConfig(filename='myapp.log', level=logging.INFO)
    #logger.info('Started')
    #bu.testlmfit()
    #bf.testlmfit()
    #a  = input()
    #bu.setEthernet()
    #maakIRLEDcurve()
    #input("druk toets om te starten")
    #dummyUse()
    #input("druk toets om te stoppen .....")
    
    #ledcurve.testDiodePlotCurve()
    #doACSweep()
    #testUSBTMC()
    #testTekTm()

    #gen = BaseGenerator.getDevice()
    #checkTDS.checkMathFunctions()
    #print(rm.list_resources_info())  
    #testHantek()
    #testTekVisa()
    #dummyUse()
    #testKorad()
    #performTransCurve()
    #logger = logging.getLogger(__name__)
    #logger.setLevel(logging.DEBUG)
    #plt.show()