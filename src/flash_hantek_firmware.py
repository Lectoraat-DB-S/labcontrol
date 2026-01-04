#!/usr/bin/env python3
"""
Hantek Scope Firmware Flasher
==============================

This script safely flashes firmware to Hantek DSO-6022 series oscilloscopes.

WHY A SEPARATE SCRIPT?
- Firmware flashing causes USB re-enumeration
- This can trigger crashes in GUI applications (especially on Wayland)
- Running in a separate process isolates the GUI from USB instability

USAGE:
    python src/flash_hantek_firmware.py

SUPPORTED DEVICES:
- Hantek DSO-6022BE
- Hantek DSO-6022BL
- Hantek DSO-6021

After flashing, unplug and replug the device, then start the GUI.
"""

import os
import sys
import time

# Add src directory to path (this script is already in src/)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import usb1

    from devices.Hantek6022API.PyHT6022.LibUsbScope import Oscilloscope
except ImportError as e:
    print("ERROR: Required libraries not found")
    print(f"  {e}")
    print("\nPlease install dependencies:")
    print("  pip install libusb1 PyHT6022")
    sys.exit(1)


def find_hantek_device():
    """Find connected Hantek scope"""
    context = usb1.USBContext()

    # Check for devices with and without firmware
    for vid in [Oscilloscope.FIRMWARE_PRESENT_VENDOR_ID, Oscilloscope.NO_FIRMWARE_VENDOR_ID]:
        for pid in [Oscilloscope.PRODUCT_ID_BL, Oscilloscope.PRODUCT_ID_BE, Oscilloscope.PRODUCT_ID_21]:
            device = context.getByVendorIDAndProductID(vid, pid)
            if device:
                model = "DSO-6022BL" if pid == Oscilloscope.PRODUCT_ID_BL else \
                        "DSO-6022BE" if pid == Oscilloscope.PRODUCT_ID_BE else \
                        "DSO-6021"
                has_fw = (vid == Oscilloscope.FIRMWARE_PRESENT_VENDOR_ID)
                return device, vid, pid, model, has_fw

    return None, None, None, None, None


