#!/usr/bin/env python3
"""
Quick USB reset utility for Hantek scope
Use this if you get LIBUSB_ERROR_BUSY errors
"""

import sys
import time

import usb1


def reset_hantek_usb():
    """Reset Hantek USB connection"""
    print("🔧 Hantek USB Reset Utility")
    print("=" * 50)
    print()

    try:
        context = usb1.USBContext()

        # Hantek VID/PID combinations
        devices_to_check = [
            (0x04B5, 0x6022, "Hantek 6022BE (firmware loaded)"),
            (0x04B4, 0x6022, "Hantek 6022BE (no firmware)"),
            (0x04B5, 0x602A, "Hantek 6022BL (firmware loaded)"),
            (0x04B4, 0x602A, "Hantek 6022BL (no firmware)"),
        ]

        found_devices = []

        print("Scanning for Hantek devices...")
        for vid, pid, name in devices_to_check:
            try:
                device = context.getByVendorIDAndProductID(vid, pid)
                if device:
                    found_devices.append((device, vid, pid, name))
                    print(f"  ✓ Found: {name}")
            except Exception as e:
                pass

        if not found_devices:
            print("\n❌ No Hantek devices found!")
            print("\nMake sure:")
            print("  1. Your Hantek scope is plugged in")
            print("  2. USB cable is properly connected")
            print("  3. You have proper USB permissions")
            return False

        print(f"\nFound {len(found_devices)} Hantek device(s)")
        print()

        # Try to reset each device
        for device, vid, pid, name in found_devices:
            print(f"Resetting {name}...")
            try:
                handle = device.open()
                # Try to release all interfaces
                for interface in range(4):  # Hantek typically uses interface 0
                    try:
                        if handle.kernelDriverActive(interface):
                            print(f"  - Detaching kernel driver from interface {interface}")
                            handle.detachKernelDriver(interface)
                    except:
                        pass

                    try:
                        handle.releaseInterface(interface)
                    except:
                        pass

                # Close handle
                handle.close()
                print(f"  ✓ Reset complete")

            except usb1.USBErrorBusy:
                print(f"  ⚠ Device is busy - attempting force reset...")
                try:
                    # Try alternate approach
                    handle = device.open()
                    handle.resetDevice()
                    handle.close()
                    print(f"  ✓ Force reset successful")
                except Exception as e2:
                    print(f"  ❌ Could not reset: {e2}")
                    print(f"\n  Manual fix required:")
                    print(f"  1. Unplug the Hantek scope")
                    print(f"  2. Wait 3 seconds")
                    print(f"  3. Plug it back in")
                    return False

            except Exception as e:
                print(f"  ⚠ Error: {e}")

        print()
        print("✓ USB reset complete!")
        print("\nYou can now use your Hantek scope with the GUI or TUI.")
        return True

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nManual fix:")
        print("  1. Unplug your Hantek scope")
        print("  2. Wait 3 seconds")
        print("  3. Plug it back in")
        return False

if __name__ == "__main__":
    print()
    success = reset_hantek_usb()
    print()

    if not success:
        sys.exit(1)

    sys.exit(0)
