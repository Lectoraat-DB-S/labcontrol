import pyvisa as visa

rm = visa.ResourceManager("@sim")

print(rm.list_resources())
inst = rm.open_resource("USB::0x1111::0x2222::0x2468::INSTR")
#inst.timeout = 10000  # ms
inst.read_termination = "\n"
inst.write_termination = "\n"
desc=inst.query("*IDN?")
print(desc)