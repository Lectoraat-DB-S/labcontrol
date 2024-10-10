from enum import Enum


class WVTP(Enum):
    SINE = 1
    SQUARE = 2
    RAMP = 3
    PULSE = 4
    NOISE= 5
    ARB = 6
    DC = 7
    PRBS = 8

class WvPARAM(Enum):
     FRQ = 1
     AMP = 2
     PERI = 3
   


class BANDSTATE(Enum):
    OFF = 0
    ON = 1

class DIFFSTATE(Enum):
    OFF = 0
    ON = 1

class WaveformParam(object):
    def __init__(self):
        self.WVTP   = WVTP.SINE
        self.frequency = 1000               #not with NOISE or DC
        self.peri      = 1/self.frequency   #not with NOISE or DC
        self.amp    = 4                     #not with NOISE or DC
        self.offset = 0                     #not with NOISE or DC
        self.sym    = 0                     #only with RAMP
        self.pulWidth = 1e-3
        self.duty     = 0                   #only with SQUARE OR PULSE
        self.phase  = 0                     #not with NOISE, PULSE or DC
        self.rise   = 0
        self.fall   = 0
        self.mean   = 0                     #only with NOISE
        self.stdev  = 0
        self.HLEV   = 0
        self.LLEV   = 0
        self.DLY    = 0
        self.bstate = BANDSTATE.OFF         #only with NOISE
        self.bwidth = 0                     #only with NOISE
        self.length = 0                     #only with PRBS   
        self.edge   = 0                     #only with PRBS
        self.diffs  = DIFFSTATE.OFF                     #only with PRBS. PRBS differential mode ON/OFF
        self.prbsbr = 0                     #only with PRBS. PRBS bit rate.
                
    def toString(self):
        returnstr = f"Waveform type: {self.WVTP.name}"
        if (self.WVTP.name != WVTP.DC.name) and (self.WVTP.name != WVTP.NOISE.name): 
            returnstr += f"Waveform frequency: {self.frequency}\n"
            returnstr += f"Waveform period: {self.peri}\n"
            returnstr += f"Waveform amplitude: {self.amp}\n"
            returnstr += f"Waveform offset: {self.offset}\n"
            returnstr += f"Waveform high level: {self.HLEV}\n"
            returnstr += f"Waveform low level: {self.LLEV}\n"
        if (self.WVTP.name == WVTP.RAMP.name):
            returnstr += f"Waveform symmetry: {self.sym}\n"
        if (self.WVTP.name == WVTP.SQUARE.name) or (self.WVTP.name == WVTP.PULSE.name): 
            returnstr += f"Waveform duty: {self.duty}\n"
        if (self.WVTP.name != WVTP.DC.name) and (self.WVTP.name != WVTP.NOISE.name) and (self.WVTP.name != WVTP.PULSE.name): 
            returnstr += f"Waveform phase: {self.phase}\n"
        if (self.WVTP.name == WVTP.NOISE.name):
            returnstr += f"Waveform MEAN: {self.mean}\n"     
            returnstr += f"Waveform stdev: {self.stdev}\n"
            returnstr += f"Waveform bandstatus: {self.bstate.name}\n"
            returnstr += f"Waveform Noise bandwith: {self.bwidth}\n"
        if (self.WVTP.name == WVTP.PULSE.name):
            returnstr += f"Waveform WIDTH: {self.pulWidth}\n"
            returnstr += f"Waveform rise time: {self.rise}\n"
            returnstr += f"Waveform fall time: {self.fall}\n"
            returnstr += f"Waveform delay: {self.DLY}\n"
        if (self.WVTP.name == WVTP.PRBS.name):
            returnstr += f"Waveform PBRS length: {self.length}\n"
            returnstr += f"Waveform PBRS rise/fall time: {self.edge}\n"
            returnstr += f"Waveform PBRS differential state: {self.diffs.name}\n"
        return returnstr
    
    def decodeWaveformParamQuery(self, resp:str):
        # example response C1:BSWV WVTP,RAMP,FRQ,500HZ,PERI,0.00200000016S,AMP,5V,OFST,2.5V,HLEV,5V,LLEV,0V,PHSE,0,SYM,50
        # another C1:BSWV WVTP,PULSE,FRQ,500HZ,PERI,0.00200000016S,AMP,5V,OFST,2.5V,HLEV,5V,LLEV,0V,DUTY,67,WIDTH,0.00134,DLY,0
        # remark examples: if FRQ = 500Hz then PERI = 0.002s and not PERI,0.00200000016S
        head = resp.split(" ")
        pattern = "BSWV"
        if pattern not in head[0]:
            return None #error
        else:
            paramstr = head[1]
            params = paramstr.split(",")
            maxindex = len(params)
            index = 0 
            while index < maxindex:
                param = params[index]
                value = params[index+1]
                match param:
                    case "WVTP":
                        #this normally goes perfectly.
                        self.WVTP = WVTP[value]
                    case "FRQ":
                        value = float(value.strip("HZ"))
                        self.frequency = value
                        pass
                    case "PERI":
                        value = float(value.strip("S"))
                        self.peri = value
                    case "AMP":
                        value = float(value.strip("V"))
                        self.amp = value
                    case "OFST":
                        value = float(value.strip("V"))
                        self.offset = value
                    case "HLEV":
                        value = float(value.strip("V"))
                        self.HLEV
                    case "LLEV":
                        value = float(value.strip("V"))
                        self.LLEV
                    case "DUTY":
                        value = float(value)
                        self.duty = value
                    case "WIDTH":
                        value = float(value)
                        self.pulWidth = value
                    case "DLY":
                        value = float(value)
                        self.DLY = value
                        pass
                index += 2
            return self            
                        

