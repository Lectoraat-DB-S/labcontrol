
import pyvisa as visa
import logging
import time
from devices.siglent.sdg.Commands import WaveformParam
from devices.siglent.sdg.Commands import WVTP
from devices.siglent.sdg.Commands import SDGCommand
from devices.BaseGenerator import BaseGenChannel


# SDGChannel: abstraction of a Siglent function generator channel.

class SDGChannel(BaseGenChannel):
    C1 = "C1"
    C2 = "C2"

    @classmethod
    def getGenChannelClass(cls,  chan_no, dev):
        if cls is SDGChannel:
            return cls
        else:
            return None     

    def __init__(self, chan_no: int, dev):
        super().__init__(chan_no, instr=dev)
        self.name = f"C{chan_no}"
        self.visaInstr = dev
        self.WVP = WaveformParam()
        
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
        self.visaInstr.write(SDGCommand.setWaveCommand(self.name,SDGCommand.FREQUENCY,freq))

    def setAmp(self, amp):
        self.visaInstr.write(SDGCommand.setWaveCommand(self.name,SDGCommand.AMPLITUDE,amp))
    
    def setOffset(self, offset):
        self.visaInstr.write(SDGCommand.setWaveCommand(self.name,SDGCommand.OFFSET,offset))

    def setSineWave(self,freq=None, amp=None):
        self.visaInstr.write(SDGCommand.setSine(self.name))
        if freq != None:
            self.visaInstr.write(SDGCommand.setWaveCommand(self.name, SDGCommand.FREQUENCY, freq))
        if amp != None:
            self.visaInstr.write(SDGCommand.setWaveCommand(self.name, SDGCommand.AMPLITUDE, amp))
            
    def setPulseWave(self, period, pulseWidth, rise, fall, delay=0):
        #setting the waveform interrupts the signal generation of de SDG, therefore setting the waweform to PULSE only needed
        #when current waveform is not PULSE. If PULSE then set ONLY the parameters, to prevent signal degradation.
        if self.WVTP != WVTP.PULSE: 
            self.visaInstr.write(SDGCommand.setPulseWave(self.name,period,pulseWidth,rise,fall,delay))
            self.WVTP   = WVTP.PULSE
            self.WVP.pulWidth = pulseWidth
            self.WVP.rise = rise
            self.WVP.fall = fall
            self.WVP.delay = delay
        else:
            self.visaInstr.write(SDGCommand.setWaveCommand(self.name, SDGCommand.PERIOD, period))
            self.visaInstr.write(SDGCommand.setWaveCommand(self.name, SDGCommand.PULSEWDITH, pulseWidth))
            self.visaInstr.write(SDGCommand.setWaveCommand(self.name, SDGCommand.RISETIME, rise))
            self.visaInstr.write(SDGCommand.setWaveCommand(self.name, SDGCommand.FALLTIME, fall))
        
    def setPulseWidth(self, pulseWidth):
        if self.WVTP == WVTP.PULSE:
            self.visaInstr.write(SDGCommand.setWaveCommand(self.name, SDGCommand.PULSEWDITH, pulseWidth))
        
    def enableSweep(self, val: bool):
        if val:
            self.visaInstr.write(SDGCommand.enableSweep(self.name))
        else:
            self.visaInstr.write(SDGCommand.disableSweep(self.name))
    
    def setSweep(self, time, start, stop):  
        self.visaInstr.write(SDGCommand.setSweep(self.name,time,start,stop))
    
    #short version call
    def setWaveType(self, type: WVTP):
        self.visaInstr.write(SDGCommand.setWaveType(self.name, type))

    def enableOutput(self,val: bool):
        self.visaInstr.write(SDGCommand.setOutput(self.name, val))

            
    ######### GET FUNCTIONS ########
    
    def getWaveParam(self) -> WaveformParam:
        resp = self.visaInstr.query(SDGCommand.queryWaveParam(self.name))
        param = self.WVP.decodeWaveformParamQuery(resp)
        return param
    
    def getModulationParam(self):
        return self.visaInstr.query(SDGCommand.queryModParam(self.name))
        
    def getSweepParam(self):
        return self.visaInstr.query(SDGCommand.querySweepParam(self.name))
    
    def getBurstParam(self):
        return self.visaInstr.query(SDGCommand.queryBurstParam(self.name))
    
    