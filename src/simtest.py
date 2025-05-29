import usb.core
import usb.backend.libusb1
#USB\VID_5345&PID_1235
backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\pyenv\\labcontrol\\Scripts\\libusb-1.0.dll")
dev = usb.core.find(idVendor=0x5345, idProduct=0x1235, backend=backend)
dev.write(1, "SOURce1:FUNCtion:SHAPe SINusoid")
dev.write(1, "SOURce1:FREQuency:FIXed 5kHz")
dev.write(1, "OUTPut1:STATe ON")
print(dev)