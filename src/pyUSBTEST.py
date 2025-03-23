import usb.core
import usb.util

DeviceName = "HantekDSO6022BE"
VendorID = "VID_04B5"
ProductID = "PID_602A"
DeviceClassGUID = "{36fc9e60-c465-11cf-8056-444553540000}"
#Date MUST be in MM/DD/YYYY format
Date = "08/12/2017"

def probeer1():

    #dev = usb.core.find(idVendor=VendorID, idProduct=ProductID,DeviceClassGUID=DeviceClassGUID)  # Vervang met jouw USB VID/PID
    if dev is None:
        raise ValueError('Device not found')

    dev.set_configuration()
    # Stuur USBTMC-commando’s
    
import usb.core

# Vervang VID en PID met de waarden van jouw Hantek 6022
dev = usb.core.find(idVendor=VendorID, idProduct=ProductID)


if dev is None:
    print("Hantek 6022 niet gevonden")
else:
    print(f"Hantek 6022 gevonden: {dev}")