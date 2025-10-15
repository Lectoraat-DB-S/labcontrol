#!/usr/bin/env python 3.10.1
# -*- coding: utf-8 -*-

"""
 * Example script to retrieve waveform from SIGLENT SDS oscilloscopes
 *
 * Copyright (C) 2022 Sebastian (AI5GW) <sebastian@baltic-lab.com>
 * Web (EN): https://baltic-lab.com
 * Web (DE): https://baltic-labor.de/
 * YouTube (EN): https://www.youtube.com/c/BalticLab
 *
"""

import sys
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plotter

try:
    rm = visa.ResourceManager()
    print(rm.list_resources())

    # Connect to device (Make sure to change the resource locator!)
    device = rm.open_resource('TCPIP::192.168.0.105::INSTR',query_delay=0.25)
except:
    print('Failed to connect to device...')
    sys.exit(0)
device.timeout = 30000
#device.chunk_size = 20480000
device.chunk_size = 102400
CHAN = 1

VDIV= device.query('C1:VDIV?')
print("VDIV =", VDIV)
VOFS= device.query('C1:OFST?')
CENTERTV = device.query('TRDL?')
TB=device.query('TDIV?')
print("VOFS =", VOFS)
print("CENTERTV =", CENTERTV)
print("TB =", TB)


SAMPLE_RATE = device.query('SARA?')
SAMPLE_RATE = SAMPLE_RATE[len('SARA '):-5]
SAMPLE_RATE = float(SAMPLE_RATE)

device.write('WFSU SP,4,NP,0,FP,0')
device.write('WFSU SP,1,NP,0,FP,0')

#device.write('C1:WF? DAT2')
#device.chunk_size = 1024*1024*1024

#datapoints = device.query_ascii_values('CURV?')
datapoints = device.query_binary_values('C1:WF? DAT2', datatype='d', is_big_endian=False)
#datapoints = device.query_binary_values('C1:WF? DAT2')
#print(datapoints)
print(f"aantal datapoints = {len(datapoints)}")
#X_AX = time = np.arange(0, len(WAVEFORM), 1);
#device.write('CURV?')
#datapoints = device.read_raw()
plotter.plot(datapoints)
plotter.title('Waveformfrom  from SDG')
plotter.grid('True')
plotter.show()
