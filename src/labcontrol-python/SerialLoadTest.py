import pickle
from tektronix.scope.Acquisitions import TekTrace

# open a file, 
file = open('traceDump', 'rb')
data = pickle.load(file)
print(data)
data.dump()
file.close()