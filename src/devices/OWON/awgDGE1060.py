import pyvisa
#dit is wat testcode omdat ik aan het klieren was om de own awg dge1060 aan de praat te krijgen onder python
#backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.dll")
#dev = usb.core.find(idVendor=0x5345, idProduct=0x1235, backend=backend)

rm=pyvisa.ResourceManager('@py')
rm=pyvisa.ResourceManager('@py')
    
print(rm.list_resources())
print(rm.list_resources_info())
infos = rm.list_resources_info()
for k, v in infos.items():
    #print("key: ",k, " value: ",v)
    print(v.resource_name,v.alias)

dev=rm.open_resource("USB0::21317::4661::24500365::0::INSTR")
dev.timeout = 2000  # ms
dev.read_termination = '\n'
dev.write_termination = '\n'
print(dev.query("*IDN?"))
dev.write("OUTPut1:STATe ON")