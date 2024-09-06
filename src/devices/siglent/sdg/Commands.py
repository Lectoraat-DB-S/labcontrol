import time
import vxi11
import struct
import numpy as np
from enum import Enum, auto, StrEnum
import socket
import pyvisa as visa
import logging
import time
import xdrlib

class BasicWaveCommandTypes(Enum):
    WVTP = 1
    FRQ = 2
    PERI = 3
    AMP = 4
    OFST = 5
    SYM = 6
    DUTY = 7
    PHSE = 8
    STDEV = 9
    MEAN = 10
    WIDTH = 11
    RISE = 12
    FALL = 13
    DLY = 14
    HLEV = 15
    LLEV = 16
    BANDSTATE = 17
    BANDWIDTH = 18
    LENGTH= 19
    EDGE= 20
    DIFFSTATE= 21
    BITRATE= 22

class WaVeformTyPe(Enum):
    SINE = 1
    SQUARE = 2
    RAMP = 3
    PULSE = 4
    NOISE= 5
    ARB = 6
    DC = 7
    PRBS = 8

class WaveForm(object):
    def __init__(self):
        self.cmdType = BasicWaveCommandTypes.WVTP
        self.wavetype = WaVeformTyPe.SINE
        self.freq = 1
        self.peri = 1/self.freq
        self.amp = 1
        self.ofst = 0

    def setWVTP(self, val: WaVeformTyPe):
        self.cmdType = BasicWaveCommandTypes.WVTP
        if val in WaVeformTyPe:
            self.wavetype = val
            return val
        else:
            #TODO: decide what to do. Is this an error? For now do nothing.
            return None

    def set(self, cmd: BasicWaveCommandTypes, val):
        if cmd == BasicWaveCommandTypes.WVTP:
            if val in WaVeformTyPe:
                self.wavetype = val
                return val
            else:
                #TODO: decide what to do. Is this an error? For now do nothing.
                return None
        else:
            if cmd == BasicWaveCommandTypes.FRQ:
                if self.wavetype != WaVeformTyPe.NOISE or self.wavetype != WaVeformTyPe.DC:
                    self.freq = val
            if cmd == BasicWaveCommandTypes.AMP:
                if self.wavetype != WaVeformTyPe.NOISE or self.wavetype != WaVeformTyPe.DC:
                    self.amp = val


class SYM(object):
        """
        :={0 to 100}. Symmetry of RAMP. The unit is "%". Only settable when WVTP is RAMP.
        """
        def __init__(self):
            self._valid_range = range(0,101)

class DUTY(object):
    """
    := {0 to 100}. Duty cycle. The unit is "%". Value depends on frequency. Only settable when WVTP is SQUARE or PULSE.
    """

    def __init__(self):
        self._valid_range = range(0, 101)

class PHSE(object):
    """
    := {0 to 360}. The unit is "degree". Not valid when WVTP is NOISE, PULSE or DC.
    """

    def __init__(self):
        self._valid_range = range(0, 361)

class RISE_TIME(object):
    """
    := rise time (10%~90%). The unit is seconds "s". Refer
    to the data sheet for the range of valid values. Only settable when WVTP is PULSE.
    """

    def __init__(self):
        self._valid_range = range(10, 91)

class WaveformParam(object):
    def __init__(self):
        self.WVTP   = WaVeformTyPe.SINE
        self.frequency = 1000               #not with NOISE or DC
        self.peri      = 1/self.frequency   #not with NOISE or DC
        self.amp    = 4                     #not with NOISE or DC
        self.offset = 0                     #not with NOISE or DC
        self.sym    = 0                     #only with RAMP
        self.pulWidth = 1e-3
        #self.duty     = berekening         #only with SQUARE OR PULSE
        self.phase  = 0                     #not with NOISE, PULSE or DC
        self.rise   = 0
        self.fall   = 0
        self.mean   = 0                     #only with NOISE
        self.stdev  = 0
        
    def keepConsistent(self):
        pass
    
    def decodeWaveformParam(self, resp:str):
        pass
        # example response C1:BSWV WVTP,RAMP,FRQ,500HZ,PERI,0.00200000016S,AMP,5V,OFST,2.5V,HLEV,5V,LLEV,0V,PHSE,0,SYM,50
        # another C1:BSWV WVTP,PULSE,FRQ,500HZ,PERI,0.00200000016S,AMP,5V,OFST,2.5V,HLEV,5V,LLEV,0V,DUTY,67,WIDTH,0.00134,DLY,0
        # remark examples: if FRQ = 500Hz then PERI = 0.002s and not PERI,0.00200000016S
        head = resp.split(" ")
        head = head.split(":")
        resp_list = resp.split(",")
        for param in resp_list:
            pass
        
    def toSCPI(self):
        cmds = list()
        cmds.append(f"FRQ,{self.frequency}")
        cmds.append(f"AMP,{self.amp}")
        cmds.append(f"OFST,{self.offset}")
        cmds.append(f"WIDTH,{self.pulWidth}")
        #line =f"FREQ,{self.frequency}Hz,AMP,{self.amp}V,OFST,{self.offset}V,WIDTH,{self.pulWidth}s"
        return cmds
        