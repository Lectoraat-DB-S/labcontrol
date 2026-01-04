#!/bin/bash
# Install script for Hantek 6022 automatic firmware flashing via udev
# This enables plug-and-play support for the Hantek oscilloscope

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_DIR="/usr/share/hantek6022"
UDEV_RULES="/etc/udev/rules.d/60-hantek-autoflash.rules"

echo "=== Hantek 6022 udev installer ==="

# Check for cycfx2prog
if ! command -v cycfx2prog &> /dev/null; then
    echo "cycfx2prog not found. Installing..."
    sudo pacman -S --noconfirm cycfx2prog
fi

echo "cycfx2prog: OK"

# Create firmware directory and copy files
echo "Installing firmware files..."
sudo mkdir -p "$FIRMWARE_DIR"
sudo cp "$SCRIPT_DIR/src/devices/Hantek6022API/PyHT6022/Firmware/HEX/"*.hex "$FIRMWARE_DIR/"
echo "Firmware installed to $FIRMWARE_DIR"

# Install udev rules
echo "Installing udev rules..."
sudo cp "$SCRIPT_DIR/60-hantek-autoflash.rules" "$UDEV_RULES"

# Reload udev rules
echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# Remove old rules if present
if [ -f "/etc/udev/rules.d/60-openhantek.rules" ]; then
    echo "Removing old openhantek rules..."
    sudo rm -f /etc/udev/rules.d/60-openhantek.rules
fi

echo ""
echo "=== Installation complete ==="
echo ""
echo "Now unplug and replug your Hantek scope."
echo "The firmware will be automatically flashed when plugged in."
echo ""
echo "Check with: lsusb | grep -i hantek"
echo "  - VID 04b4: No firmware (being flashed)"
echo "  - VID 04b5: Firmware loaded (ready to use)"
