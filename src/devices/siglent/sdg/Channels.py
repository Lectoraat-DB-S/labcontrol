import time
import vxi11
import struct
import numpy as np
from enum import Enum
import socket
import pyvisa as visa
import logging
import time
import xdrlib
from devices.siglent.sdg.Commands import WaveForm
from devices.siglent.sdg.Commands import BasicWaveCommandTypes
from devices.siglent.sdg.Commands import WaVeformTyPe
# SDGChannel: abstraction of a Siglent function generator channel.

class SDGChannel(object):
    C1 = "C1"
    C2 = "C2"

    def __init__(self, chan_no: int, dev):
        self._name = f"C{chan_no}"
        self._dev = dev
        self._waveForm = WaveForm()

    def setBasicWaveFormFreq(self, freq):
        line1 = f"{self._name}:BSWV FRQ,{freq}"
        #print(line1)
        self._dev.write(line1)
    #short name for above mentioned
    def setFreq(self, freq=1000):
        self.setBasicWaveFormFreq(freq)

    def setAmp(self, amp):
        line1 = f"{self._name}:BSWV AMP,{amp}"
        self._dev.write(line1)

    def setBasicSweepWave(self, startfreq, stopfreq):
        line1 = f"{self._name}:SWWV STATE,ON"
        self._dev.write(line1)
        line1 = f"{self._name}:SWWV STOP,{stopfreq}"
        self._dev.write(line1)
            
    def setBasicWaveFormType(self, val: WaVeformTyPe):
        # check if WaveParam is correct.
        self._waveForm.setWVTP(val)
        line1 = f"{self._name}:BSWV WVTP,{self._waveForm.wavetype.name}"
        print(line1)
        self._dev.write(line1)

    #short version call
    def setType(self, type):
        match type:
            case "RAMP":
                self.setBasicWaveFormType(WaVeformTyPe.RAMP)
            case "SIN":
                self.setBasicWaveFormType(WaVeformTyPe.SINE)
            case _:
                self.setBasicWaveFormType(WaVeformTyPe.SINE)
    def setOutputOn(self,val: bool):
        if val:
            self._dev.write(f"{self._name}:OUTPut ON")
        else:
            self._dev.write(f"{self._name}:OUTPut OFF")
    def setSweep(self, enable: bool, start=1, stop=10, sweepTime=1):
        if enable:
            self._dev.write(f"{self._name}:SWWV STATE,ON,START,{start},STOP,{stop},TIME,{sweepTime}")
        else:
            self._dev.write(f"{self._name}:SWWV STATE OFF")