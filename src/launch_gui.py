#!/usr/bin/env python3
"""
LabControl GUI Launcher
Launch the unified lab equipment control interface
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check dependencies
try:
    import PyQt5
    print("✓ PyQt5 found")
except ImportError:
    print("✗ PyQt5 not found. Install with: pip install PyQt5")
    sys.exit(1)

try:
    import pyqtgraph
    print("✓ pyqtgraph found")
except ImportError:
    print("⚠ pyqtgraph not found. Install with: pip install pyqtgraph")
    print("  (GUI will work but scope visualization will be limited)")

# Import and run main window
from gui.MainWindow import main

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  LabControl - Unified Lab Equipment Control")
    print("="*60)
    print("\nStarting GUI...\n")

    main()
