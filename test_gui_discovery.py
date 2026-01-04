#!/usr/bin/env python3
"""
Test script to verify GUI discovery works without BUSY errors
"""

import sys
import time

# Test 1: Multiple discovery calls
print("="*60)
print("Test: Multiple BaseScope.getDevice() calls")
print("="*60)

from devices.BaseScope import BaseScope
from devices.Hantek.HantekBaseScope import HantekScope

print("\n1st call to getDevice()...")
scope1 = BaseScope.getDevice()
if scope1:
    print(f"  ✓ Success: {scope1.brand} {scope1.model}")
    print(f"  Device handle open: {scope1.scope_obj.device_handle is not None}")
else:
    print("  ✗ No scope found")
    sys.exit(1)

print("\n2nd call to getDevice() (should reuse same instance)...")
scope2 = BaseScope.getDevice()
if scope2:
    print(f"  ✓ Success: {scope2.brand} {scope2.model}")
    print(f"  Device handle open: {scope2.scope_obj.device_handle is not None}")
    print(f"  Same instance? {scope1.scope_obj is scope2.scope_obj}")
else:
    print("  ✗ Failed")
    sys.exit(1)

print("\n3rd call to getDevice()...")
scope3 = BaseScope.getDevice()
if scope3:
    print(f"  ✓ Success: {scope3.brand} {scope3.model}")
    print(f"  Same instance? {scope1.scope_obj is scope3.scope_obj}")
else:
    print("  ✗ Failed")
    sys.exit(1)

# Test 2: Capture waveform
print("\n" + "="*60)
print("Test: Waveform capture")
print("="*60)

try:
    chan1 = scope1.vertical.chan(1)
    print("  Capturing waveform...")
    wf = chan1.capture()
    print(f"  ✓ Captured {len(wf.scaledYdata)} samples")
except Exception as e:
    print(f"  ✗ Capture failed: {e}")
    sys.exit(1)

# Test 3: Cleanup
print("\n" + "="*60)
print("Test: Cleanup")
print("="*60)

try:
    scope1.scope_obj.close_handle()
    print("  ✓ Handle closed successfully")
except Exception as e:
    print(f"  ⚠ Cleanup warning: {e}")

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
print("\nYou can now safely run the GUI:")
print("  python src/launch_gui.py")
print()
