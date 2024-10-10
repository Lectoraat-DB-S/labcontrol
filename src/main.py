
import pyvisa
import measurements.weerstandsmetingDMM as measurement
import measurements.transistorcurve as curfje

import tests.testSDG as sigTest
import tests.testSiglent as dmmtest
import tests.testSDS as scopeTest
import control.gutter as gootje

def main():
    measurement.meetInterneWeerstandGenerator()

#def testSiglent():
#    sigTest.doTheTest()

def performTransCurve():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())


if __name__ == "__main__":
    #main()
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    #dev=rm.open_resource("USB0::0x5345::0x1235::23390166::INSTR")
    #print(dev.query("*IDN?"))
    #print(dev.query("MMEMory:CATalog?"))
    #gootje.controlBall()
    #testSiglent()
    #measurement.meetInterneWeerstandGenerator()
    #curfje.createTransCurve()
    #scopeTest.testTheSDS()
    dmmtest.testDMM()