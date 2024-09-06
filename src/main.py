
import pyvisa
import measurements.weerstandsmetingDMM as measurement
import tests.testSiglent as sigTest
import control.gutter as gootje

def main():
    measurement.meetInterneWeerstandGenerator()

def testSiglent():
    sigTest.testAllParam()
    

if __name__ == "__main__":
    #main()
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    #dev=rm.open_resource("USB0::0x5345::0x1235::23390166::INSTR")
    #print(dev.query("*IDN?"))
   # print(dev.query("MMEMory:CATalog?"))
    #gootje.controlBall()
    #testSiglent()
    measurement.meetInterneWeerstandGenerator()