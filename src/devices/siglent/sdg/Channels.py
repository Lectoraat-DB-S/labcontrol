
import pyvisa as visa
import logging
import time
from devices.siglent.sdg.Commands import WaveformParam
from devices.siglent.sdg.Commands import WVTP
from devices.siglent.sdg.Commands import SDGCommand


# SDGChannel: abstraction of a Siglent function generator channel.

class SDGChannel(object):
    C1 = "C1"
    C2 = "C2"

    def __init__(self, chan_no: int, dev):
        self._name = f"C{chan_no}"
        self._dev = dev
        self._WVP = WaveformParam()
        
    # __enter__ method
    # precondition: Generator just started or after waveparam set
    # purpose: when object will be used (for the first time), this method queries for all basic WaveFormParam, for consistency
    # Reason: waveparam aren't consistent, e.g. f=500Hz => T=2.0000006 ms? Maybe an artefact of Python or bug (feature) in a VISA 
    # driver?
    # postcondition: WaveformParam object reflect actual state of generator.
    # 
    def __enter__(self):
        self.getBasicWaveParam()

    def setfreq(self, freq):
        self._dev.write(SDGCommand.setWaveCommand(self._name,SDGCommand.FREQUENCY,freq))

    def setAmp(self, amp):
        self._dev.write(SDGCommand.setWaveCommand(self._name,SDGCommand.AMPLITUDE,amp))
    
    def setOffset(self, offset):
        self._dev.write(SDGCommand.setWaveCommand(self._name,SDGCommand.OFFSET,offset))

    def setSineWave(self,freq=None, amp=None):
        self._dev.write(SDGCommand.setSine(self._name))
        if freq != None:
            self._dev.write(SDGCommand.setWaveCommand(self._name, SDGCommand.FREQUENCY, freq))
        if amp != None:
            self._dev.write(SDGCommand.setWaveCommand(self._name, SDGCommand.AMPLITUDE, amp))
            
    def setPulseWave(self, period, pulseWidth, rise, fall, delay=0):
        #setting the waveform interrupts the signal generation of de SDG, therefore setting the waweform to PULSE only needed
        #when current waveform is not PULSE. If PULSE then set ONLY the parameters, to prevent signal degradation.
        if self.WVTP != WVTP.PULSE: 
            self._dev.write(SDGCommand.setPulseWave(self._name,period,pulseWidth,rise,fall,delay))
            self.WVTP   = WVTP.PULSE
            self._WVP.pulWidth = pulseWidth
            self._WVP.rise = rise
            self._WVP.fall = fall
            self._WVP.delay = delay
        else:
            self._dev.write(SDGCommand.setWaveCommand(self._name, SDGCommand.PERIOD, period))
            self._dev.write(SDGCommand.setWaveCommand(self._name, SDGCommand.PULSEWDITH, pulseWidth))
            self._dev.write(SDGCommand.setWaveCommand(self._name, SDGCommand.RISETIME, rise))
            self._dev.write(SDGCommand.setWaveCommand(self._name, SDGCommand.FALLTIME, fall))
        
    def setPulseWidth(self, pulseWidth):
        if self.WVTP == WVTP.PULSE:
            self._dev.write(SDGCommand.setWaveCommand(self._name, SDGCommand.PULSEWDITH, pulseWidth))
        
    def enableSweep(self, val: bool):
        if val:
            self._dev.write(SDGCommand.enableSweep(self._name))
        else:
            self._dev.write(SDGCommand.disableSweep(self._name))
    
    def setSweep(self, time, start, stop):  
        self._dev.write(SDGCommand.setSweep(self._name,time,start,stop))
    
    #short version call
    def setWaveType(self, type: WVTP):
        self._dev.write(SDGCommand.setWaveType(self._name, type))

    def enableOutput(self,val: bool):
        self._dev.write(SDGCommand.setOutput(self._name, val))

            
    ######### GET FUNCTIONS ########
    
    def getWaveParam(self) -> WaveformParam:
        resp = self._dev.query(SDGCommand.queryWaveParam(self._name))
        param = self._WVP.decodeWaveformParamQuery(resp)
        return param
    
    def getModulationParam(self):
        return self._dev.query(SDGCommand.queryModParam(self._name))
        
    def getSweepParam(self):
        return self._dev.query(SDGCommand.querySweepParam(self._name))
    
    def getBurstParam(self):
        return self._dev.query(SDGCommand.queryBurstParam(self._name))
    
    