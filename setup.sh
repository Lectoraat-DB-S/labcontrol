#!/bin/bash
# LabControl Setup Script for Linux/Mac
# Creates venv and installs all dependencies

set -e

echo "========================================"
echo "  LabControl Setup"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "src/requirements.txt" ]; then
    echo "Error: Run this script from the labcontrol root directory"
    exit 1
fi

# Create virtual environment
echo ""
echo "[1/3] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo ""
echo "[2/3] Installing dependencies..."
pip install -r src/requirements.txt

# Install Hantek6022API from submodule
echo ""
echo "[3/3] Installing Hantek6022 driver..."
pip install -e src/devices/Hantek6022API

echo ""
echo "========================================"
echo "  Setup complete!"
echo "========================================"
echo ""
echo "To start LabControl:"
echo "  source venv/bin/activate"
echo "  cd src && python launch_gui.py   # GUI"
echo "  cd src && python launch_tui.py   # TUI"
echo ""
echo "To install desktop shortcuts (Linux), run:"
echo "  ./install.sh"
echo ""
