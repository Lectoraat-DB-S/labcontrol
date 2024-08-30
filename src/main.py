
import pyvisa
import measurements.weerstandsmetingDMM as measurement
import tests.testSiglent as sigTest

def main():
    measurement.meetInterneWeerstandGenerator()

def testSiglent():
    sigTest.testAllParam()
    

if __name__ == "__main__":
    #main()
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    #testSiglent()
    measurement.meetInterneWeerstandGenerator()