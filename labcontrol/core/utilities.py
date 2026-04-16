import usb.core
import usb.backend.libusb1

backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.dll")
dev = usb.core.find(idVendor=0x1234, idProduct=0x5678, backend=backend)