# Programming guide Siglent analyse:
# System commands: output, etc
# Wave commands: basic, modulation, sweep, burst, arbitrary 
class SDGCommand(object):
    FREQUENCY = "FRQ"
    AMPLITUDE = "AMP"
    SINE = "SINE"
    OFFSET = "OFST"

       
    def setWaveCommand(channel, parameter, value):
        basicWaveCommandstr = f"{channel}:BSWV {parameter},{value}"
        return basicWaveCommandstr
    
    def enableSweep(channel):
        cmdStr = f"{channel}:SWWV STATE,ON"
        return cmdStr
    
    def disableSweep(channel):
        cmdStr = f"{channel}:SWWV STATE,OFF"
        return cmdStr
    
    def setSweep(channel, time,startfreq, stopfreq):
        cmdStr = f"{channel}:SWWV STATE,ON,TIME,{time},STOP,{stopfreq},START,{startfreq}"
        return cmdStr
    
    def setWaveType(channel, waveType: WVTP):
        cmdStr = ""
        if waveType in WVTP.__members__:
            cmdStr = SDGCommand.setWaveCommand(channel, "WVTP", waveType)
        else:
            cmdStr = None
        return cmdStr    
    
    def setPulseWave(channel, period, pulseWidth, rise, fall, delay=0):
        cmdStr = f"{channel}:BSWV WVTP,{WVTP.PULSE.name},PERI,{period},WIDTH,{pulseWidth},RISE,{rise},FALL,{fall},DLY,{delay}"
        return cmdStr
    
    def setSine(channel):
        cmdStr = SDGCommand.setWaveType(channel, WVTP.SINE.name)
        return cmdStr
    
    def setOutput(channel, oState: bool):
        if oState:
            outStr = "ON"
        else:
            outStr = "OFF"
        cmdStr = f"{channel}:OUTPut {outStr}"
        return cmdStr
    
    def setWaveParam(channel, param:WaveformParam)->list:
        commandList = list() 
        if (param.WVTP.name != WVTP.DC.name) and (param.WVTP.name != WVTP.NOISE.name): 
            commandList.append(SDGCommand.setWaveCommand(channel,SDGCommand.FREQUENCY,param.frequency))
            commandList.append(SDGCommand.setWaveCommand(channel,SDGCommand.AMPLITUDE,param.amp))
            #commandList.append(SDGCommand.setWaveCommand(channel,,param.amp))
            returnstr += f"Waveform period: {self.peri}"
            returnstr += f"Waveform offset: {self.offset}"
            returnstr += f"Waveform high level: {self.HLEV}"
            returnstr += f"Waveform low level: {self.LLEV}"
        if (self.WVTP.name == WVTP.RAMP.name):
            returnstr += f"Waveform symmetry: {self.sym}"
        if (self.WVTP.name == WVTP.SQUARE.name) or (self.WVTP.name == WVTP.PULSE.name): 
            returnstr += f"Waveform duty: {self.duty}"
        if (self.WVTP.name != WVTP.DC.name) and (self.WVTP.name != WVTP.NOISE.name) and (self.WVTP.name != WVTP.PULSE.name): 
            returnstr += f"Waveform phase: {self.phase}"
        if (self.WVTP.name == WVTP.NOISE.name):
            returnstr += f"Waveform MEAN: {self.mean}"     
            returnstr += f"Waveform stdev: {self.stdev}"
            returnstr += f"Waveform bandstatus: {self.bstate.name}"
            returnstr += f"Waveform Noise bandwith: {self.bwidth}"
        if (self.WVTP.name == WVTP.PULSE.name):
            returnstr += f"Waveform WIDTH: {self.pulWidth}"
            returnstr += f"Waveform rise time: {self.rise}"
            returnstr += f"Waveform fall time: {self.fall}"
            returnstr += f"Waveform delay: {self.DLY}"
        if (self.WVTP.name == WVTP.PRBS.name):
            returnstr += f"Waveform PBRS length: {self.length}"
            returnstr += f"Waveform PBRS rise/fall time: {self.edge}"
            returnstr += f"Waveform PBRS differential state: {self.diffs.name}"
        return returnstr
        
    
    def queryWaveParam(channel):
        cmdStr = f"{channel}:BSWV?"
        return cmdStr
    
    def queryModParam(channel):
        cmdStr = f"{channel}:MDWV?"
        return cmdStr
    
    def querySweepParam(channel):
        cmdStr = f"{channel}:SWWV?"
        return cmdStr
    
    def queryBurstParam(channel):
        cmdStr = f"{channel}:BTWV?"
        return cmdStr
