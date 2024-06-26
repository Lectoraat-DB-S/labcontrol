import pickle
from tektronix.scope.Acquisitions import TekTrace

tracie = TekTrace()
tracie.NR_PT = 1
tracie.V_DIV = 1

# open a file, where you ant to store the data
file = open('traceDump', 'wb')

#Here's an example dict
#grades = { 'Alice': 89, 'Bob': 72, 'Charles': 87 }

#Use dumps to convert the object to a serialized string
pickle.dump(tracie, file )

file.close()
#Use loads to de-serialize an object
#received_grades = pickle.load( serial_grades )