def main():
    print("=" * 60)
    print("  Hantek Oscilloscope Firmware Flasher")
    print("=" * 60)
    print()

    # Find device
    print("Searching for Hantek scope...")
    device, vid, pid, model, has_firmware = find_hantek_device()

    if not device:
        print("✗ No Hantek scope found!")
        print("\nTroubleshooting:")
        print("  1. Is the scope plugged in?")
        print("  2. Check USB cable connection")
        print("  3. Try a different USB port")
        print("  4. Check permissions: sudo chmod 666 /dev/bus/usb/*/*")
        return 1

    print(f"✓ Found: {model}")
    print(f"  VID: 0x{vid:04x}, PID: 0x{pid:04x}")

    if has_firmware:
        print(f"  Firmware: Already present (version 0x{Oscilloscope.FIRMWARE_VERSION:04x})")
        print("\n✓ Device is ready to use!")
        print("\nYou can now:")
        print("  1. Close this window")
        print("  2. Start the GUI: python src/launch_gui.py")
        print("  3. Click 'Discover Devices'")
        return 0
    else:
        print("  Firmware: NOT present - needs flashing")

    print()
    print("-" * 60)
    print("FIRMWARE FLASH PROCEDURE")
    print("-" * 60)
    print()
    print("This will:")
    print("  1. Upload firmware to the device")
    print("  2. Device will disconnect and reconnect")
    print("  3. Take about 5 seconds")
    print()

    response = input("Continue with firmware flash? [y/N]: ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return 0

    print()
    print("Starting firmware flash...")

    try:
        # Create oscilloscope instance
        scope = Oscilloscope(VID=vid, PID=pid)

        # Setup device
        print("  [1/4] Setting up device...")
        if not scope.setup():
            raise RuntimeError("Failed to setup device")

        # Open handle
        print("  [2/4] Opening USB handle...")
        if not scope.open_handle():
            raise RuntimeError("Failed to open device (might be busy)")

        # Flash firmware - this will cause USB re-enumeration
        print("  [3/4] Flashing firmware (this takes a few seconds)...")
        print("        Device will disconnect and reconnect with new VID...")

        # Write firmware packets directly (don't use flash_firmware which
        # tries to re-setup immediately and may fail during re-enumeration)
        if pid == Oscilloscope.PRODUCT_ID_BE:
            from devices.Hantek6022API.PyHT6022.Firmware import dso6022be_firmware as fw
        elif pid == Oscilloscope.PRODUCT_ID_BL:
            from devices.Hantek6022API.PyHT6022.Firmware import dso6022bl_firmware as fw
        elif pid == Oscilloscope.PRODUCT_ID_21:
            from devices.Hantek6022API.PyHT6022.Firmware import dso6021_firmware as fw
        else:
            raise RuntimeError(f"Unknown product ID: {pid}")

        for packet in fw:
            scope.device_handle.controlWrite(0x40, Oscilloscope.RW_FIRMWARE_REQUEST,
                                             packet.value, Oscilloscope.RW_FIRMWARE_INDEX,
                                             packet.data, timeout=60)

        # Close handle before re-enumeration
        try:
            scope.close_handle()
        except:
            pass

        print("  [4/4] Waiting for device to re-enumerate...")
        print("        (VID changes from 0x04b4 to 0x04b5)")

        # Wait for re-enumeration and verify
        time.sleep(2)

        # Check if device re-appeared with firmware
        max_retries = 10
        for i in range(max_retries):
            new_device, new_vid, new_pid, new_model, has_fw = find_hantek_device()
            if has_fw:
                print()
                print("=" * 60)
                print("✓ FIRMWARE FLASH SUCCESSFUL!")
                print("=" * 60)
                print()
                print(f"Device now has VID: 0x{new_vid:04x} (firmware present)")
                print()
                print("You can now start the GUI:")
                print("  python src/launch_gui.py")
                print()
                return 0
            time.sleep(0.5)

        # Device didn't re-appear with firmware - but may still have worked
        print()
        print("⚠ Device re-enumeration check timed out")
        print()
        print("The firmware may still have been flashed successfully.")
        print("Please:")
        print("  1. Unplug the Hantek scope")
        print("  2. Wait 3 seconds")
        print("  3. Plug it back in")
        print("  4. Run this script again to verify")
        print()
        return 0

    except usb1.USBErrorBusy:
        print()
        print("✗ ERROR: Device is busy")
        print()
        print("Fix:")
        print("  1. Close any other scope software")
        print("  2. Unplug the scope")
        print("  3. Wait 5 seconds")
        print("  4. Plug it back in")
        print("  5. Run this script again")
        return 1

    except usb1.USBErrorAccess:
        print()
        print("✗ ERROR: Permission denied")
        print()
        print("Fix (run in terminal):")
        print("  sudo chmod 666 /dev/bus/usb/*/*")
        print()
        print("Or add a udev rule for permanent fix:")
        print('  echo \'SUBSYSTEM=="usb", ATTR{idVendor}=="04b4", MODE="0666"\' | sudo tee /etc/udev/rules.d/50-hantek.rules')
        print("  sudo udevadm control --reload-rules")
        return 1

    except usb1.USBErrorNoDevice:
        print()
        print("✗ ERROR: Device disconnected during flash")
        print()
        print("This can happen if:")
        print("  • USB cable is loose")
        print("  • USB port has power issues")
        print("  • Device is faulty")
        print()
        print("Try:")
        print("  1. Use a different USB cable")
        print("  2. Try a different USB port (USB 2.0 preferred)")
        print("  3. Connect directly to PC (not through hub)")
        return 1

    except Exception as e:
        print()
        print(f"✗ ERROR: {e}")
        print()
        print("Try:")
        print("  1. Unplug and replug the device")
        print("  2. Run this script again")
        print("  3. Check USB cable quality")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(130)
