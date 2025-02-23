
import pyvisa
import logging
#import measurements.weerstandsmetingDMM as measurement
#import measurements.transistorcurve as curfje

import tests.testSDG as sigTest
import tests.testSDS as scopeTest
import control.gutter as gootje
from devices.BaseScope import BaseScope, FakeScopie

import matplotlib.pyplot as plt
import numpy as np


def initLog():
    logging.basicConfig(filename='labcontrol.log',
                            format='%(asctime)s %(module)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')



#def testSiglent():
#    sigTest.doTheTest()

def performTransCurve():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())


if __name__ == "__main__":
    
    rm=pyvisa.ResourceManager()
    print(rm.list_resources())
    #BaseScope.register(FakeScopie)
    scoopje = BaseScope()
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
    #trace=gootje.aquireSamplesFromDistSensor()
    #np.save("sanyo_dump.dat",trace)
    #plt.plot(trace)
    #plt.show()
    #testSiglent()
    #measurement.meetInterneWeerstandGenerator()
    #curfje.createTransCurve()
    scopeTest.testTheSDS()
    #dmmtest.testDMM()
    #logging.info('Finished') 