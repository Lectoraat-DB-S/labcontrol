#!/usr/bin/env python3
"""
Test script for Hantek 6022BL integration with BaseScope framework
"""

import time

from devices.BaseScope import BaseScope
from devices.Hantek.HantekBaseScope import HantekScope  # Import to register

print("="*60)
print("Hantek 6022 Integration Test")
print("="*60)

# Test 1: Detection
print("\n[Test 1] Detecting scope...")
scope = BaseScope.getDevice()
if scope is None:
    print("  ✗ FAIL: No scope detected")
    exit(1)
else:
    print(f"  ✓ PASS: Detected {scope.brand} {scope.model}")

# Test 2: Channel access
print("\n[Test 2] Accessing channels...")
chan1 = scope.vertical.chan(1)
chan2 = scope.vertical.chan(2)
if chan1 and chan2:
    print(f"  ✓ PASS: Both channels accessible")
    print(f"    - Channel 1: {chan1.name}")
    print(f"    - Channel 2: {chan2.name}")
else:
    print("  ✗ FAIL: Could not access channels")
    exit(1)

# Test 3: Voltage range settings
print("\n[Test 3] Testing voltage range settings...")
try:
    chan1.setVdiv(5.0)  # Set to 5V range
    vdiv = chan1.getVdiv()
    print(f"  ✓ PASS: V/div = {vdiv} V")
except Exception as e:
    print(f"  ✗ FAIL: {e}")
    exit(1)

# Test 4: Coupling settings
print("\n[Test 4] Testing coupling settings...")
try:
    chan1.setCoupling("DC")
    coupling = chan1.getCoupling()
    print(f"  ✓ PASS: Coupling = {coupling}")
except Exception as e:
    print(f"  ✗ FAIL: {e}")
    exit(1)

# Test 5: Horizontal (timebase) settings
print("\n[Test 5] Testing timebase settings...")
try:
    scope.horizontal.setTimeDiv(0.001)  # 1ms/div
    print(f"  ✓ PASS: Sample rate set")
except Exception as e:
    print(f"  ✗ FAIL: {e}")
    exit(1)

# Test 6: Waveform capture
print("\n[Test 6] Capturing waveform...")
print("  NOTE: Make sure channel 1 has a signal connected!")
print("  Capturing... (this may take a few seconds)")
try:
    wf = chan1.capture()
    if wf and len(wf.scaledYdata) > 0:
        print(f"  ✓ PASS: Captured {len(wf.scaledYdata)} samples")
        print(f"    - Time range: {min(wf.scaledXdata):.6f} to {max(wf.scaledXdata):.6f} s")
        print(f"    - Voltage range: {min(wf.scaledYdata):.3f} to {max(wf.scaledYdata):.3f} V")
    else:
        print("  ✗ FAIL: No waveform data")
        exit(1)
except Exception as e:
    print(f"  ✗ FAIL: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 7: Measurements
print("\n[Test 7] Testing measurements...")
try:
    mean = chan1.getMean()
    vmin = chan1.getMin()
    vmax = chan1.getMax()
    pkpk = chan1.getPkPk()

    print(f"  ✓ PASS: Measurements completed")
    print(f"    - Mean:     {mean:.3f} V")
    print(f"    - Min:      {vmin:.3f} V")
    print(f"    - Max:      {vmax:.3f} V")
    print(f"    - Peak-Peak: {pkpk:.3f} V")
except Exception as e:
    print(f"  ✗ FAIL: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("ALL TESTS PASSED! ✓")
print("Hantek 6022 is fully integrated and ready to use!")
print("="*60)
