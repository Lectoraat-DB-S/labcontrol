import pickle
#from tektronix.scope.Acquisitions import TekTrace
from devices.siglent.sds.Channels import SDSChannel

def testChan(mylog):
    chan = SDSChannel(1, None, mylog)
    #tracie = TekTrace()
    chan._WFP._code_per_div=8

    # open a file, where you ant to store the data
    file = open('traceDump.dat', 'wb')

#Here's an example dict
#grades = { 'Alice': 89, 'Bob': 72, 'Charles': 87 }

#Use dumps to convert the object to a serialized string
    pickle.dump(chan, file )

    file.close()
#Use loads to de-serialize an object
#received_grades = pickle.load( serial_grades )

def readTheChan():
    mywvp = pickle.load(open('traceDump.dat', 'rb'))
    print(mywvp)
