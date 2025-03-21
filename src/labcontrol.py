import pyvisa
import logging
#import core.Settings as setting
#import core.myconfig as configje
#import measurements.weerstandsmetingDMM as measurement
import measurements.transistorcurve as curfje

import tests.testSDG as sigTest
import tests.testSDS as scopeTest
import control.gutter as gootje
from devices.BaseScope import BaseChannel, BaseScope, BaseHorizontal, BaseVertical, BaseWaveForm, BaseWaveFormPreample
from devices.siglent.sds.Scopes import  SiglentScope
#from devices.tektronix.scope.TekScopes import TekScope, TekHorizontal, TekTrigger

import matplotlib.pyplot as plt
import numpy as np

def initLog():
    logging.basicConfig(filename='labcontrol.log',
                            format='%(asctime)s %(module)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')

def dummyUse():
    scope = BaseScope()
    scope.horizontal.timediv=1e-3 #1ms/div
    trig = scope.trigger
    trig.setSource(2)
    ch1 = scope.vertical.chan(1)
    chs = scope.vertical.channels
    ch1.capture()
    wfdata = ch1.WFP
    trace = ch1.WF
    #plt.plot(trace.rawXdata, trace.rawYdata)
    plt.plot(trace.scaledXdata, trace.scaledYdata)
    
    
    plt.show()

#def testSiglent():
#    sigTest.doTheTest()

def performTransCurve():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    curfje.createTransCurve()


if __name__ == "__main__":
    
    #m=pyvisa.ResourceManager()
    #print(rm.list_resources()*****************************)  
    #dummyUse()
    performTransCurve()
    
    #logger = logging.getLogger(__name__)
    #logger.setLevel(logging.DEBUG)

    #testPickle(logger)
    #initLog()
    #logging.info('Main Started')
    #rm = pyvisa.ResourceManager()
    #myList=rm.list_resources()
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