import pyvisa
import numpy as np

rm = pyvisa.ResourceManager()
inst:pyvisa.resources.MessageBasedResource = rm.open_resource("TCPIP::127.0.0.1::5025::SOCKET")
inst.timeout = 10000  # ms
inst.read_termination = '\n'
inst.write_termination = '\n'

#print(inst.query("*IDN?"))  # Hantek,6022BL,123456,1.0
print(inst.query_binary_values("CAPTURE?", datatype='B', is_big_endian=False, container=np.ndarray))  # Meetdata van de oscilloscoop

#print(inst.read_bytes(count=200))
inst.close()
