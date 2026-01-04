#!/bin/bash
# Fix LIBUSB_ERROR_BUSY for Hantek scope
# Run this if you get "Failed to open Hantek scope" errors

echo "🔧 Fixing USB Busy Error for Hantek Scope"
echo "=========================================="
echo ""

# Check if Hantek is connected
echo "1. Checking for Hantek device..."
HANTEK=$(lsusb | grep -i "04b5:602a")
if [ -z "$HANTEK" ]; then
    echo "   ❌ Hantek DSO-6022BL not found!"
    echo "   Please connect your Hantek scope."
    exit 1
else
    echo "   ✓ Found: $HANTEK"
fi

echo ""
echo "2. Checking for processes using Hantek..."
# Check for Python processes
PROCS=$(ps aux | grep -i hantek | grep -v grep)
if [ ! -z "$PROCS" ]; then
    echo "   ⚠ Found processes using Hantek:"
    echo "$PROCS"
    echo ""
    read -p "   Kill these processes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f hantek
        pkill -f Hantek
        echo "   ✓ Processes killed"
    fi
else
    echo "   ✓ No blocking processes found"
fi

echo ""
echo "3. Resetting USB..."
# Method 1: Unbind and rebind (safer)
echo "   Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "4. Solution steps:"
echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   🔌 UNPLUG your Hantek scope"
echo "   ⏱  Wait 3 seconds..."
sleep 1
echo "   ⏱  Wait 2 seconds..."
sleep 1
echo "   ⏱  Wait 1 second..."
sleep 1
echo "   🔌 PLUG IT BACK IN"
echo ""
echo "   Then try your application again!"
echo ""

# Optional: Show device info
echo "5. Device information:"
echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
lsusb -d 04b5:602a -v 2>/dev/null | grep -E "(Bus|Device|idVendor|idProduct|iManufacturer|iProduct)" || echo "   Run with sudo for detailed info"

echo ""
echo "✓ Fix complete!"
echo ""
echo "Now try:"
echo "  ./launch_tui.py"
echo "  or"
echo "  ./launch_gui.py"
