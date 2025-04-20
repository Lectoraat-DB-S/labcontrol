import pyvisa

rm = pyvisa.ResourceManager()
inst = rm.open_resource("TCPIP::127.0.0.1::5025::INSTR")

print(inst.query("*IDN?"))  # Hantek,6022BL,123456,1.0
print(inst.query("MEASURE?"))  # Meetdata van de oscilloscoop
inst.close()
