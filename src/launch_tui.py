#!/usr/bin/env python3
"""LabControl TUI Launcher"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tui.LabControlTUI import main

if __name__ == '__main__':
    main()
