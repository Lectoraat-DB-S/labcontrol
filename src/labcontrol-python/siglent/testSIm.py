import pyvisa
#from tektronix.scope.TekScopes import TekScope

rm = pyvisa.ResourceManager('@sim')
print(rm.list_resources())
inst = rm.open_resource('TCPIP0::localhost::inst0::INSTR', read_termination='\n')
print(inst.query("?IDN"))
