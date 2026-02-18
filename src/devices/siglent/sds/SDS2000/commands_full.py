"""
siglent_sds_scpi_full.py

Auto-generated SCPI mapping for Siglent SDS Series (EN11D Programming Guide).
Source: SDS-Series_ProgrammingGuide_EN11D.pdf (user-upload). See file citations in chat.
"""

from typing import Any

def qstr(s: str) -> str:
    """Return a quoted SCPI string (double quotes)."""
    return f'"{s}"'

# convenience channel formatting
def ch(n: int) -> str:
    return f"CHANnel{n}"

#
# CHANNEL subsystem - extensive
#
CHANNEL = {
    # reference strategy
    "reference":        lambda val:       f":CHANnel:REFerence {val}",
    "reference?":       lambda:           ":CHANnel:REFerence?",
    # per-channel commands (use ch(n) or integer)
    "scale":            lambda n, v:      f":CHANnel{n}:SCALe {v}",
    "scale?":           lambda n:         f":CHANnel{n}:SCALe?",
    "offset":           lambda n, v:      f":CHANnel{n}:OFFSet {v}",
    "offset?":          lambda n:         f":CHANnel{n}:OFFSet?",
    "probe":            lambda n, mode, value=None: f":CHANnel{n}:PROBe {mode}" + (f",{value}" if value is not None else ""),
    "probe?":           lambda n:         f":CHANnel{n}:PROBe?",
    "coupling":         lambda n, mode:   f":CHANnel{n}:COUPling {mode}",
    "coupling?":        lambda n:         f":CHANnel{n}:COUPling?",
    "bwlimit":          lambda n, v:      f":CHANnel{n}:BWLimit {v}",
    "bwlimit?":         lambda n:         f":CHANnel{n}:BWLimit?",
    "impedance":        lambda n, v:      f":CHANnel{n}:IMPedance {v}",
    "impedance?":       lambda n:         f":CHANnel{n}:IMPedance?",
    "invert":           lambda n, s:      f":CHANnel{n}:INVert {s}",
    "invert?":          lambda n:         f":CHANnel{n}:INVert?",
    "label":            lambda n, s:      f":CHANnel{n}:LABel {s}",
    "label?":           lambda n:         f":CHANnel{n}:LABel?",
    "label_text":       lambda n, text:   f":CHANnel{n}:LABel:TEXT {qstr(text)}",
    "label_text?":      lambda n:         f":CHANnel{n}:LABel:TEXT?",
    "skew":             lambda n, v:      f":CHANnel{n}:SKEW {v}",
    "skew?":            lambda n:         f":CHANnel{n}:SKEW?",
    "unit":             lambda n, u:      f":CHANnel{n}:UNIT {u}",
    "unit?":            lambda n:         f":CHANnel{n}:UNIT?",
    "switch":           lambda n, s:      f":CHANnel{n}:SWITch {s}",
    "switch?":          lambda n:         f":CHANnel{n}:SWITch?",
    "visible":          lambda n, s:      f":CHANnel{n}:VISible {s}",
    "visible?":         lambda n:         f":CHANnel{n}:VISible?",
    # additional aliases for short form (manual supports CHAN1:SCAL etc.)
    "scale_short":      lambda n, v:      f":CHAN{n}:SCALe {v}",
    "scale_short?":     lambda n:         f":CHAN{n}:SCALe?",
}

#
# ACQUIRE subsystem
#
ACQUIRE = {
    "amode":            lambda v:         f":ACQuire:AMODe {v}",
    "amode?":           lambda:            ":ACQuire:AMODe?",
    "csweep":           lambda:            ":ACQuire:CSWeep",
    "interpolation":    lambda v:         f":ACQuire:INTerpolation {v}",
    "interpolation?":   lambda:            ":ACQuire:INTerpolation?",
    "mmanagement":      lambda v:         f":ACQuire:MMANagement {v}",
    "mmanagement?":     lambda:            ":ACQuire:MMANagement?",
    "mode":             lambda v:         f":ACQuire:MODE {v}",
    "mode?":            lambda:            ":ACQuire:MODE?",
    "mdepth":           lambda v:         f":ACQuire:MDEPth {v}",
    "mdepth?":          lambda:            ":ACQuire:MDEPth?",
    "numacq?":          lambda:            ":ACQuire:NUMAcq?",
    "points?":          lambda:            ":ACQuire:POINts?",
    "resolution":       lambda v:         f":ACQuire:RESolution {v}",
    "resolution?":      lambda:            ":ACQuire:RESolution?",
    "sequence":         lambda s:         f":ACQuire:SEQuence {s}",
    "sequence?":        lambda:            ":ACQuire:SEQuence?",
    "sequence_count":   lambda v:         f":ACQuire:SEQuence:COUNt {v}",
    "sequence_count?":  lambda:            ":ACQuire:SEQuence:COUNt?",
    "srate":            lambda v:         f":ACQuire:SRATe {v}",
    "srate?":           lambda:            ":ACQuire:SRATe?",
    "type_1":           lambda v:         f":ACQuire:TYPE {v}",
    "type_2":           lambda v1, v2:    f":ACQuire:TYPE {v1},{v2}",
    "type?":            lambda:            ":ACQuire:TYPE?",
    "points_to":        lambda v:         f":ACQuire:POINts {v}",  # some models accept set points
}

#
# TRIGGER subsystem (large, includes EDGE, FREQuency, BUS-specific)
#
#EDGE trigger subsubsystem
EDGE = {
    "level":        lambda val:     f":TRIGger:EDGE:LEVel {val}",
    "level?":       lambda :        ":TRIGger:EDGE:LEVel?",
    "coupling":     lambda c:       f":TRIGger:EDGE:COUPling {c}",
    "coupling?":    lambda:         ":TRIGger:EDGE:COUPling?",
    "events":       lambda t:       f":TRIGger:EDGE:HLDEVent {t}",
    "events?":      lambda:         ":TRIGger:EDGE:HLDEVent?",
    
    "hldtime":      lambda t:       f":TRIGger:EDGE:HLDTime {t}",
    "hldtime?":     lambda:         ":TRIGger:EDGE:HLDTime?",

    "hldtype":      lambda t:       f":TRIGger:EDGE:HOLDoff {t}",
    "hldtype?":     lambda:         ":TRIGger:EDGE:HOLDoff?",
    
    "hldstart":     lambda t:       f":TRIGger:EDGE:HSTart {t}",
    "hldstart?":    lambda:         ":TRIGger:EDGE:HSTart?",
    
    "impedance":    lambda imp:     f":TRIGger:EDGE:IMPedance {imp}",
    "impedance?":   lambda:         ":TRIGger:EDGE:IMPedance?",
    
    "noise":        lambda state:   f":TRIGger:EDGE:NREJect {state}",
    "noise?":       lambda:         ":TRIGger:EDGE:NREJect?",
    
    "source":       lambda s:       f":TRIGger:EDGE:SOURce {s}",
    "source?":      lambda:         ":TRIGger:EDGE:SOURce?",
    "slope":        lambda s:       f":TRIGger:EDGE:SLOPe {s}",
    "slope?":       lambda:         ":TRIGger:EDGE:SLOPe?",
}

#SLOPE trigger subsubsystem
SLOPE = {    
    "coupling":     lambda v:           f":TRIGger:SLOPe:COUPling {v}",
    "coupling?":    lambda:             ":TRIGger:SLOPe:COUPling?",
    "event":        lambda val:         f":TRIGger:SLOPe:HLDEVent {val}",
    "event?":       lambda :             ":TRIGger:SLOPe:HLDEVent?",
    "time":         lambda c:           f":TRIGger:SLOPe:HLDTime {c}",
    "time?":        lambda:             ":TRIGger:SLOPe:HLDTime?",   
    "level":        lambda t:           f":TRIGger:SLOPe:HLEVel {t}",
    "level?":       lambda:             ":TRIGger:SLOPe:HLEVel?",
    "holdoff":      lambda t:           f":TRIGger:SLOPe:HOLDoff {t}",
    "holdoff?":     lambda:             ":TRIGger:SLOPe:HOLDoff?",
    "start":        lambda t:           f":TRIGger:SLOPe:HSTart {t}",
    "start?":       lambda:             ":TRIGger:SLOPe:HSTart?",
    "LIMit":        lambda t:           f":TRIGger:SLOPe:LIMit {t}",
    "LIMit?":       lambda:             ":TRIGger:SLOPe:LIMit?",
    "llevel":       lambda imp:         f":TRIGger:SLOPe:LLEVel {imp}",
    "llevel?":      lambda:             ":TRIGger:SLOPe:LLEVel?",
    "noise":        lambda state:       f":TRIGger:SLOPe:NREJect {state}",
    "noise?":       lambda:            ":TRIGger:SLOPe:NREJect?",
    
    "source":       lambda s:           f":TRIGger:SLOPe:SOURce {s}",
    "source?":      lambda:             ":TRIGger:SLOPe:SOURce?",
    "slope":        lambda s:           f":TRIGger:SLOPe:SLOPe {s}",
    "slope?":       lambda:             ":TRIGger:SLOPe:SLOPe?",
    
    "tlower":       lambda s:           f":TRIGger:SLOPe:TLOWer {s}",
    "tlower?":      lambda:             ":TRIGger:SLOPe:TLOWer?",
    
    "tupper":       lambda s:           f"TRIGger:SLOPe:TUPPer {s}",
    "tupper?":      lambda:              "TRIGger:SLOPe:TUPPer?",
    }

#PULSe trigger subsubsystem command set
PULSE = {    
    "coupling":     lambda v:           f":TRIGger:PULSe:COUPling {v}",
    "coupling?":    lambda:             ":TRIGger:PULSe:COUPling?",
    "event":        lambda val:         f":TRIGger:PULSe:HLDEVent {val}",
    "event?":       lambda :             ":TRIGger:PULSe:HLDEVent?",
    "time":         lambda c:           f":TRIGger:PULSe:HLDTime {c}",
    "time?":        lambda:             ":TRIGger:PULSe:HLDTime?",   
    "start":        lambda t:           f":TRIGger:PULSe:HSTart {t}",
    "start?":       lambda:             ":TRIGger:PULSe:HSTart?",
    "holdoff":      lambda t:           f":TRIGger:PULSe:HOLDoff {t}",
    "holdoff?":     lambda:             ":TRIGger:PULSe:HOLDoff?",
    "level":        lambda t:           f":TRIGger:PULSe:LEVel {t}",
    "level?":       lambda:             ":TRIGger:PULSe:LEVel?",
    "limit":        lambda t:           f":TRIGger:PULSe:LIMit {t}",
    "limit?":       lambda:             ":TRIGger:PULSe:LIMit?",
    "noise":        lambda state:       f":TRIGger:PULSe:NREJect {state}",
    "noise?":       lambda:             ":TRIGger:PULSe:NREJect?",
    "polarity":     lambda s:           f":TRIGger:PULSe:POLarity {s}",
    "polarity?":    lambda:             ":TRIGger:PULSe:POLarity?",
    
    "source":       lambda s:           f":TRIGger:PULSe:SOURce {s}",
    "source?":      lambda:             ":TRIGger:PULSe:SOURce?",
    "tlower":       lambda s:           f":TRIGger:PULSe:TLOWer {s}",
    "tlower?":      lambda:             ":TRIGger:PULSe:TLOWer?",
    
    "tupper":       lambda s:           f"TRIGger:PULSe:TUPPer {s}",
    "tupper?":      lambda:              "TRIGger:PULSe:TUPPer?",
    }
#INTERVAL trigger subsubsystem command set
INTERVAL = {    
    "coupling":     lambda v:           f":TRIGger:INTerval:COUPling {v}",
    "coupling?":    lambda:             ":TRIGger:INTerval:COUPling?",
    "event":        lambda val:         f":TRIGger:INTerval:HLDEVent {val}",
    "event?":       lambda :             ":TRIGger:INTerval:HLDEVent?",
    "time":         lambda c:           f":TRIGger:INTerval:HLDTime {c}",
    "time?":        lambda:             ":TRIGger:INTerval:HLDTime?",   
    "start":        lambda t:           f":TRIGger:INTerval:HSTart {t}",
    "start?":       lambda:             ":TRIGger:INTerval:HSTart?",
    "holdoff":      lambda t:           f":TRIGger:INTerval:HOLDoff {t}",
    "holdoff?":     lambda:             ":TRIGger:INTerval:HOLDoff?",
    "level":        lambda t:           f":TRIGger:INTerval:LEVel {t}",
    "level?":       lambda:             ":TRIGger:INTerval:LEVel?",
    "limit":        lambda t:           f":TRIGger:INTerval:LIMit {t}",
    "limit?":       lambda:             ":TRIGger:INTerval:LIMit?",
    "noise":        lambda state:       f":TRIGger:INTerval:NREJect {state}",
    "noise?":       lambda:             ":TRIGger:INTerval:NREJect?",
    
    "source":       lambda s:           f":TRIGger:INTerval:SOURce {s}",
    "source?":      lambda:             ":TRIGger:INTerval:SOURce?",
    "slope":        lambda s:           f":TRIGger:INTerval:SLOPe {s}",
    "slope?":       lambda:             ":TRIGger:INTerval:SLOPe?",
    
    "tlower":       lambda s:           f":TRIGger:INTerval:TLOWer {s}",
    "tlower?":      lambda:             ":TRIGger:INTerval:TLOWer?",
    
    "tupper":       lambda s:           f"TRIGger:INTerval:TUPPer {s}",
    "tupper?":      lambda:              "TRIGger:INTerval:TUPPer?",

}

#DROPOUT triggering subsubsystem command set
DROPOUT = {    
    "coupling":         lambda v:           f":TRIGger:DROPout:COUPling {v}",
    "coupling?":        lambda:             ":TRIGger:DROPout:COUPling?",
    "event":            lambda val:         f":TRIGger:DROPout:HLDEVent {val}",
    "event?":           lambda :             ":TRIGger:DROPout:HLDEVent?",
    "time":             lambda c:           f":TRIGger:DROPout:HLDTime {c}",
    "time?":            lambda:             ":TRIGger:DROPout:HLDTime?",   
    "start":            lambda t:           f":TRIGger:DROPout:HSTart {t}",
    "start?":           lambda:             ":TRIGger:DROPout:HSTart?",
    "holdoff":          lambda t:           f":TRIGger:DROPout:HOLDoff {t}",
    "holdoff?":         lambda:             ":TRIGger:DROPout:HOLDoff?",
    "level":            lambda t:           f":TRIGger:DROPout:LEVel {t}",
    "level?":           lambda:             ":TRIGger:DROPout:LEVel?",
    "noise":            lambda state:       f":TRIGger:DROPout:NREJect {state}",
    "noise?":           lambda:             ":TRIGger:DROPout:NREJect?",
    
    "source":           lambda s:           f":TRIGger:DROPout:SOURce {s}",
    "source?":          lambda:             ":TRIGger:DROPout:SOURce?",
    "slope":            lambda s:           f":TRIGger:DROPout:SLOPe {s}",
    "slope?":           lambda:             ":TRIGger:DROPout:SLOPe?",
    
    "time":           lambda s:           f":TRIGger:DROPout:TIME {s}",
    "time?":          lambda:             ":TRIGger:DROPout:TIME?",
    
    "type":           lambda s:           f"TRIGger:DROPout:TYPE {s}",
    "type?":          lambda:              "TRIGger:DROPout:TYPE?",
    }
#RUNT triggering subsubsystem command set
RUNT = {    
    "coupling":         lambda v:           f":TRIGger:RUNT:COUPling {v}",
    "coupling?":        lambda:             ":TRIGger:RUNT:COUPling?",
    "event":            lambda val:         f":TRIGger:RUNT:HLDEVent {val}",
    "event?":           lambda :             ":TRIGger:RUNT:HLDEVent?",
    "time":             lambda c:           f":TRIGger:RUNT:HLDTime {c}",
    "time?":            lambda:             ":TRIGger:RUNT:HLDTime?",   
    "start":            lambda t:           f":TRIGger:RUNT:HSTart {t}",
    "start?":           lambda:             ":TRIGger:RUNT:HSTart?",
    "holdoff":          lambda t:           f":TRIGger:RUNT:HOLDoff {t}",
    "holdoff?":         lambda:             ":TRIGger:RUNT:HOLDoff?",
    "hlevel":           lambda t:           f":TRIGger:RUNT:HLEVel {t}",
    "hlevel?":          lambda:             ":TRIGger:RUNT:HLEVel?",
    "llevel":           lambda t:           f":TRIGger:RUNT:LLEVel {t}",
    "llevel?":          lambda:             ":TRIGger:RUNT:LLEVel?",
    "limit":            lambda t:           f":TRIGger:RUNT:LIMit {t}",
    "limit?":           lambda:             ":TRIGger:RUNT:LIMit?",
    "noise":            lambda state:       f":TRIGger:RUNT:NREJect {state}",
    "noise?":           lambda:             ":TRIGger:RUNT:NREJect?",
    "polarity":         lambda t:           f":TRIGger:RUNT:POLarity {t}",
    "polarity?":        lambda:             ":TRIGger:RUNT:POLarity?",    
    "source":           lambda s:           f":TRIGger:RUNT:SOURce {s}",
    "source?":          lambda:             ":TRIGger:RUNT:SOURce?",
    
    "tlower":           lambda s:           f":TRIGger:RUNT:TLOWer {s}",
    "tlower?":          lambda:             ":TRIGger:RUNT:TLOWer?",
    
    "tupper":           lambda s:           f"TRIGger:RUNT:TUPPer {s}",
    "tupper?":          lambda:              "TRIGger:RUNT:TUPPer?",
    }
#Window triggering subsubsystem command set
WINDOW = {    
    
    "clevel":           lambda v:           f":TRIGger:WINDow:COUPling {v}",
    "clevel?":          lambda:             ":TRIGger:WINDow:COUPling?",
    "dlevel":           lambda t:           f":TRIGger:WINDow:DLEVel {t}",
    "dlevel?":          lambda:             ":TRIGger:WINDow:DLEVel?",
    
    "coupling":         lambda v:           f":TRIGger:WINDow:COUPling {v}",
    "coupling?":        lambda:             ":TRIGger:WINDow:COUPling?",
    "event":            lambda val:         f":TRIGger:WINDow:HLDEVent {val}",
    "event?":           lambda :             ":TRIGger:WINDow:HLDEVent?",
    "time":             lambda c:           f":TRIGger:WINDow:HLDTime {c}",
    "time?":            lambda:             ":TRIGger:WINDow:HLDTime?",   
    "start":            lambda t:           f":TRIGger:WINDow:HSTart {t}",
    "start?":           lambda:             ":TRIGger:WINDow:HSTart?",
    "holdoff":          lambda t:           f":TRIGger:WINDow:HOLDoff {t}",
    "holdoff?":         lambda:             ":TRIGger:WINDow:HOLDoff?",
    "hlevel":           lambda t:           f":TRIGger:WINDow:HLEVel {t}",
    "hlevel?":          lambda:             ":TRIGger:WINDow:HLEVel?",
    "llevel":           lambda t:           f":TRIGger:WINDow:LLEVel {t}",
    "llevel?":          lambda:             ":TRIGger:WINDow:LLEVel?",
    "noise":            lambda state:       f":TRIGger:WINDow:NREJect {state}",
    "noise?":           lambda:             ":TRIGger:WINDow:NREJect?",
    "source":           lambda s:           f":TRIGger:WINDow:SOURce {s}",
    "source?":          lambda:             ":TRIGger:WINDow:SOURce?",
    "type":             lambda s:           f"TRIGger:WINDow:TYPE {s}",
    "type?":            lambda:              "TRIGger:WINDow:TYPE?",
    
    }

#PATTERN triggering subsubsystem command set
PATTERN = {    
    
    "event":            lambda val:         f":TRIGger:PATTern:HLDEVent {val}",
    "event?":           lambda :             ":TRIGger:PATTern:HLDEVent?",
    "time":             lambda c:           f":TRIGger:PATTern:HLDTime {c}",
    "time?":            lambda:             ":TRIGger:PATTern:HLDTime?",   
    "start":            lambda t:           f":TRIGger:PATTern:HSTart {t}",
    "start?":           lambda:             ":TRIGger:PATTern:HSTart?",
    "holdoff":          lambda t:           f":TRIGger:PATTern:HOLDoff {t}",
    "holdoff?":         lambda:             ":TRIGger:PATTern:HOLDoff?",
    "input":            lambda t:           f":TRIGger:PATTern:INPut {t}",
    "input?":           lambda:             ":TRIGger:PATTern:INPut?",
    "level":            lambda t:           f":TRIGger:PATTern:LEVel {t}",
    "level?":           lambda:             ":TRIGger:PATTern:LEVel?",
    "limit":            lambda t:           f":TRIGger:PATTern:LIMit {t}",
    "limit?":           lambda:             ":TRIGger:PATTern:LIMit?",
    "logic":            lambda t:           f":TRIGger:PATTern:LOGic {t}",
    "logic?":           lambda:             ":TRIGger:PATTern:LOGic?",
    "tlower":           lambda s:           f":TRIGger:PATTern:TLOWer {s}",
    "tlower?":          lambda:             ":TRIGger:PATTern:TLOWer?",
    
    "tupper":           lambda s:           f"TRIGger:PATTern:TUPPer {s}",
    "tupper?":          lambda:              "TRIGger:PATTern:TUPPer?",
    }

#DELAY trigger subsubsystem command set
DELAY = {    
    "coupling":         lambda v:           f":TRIGger:DELay:COUPling {v}",
    "coupling?":        lambda:             ":TRIGger:DELay:COUPling?",
    "source":           lambda s:           f":TRIGger:DELay:SOURce {s}",
    "source?":          lambda:             ":TRIGger:DELay:SOURce?",
    "source2":          lambda s:           f":TRIGger:DELay:SOURce2 {s}",
    "source2?":         lambda:             ":TRIGger:DELay:SOURce2?",
    "slope":            lambda s:           f":TRIGger:DELay:SLOPe {s}",
    "slope?":           lambda:             ":TRIGger:DELay:SLOPe?",
    "slope2":           lambda s:           f":TRIGger:DELay:SLOPe2 {s}",
    "slope2?":          lambda:             ":TRIGger:DELay:SLOPe2?",
    "level":            lambda t:           f":TRIGger:DELay:LEVel {t}",
    "level?":           lambda:             ":TRIGger:DELay:LEVel?",
    "level2":           lambda t:           f":TRIGger:DELay:LEVel2 {t}",
    "level2?":          lambda:             ":TRIGger:DELay:LEVel2?",
    "limit":            lambda t:           f":TRIGger:DELay:LIMit {t}",
    "limit?":           lambda:             ":TRIGger:DELay:LIMit?",
    "tlower":           lambda s:           f":TRIGger:DELay:TLOWer {s}",
    "tlower?":          lambda:             ":TRIGger:DELay:TLOWer?",
    "tupper":           lambda s:           f"TRIGger:DELay:TUPPer {s}",
    "tupper?":          lambda:              "TRIGger:DELay:TUPPer?",
    }

#NEDGE trigge0ring subsubsystem command set
NEDGE = {      
    "source":           lambda s:           f":TRIGger:NEDGe:SOURce {s}",
    "source?":          lambda:             ":TRIGger:NEDGe:SOURce?",
    "slope":            lambda s:           f":TRIGger:NEDGe:SLOPe {s}",
    "slope?":           lambda:             ":TRIGger:NEDGe:SLOPe?",
    "level":            lambda t:           f":TRIGger:NEDGe:LEVel {t}",
    "level?":           lambda:             ":TRIGger:NEDGe:LEVel?",
    "event":            lambda val:         f":TRIGger:NEDGe:HLDEVent {val}",
    "event?":           lambda :             ":TRIGger:NEDGe:HLDEVent?",
    "time":             lambda c:           f":TRIGger:NEDGe:HLDTime {c}",
    "time?":            lambda:             ":TRIGger:NEDGe:HLDTime?",   
    "start":            lambda t:           f":TRIGger:NEDGe:HSTart {t}",
    "start?":           lambda:             ":TRIGger:NEDGe:HSTart?",
    "holdoff":          lambda t:           f":TRIGger:NEDGe:HOLDoff {t}",
    "holdoff?":         lambda:             ":TRIGger:NEDGe:HOLDoff?",
    "idle":             lambda state:       f":TRIGger:NEDGe:IDLE {state}",
    "idle?":            lambda:             ":TRIGger:NEDGe:IDLE?",
    "edge":             lambda state:       f":TRIGger:NEDGe:EDGE {state}",
    "edge?":            lambda:             ":TRIGger:NEDGe:EDGE?",

    "noise":            lambda state:       f":TRIGger:NEDGe:NREJect {state}",
    "noise?":           lambda:             ":TRIGger:NEDGe:NREJect?",
    
    }
TRIGGER = {
    "run":              lambda:             ":TRIGger:RUN",
    "stop":             lambda:             ":TRIGger:STOP",
    "type":             lambda v:           f":TRIGger:TYPE {v}",
    
    "mode":             lambda v:           f":TRIGger:MODE {v}",
    "mode?":            lambda:             ":TRIGger:MODE?",
    # frequency trigger (added in E11D)
    "freq":             lambda v:           f":TRIGger:FREQuency {v}",
    "freq?":            lambda:             ":TRIGger:FREQuency?",
    "status?":          lambda:             ":TRIGger:STATus?",
    "EDGE": EDGE,    
    "SLOPE":SLOPE,
    "PULSE":PULSE,
    "INTERVAL":INTERVAL,
    "DROPOUT":DROPOUT,
    "RUNT":RUNT,
    "WINDOW":WINDOW,
    "PATTERN":PATTERN,    
    "DELAY":DELAY,
    "NEDGE":NEDGE,            
    # add generic bus trigger factory
    "bus":  lambda b,cmd,*args: f":TRIGger:{b}:{cmd} " + ",".join(map(str,args)) if args else f":TRIGger:{b}:{cmd}"
}
"""
:TRIGger:VIDeo Commands
        The :TRIGGER:VIDeo subsystem commands control the video trigger parameters.
         :TRIGger:VIDeo:FCNT
         :TRIGger:VIDeo:FIELd
         :TRIGger:VIDeo:FRATe
         :TRIGger:VIDeo:INTerlace
         :TRIGger:VIDeo:LCNT
         :TRIGger:VIDeo:LEVel
         :TRIGger:VIDeo:LINE
         TRIGger:VIDeo:SOURce
         :TRIGger:VIDeo:STANdard
         :TRIGger:VIDeo:SYNC"""


"""      :TRIGger:QUALified:ELEVel
         :TRIGger:QUALified:ESLope
         :TRIGger:QUALified:ESource
         :TRIGger:QUALified:LIMit
         :TRIGger:QUALified:QLEVel
         :TRIGger:QUALified:QSource
         :TRIGger:QUALified:TLOWer
         :TRIGger:QUALified:TUPPer
         :TRIGger:QUALified:TYPE"""


""":TRIGger:SHOLd Commands
        The :TRIGGER:SHOLd subsystem commands control the setup/hold trigger parameters.
         : SHOLd :TYPE
         : SHOLd :CSource
         : SHOLd :CTHReshold
         : SHOLd :SLOPe
         : SHOLd :DSource
         : SHOLd :DTHReshold
         : SHOLd :LEVel
         : SHOLd :LIMit
         : SHOLd :TUPPer
         : SHOLd :TLOWer"""
    
""" :TRIGger:IIC Commands
        The :TRIGGER:IIC subsystem commands control the IIC bus trigger parameters.
         :TRIGger:IIC:ADDRess
         :TRIGger:IIC:ALENgth
         :TRIGger:IIC:CONDition
         :TRIGger:IIC:DAT2
         :TRIGger:IIC:DATA
         :TRIGger:IIC:DLENgth
         :TRIGger:IIC:LIMit
         :TRIGger:IIC:RWBit
         :TRIGger:IIC:SCLSource
         :TRIGger:IIC:SCLThreshold
         :TRIGger:IIC:SDASource
         :TRIGger:IIC:SDAThreshold"""
    
"""      :TRIGger: BIT ord er
         :TRIGger:SPI:CLKSource
         :TRIGger:SPI:CLKThreshold
         :TRIGger:SPI:CSSource
         :TRIGger:SPI:CSThreshold
         :TRIGger:SPI:CSTYpe
         :TRIGger:SPI:DATA
         :TRIGger:SPI:DLENgth
         :TRIGger:SPI:LATChedge
         :TRIGger:SPI:MISOSource
         :TRIGger:SPI:MISOThreshold
         :TRIGger:SPI:MOSISource
         :TRIGger:SPI:MOSIThreshold
         :TRIGger:SPI:NCSSource
         :TRIGger:SPI:NCSThreshold
         :TRIGger:SPI:TTYPe"""
    
"""The :TRIGGER:UART subsystem
        commands control the UART bus trigger parameters.
         TRIGger:UART:BAUD
         :TRIGger: BITorder
         :TRIGger:UART:CONDition
         :TRIGger:UART:DATA
         :TRIGger:UART:DLENgth
         :TRIGger:UART:IDLE
         :TRIGger:UART:LIMit
         :TRIGger:UART:PARity
         :TRIGger:UART:RXSource
         :TRIGger:UART:RXThreshold
         :TRIGger:UART:STOP
         :TRIGger:UART:TTYPe
         :TRIGger:UART:TXSource
         :TRIGger:UART:TXThreshold"""
    
""":TRIGger:CAN Commands
        The :TRIGGER:CAN subsystem commands control the CAN bus trigger parameters.
         :TRIGger:CAN:BAUD
         :TRIGger:CAN:CONDition
         :TRIGger:CAN:DAT2
         :TRIGger:CAN:DATA
         :TRIGger:CAN:ID
         :TRIGger:CAN:IDLength
         :TRIGger:CAN:SOURce
         :TRIGger:CAN:THReshold"""
    
"""      :TRIGger:LIN:BAUD
         :TRIGger:LIN:CONDition
         :TRIGger:LIN:DAT2
         :TRIGger:LIN:DATA
         :TRIGger:LIN:ERRor:CHECksum
         :TRIGger:LIN:ERRor:DLENgth
         :TRIGger:LIN:ERRor:ID
         :TRIGger:LIN:ERRor:PARity
         :TRIGger:LIN:ERRor:SYNC
         :TRIGger:LIN:ID
         :TRIGger:LIN:SOURce
         :TRIGger:LIN:STANdard
         :TRIGger:LIN:THReshold"""
    
"""      :TRIGger:FLEXray:BAUD
         :TRIGger:FLEXray:CONDition
         :TRIGger:FLEXray:FRAMe:COMPare
         :TRIGger:FLEXray:FRAMe:CYCLe
         :TRIGger:FLEXray:FRAMe:ID
         :TRIGger:FLEXray:FRAMe:REPetition
         :TRIGger:FLEXray:SOURce
         :TRIGger:FLEXray:THReshold"""
    
"""      :TRIGger:CANFd:BAUDData
         : CANFd:BAUDNominal
         :TRIGger:CANFd:C ONDition
         :TRIGger:CANFd:DAT2
         :TRIGger:CANFd:DATA
         :TRIGger:CANFd:FTYPe
         :TRIGger:CANFd:ID
         :TRIGger:CANFd:IDLength
         :TRIGger:CANFd:SOURce
         :TRIGger:CANFd:THReshold"""

""":TRIGger:IIS Commands [Option]
    The :TRIGGER:IIS subsystem  commands control the IIS bus trigger parameters.
     :TRIGger:IIS:AVARiant
     :TRIGger:IIS:BCLKSource
     :TRIGger:IIS:BCLKThreshold
     :TRIGger: BITorder
     :TRIGger:IIS:CHANnel
     :TRIGger:IIS:COMPare
     :TRIGger:IIS:CONDition
     :TRIGger:IIS:DLENgth
     :TRIGger:IIS:DSource
     :TRIGger:IIS:DTHReshold
     :TRIGger:IIS:LATChedge
     :TRIGger:IIS:LCH
     :TRIGger:IIS:VALue
     :TRIGger:IIS:WSSource
     :TRIGger:IIS:WSTHreshold"""
IIS ={
    # IIS bus example (many bus triggers exist; follow same pattern)
    "wssource":         lambda v:         f":TRIGger:IIS:WSSource {v}",
    "wssource?":        lambda:            ":TRIGger:IIS:WSSource?",
    "wsthreshold":      lambda v:         f":TRIGger:IIS:WSThreshold {v}",
    "wsthreshold?":     lambda:            ":TRIGger:IIS:WSThreshold?",
    
}

#
# WAVeform subsystem
#
WAVEFORM = {
    "data?":            lambda:            ":WAVeform:DATA?",
    "source":           lambda src:        f":WAVeform:SOURce {src}",
    "source?":          lambda:            ":WAVeform:SOURce?",
    "preamble?":        lambda:            ":WAVeform:PREamble?",
    "points":           lambda v:          f":WAVeform:POINt {v}", #deze was chatGPT vergeten.....
    "points?":          lambda:            ":WAVeform:POINt?",
    "start":            lambda v:          f":WAVeform:STARt {v}",
    "start?":           lambda:            ":WAVeform:STARt?",
    "interval":         lambda v:          f":WAVeform:INTerval {v}",
    "interval?":        lambda:            ":WAVeform:INTerval?",
    "width":            lambda v:          f":WAVeform:WIDTh {v}",
    "width?":           lambda:            ":WAVeform:WIDTh?",
    "maxpoint?":        lambda:            ":WAVeform:MAXPoint?",
    "sequence":         lambda v1, v2=None: f":WAVeform:SEQuence {v1}" + (f",{v2}" if v2 is not None else ""),
    "sequence?":        lambda:            ":WAVeform:SEQuence?",
    # helper: request wave data from channel/function/digital
    "set_source_ch":    lambda ch:         f":WAVeform:SOURce C{ch}",
    "set_source_func":  lambda fidx:       f":WAVeform:SOURce F{fidx}",
    "set_source_dig":   lambda d:          f":WAVeform:SOURce D{d}",
    # reading helpers documented in manual (preamble parsing etc.) see WAVeform PREamble table. :contentReference[oaicite:6]{index=6}
}

#
# CURSOR subsystem
#
CURSOR = {
    "on":               lambda s:          f":CURSor {s}",
    "on?":              lambda:            ":CURSor?",
    "tagstyle":         lambda v:          f":CURSor:TAGStyle {v}",
    "tagstyle?":        lambda:            ":CURSor:TAGStyle?",
    "mode":             lambda v:          f":CURSor:MODE {v}",
    "mode?":            lambda:            ":CURSor:MODE?",
    "sour1":            lambda src:        f":CURSor:SOURce1 {src}",
    "sour1?":           lambda:            ":CURSor:SOURce1?",
    "sour2":            lambda src:        f":CURSor:SOURce2 {src}",
    "sour2?":           lambda:            ":CURSor:SOURce2?",
    "x1":               lambda v:          f":CURSor:X1 {v}",
    "x1?":              lambda:            ":CURSor:X1?",
    "x2":               lambda v:          f":CURSor:X2 {v}",
    "x2?":              lambda:            ":CURSor:X2?",
    "y1":               lambda v:          f":CURSor:Y1 {v}",
    "y1?":              lambda:            ":CURSor:Y1?",
    "y2":               lambda v:          f":CURSor:Y2 {v}",
    "y2?":              lambda:            ":CURSor:Y2?",
    "xdelta?":          lambda:            ":CURSor:XDELta?",
    "ydelta?":          lambda:            ":CURSor:YDELta?",
    "mitem":            lambda typ,src1,src2=None: f":CURSor:MITem {typ},{src1}" + (f",{src2}" if src2 else ""),
    "mitem?":           lambda:            ":CURSor:MITem?",
}

#
# DISPLAY subsystem
#
DISPLAY = {
    "print?":           lambda t:          f":PRINt? {t}",            # BMP|PNG
    "format_data":      lambda opt,d=None: f":FORMat:DATA {opt}" + (f",{d}" if d is not None else ""),
    "format_data?":     lambda:            ":FORMat:DATA?",
    # screen dump and axis/label controls exist in manual
}

#
# SAVE / RECALL
#
SAVE = {
    "binary":           lambda path, src=None: f":SAVE:BINary {path}" + (f",{src}" if src else ""),
    "png":              lambda path, src=None: f":SAVE:IMAGe:FILE {path},{src}" if src else f":SAVE:IMAGe:FILE {path}",
    "setup":            lambda path:        f":SAVE:SETup {path}",
    "default":          lambda:             ":SAVE:DEFault",
    "matlab":           lambda path, src=None: f":SAVE:MATLab {path}" + (f",{src}" if src else ""),
}

RECALL = {
    "setup":            lambda path:        f":RECall:SETup {path}",
    "setup?":           lambda:             ":RECall:SETup?",
    "fdefault":         lambda:             ":RECall:FDEFault"
}

#
# SYSTEM subsystem (many items)
#
SYSTEM = {
    "idn?":                 lambda:            "*IDN?",
    "opc?":                 lambda:            "*OPC?",
    "reset":                lambda:            "*RST",
    "autoset":              lambda:            ":AUToset",
    "menu":                 lambda s:          f":SYSTem:MENU {s}",
    "menu?":                lambda:            ":SYSTem:MENU?",
    "language":             lambda v:          f":SYSTem:LANGuage {v}",
    "language?":            lambda:            ":SYSTem:LANGuage?",
    "pon":                  lambda s:          f":SYSTem:PON {s}",
    "pon?":                 lambda:            ":SYSTem:PON?",
    "reboot":               lambda:            ":SYSTem:REBoot",
    "shutdown":             lambda:            ":SYSTem:SHUTdown",
    "remote":               lambda s:          f":SYSTem:REMote {s}",
    "remote?":              lambda:            ":SYSTem:REMote?",
    "selfcal":              lambda:            ":SYSTem:SELFCal",
    "selfcal?":             lambda:            ":SYSTem:SELFCal?",
    # network storage (NSTorage) group
    "nstorage":             lambda path,user,pwd,anon,auto_con,rem_path,rem_user,rem_pwd: f":SYSTem:NSTorage {qstr(path)},{qstr(user)},{qstr(pwd)},{anon},{auto_con},{rem_path},{rem_user},{rem_pwd}",
    "nstorage?":            lambda:            ":SYSTem:NSTorage?",
    "nstorage_connect":     lambda:            ":SYSTem:NSTorage:CONNect",
    "nstorage_disconnect":  lambda:         ":SYSTem:NSTorage:DISConnect",
    "nstorage_status?":     lambda:            ":SYSTem:NSTorage:STATus?",
}

#
# DIGITAL subsystem (option)
#
DIGITAL = {
    "srate?":           lambda:            ":DIGital:SRATe?",
    "skew":             lambda v:          f":DIGital:SKEW {v}",
    "skew?":            lambda:            ":DIGital:SKEW?",
    "threshold":        lambda n, t:       f":DIGital:THReshold{n} {t}",
    "threshold?":       lambda n:          f":DIGital:THReshold{n}?",
    "enable":           lambda group, s:    f":DIGital:ENAble {group},{s}",
    "enable?":          lambda:            ":DIGital:ENAble?",
}

TIMEBASE = {
    "delay?":           lambda:             ":TIMebase:DELay?",
    "delay":            lambda t:           f":TIMebase:DELay {t}",
    "reference":        lambda v:           f":TIMebase:REFerence {v}",
    "reference?":       lambda:             ":TIMebase:REFerence?",
    "position":         lambda n:           f":TIMebase:REFerence:POSition {n}",
    "position?":        lambda:             f":TIMebase:REFerence:POSition?",
    "scale":            lambda n:           f":TIMebase:SCALe {n}",
    "scale?":           lambda:             ":TIMebase:SCALe?",
    "window":           lambda v:           f":TIMebase:WINDow {v}",
    "window?":          lambda:             ":TIMebase:WINDow?",
    "windelay":         lambda v:           f":TIMebase:WINDow:DELay {v}",
    "windelay?":        lambda:             ":TIMebase:WINDow:DELay?",
    "winscale":         lambda v:           f":TIMebase:WINDow:SCALe {v}",
    "winscale?":        lambda:             ":TIMebase:WINDow:SCALe?",
}


#TODO: add commands below
#:TIMebase:WINDow
# :TIMebase:WINDow:DELay
# :TIMebase:WINDow:SCALe

#
# DECODE subsystem (bus decoding)
#
DECODE = {
    "on":               lambda typ, s:     f":DECode:{typ} {s}",
    "on?":              lambda typ:        f":DECode:{typ}?",
    "result?":          lambda typ:        f":DECode:{typ}:REsult?",
    # includes 1553B, SENT, Manchester etc. (E11D adds commands). :contentReference[oaicite:7]{index=7}
}

#
# MEASURE subsystem (skeleton; many items)
#
MEASURE = {
    "meas?":            lambda:                 ":MEASure:?",
    "meas":             lambda state:           f":MEASure: {state}",
    
    "measmode":         lambda mode:            f":MEASure:MODE {mode}",
    "measmode?":        lambda:                 ":MEASure:MODE?",

    "measstat":         lambda status:          f":MEASure:ADVanced:STATistics {status}",
    "measstat?":        lambda:                 ":MEASure:ADVanced:STATistics?",
    
    "meashisto":        lambda status:          f":MEASure:ADVanced:STATistics:HISTOGram {status}",
    "meashisto?":       lambda:                 ":MEASure:ADVanced:STATistics:HISTOGram?",
    "measmaxcnt":       lambda status:          f":MEASure:ADVanced:STATistics:MAXCount {status}",
    "measmaxcnt?":      lambda:                 ":MEASure:ADVanced:STATistics:MAXCount?",
  
    "measrststat":      lambda:                 ":MEASure:ADVanced:STATistics:RESet",

    "measstyle":        lambda style:           f":MEASure:ADVanced:STYLe {style}",
    "measstyle?":       lambda:                 ":MEASure:ADVanced:STYLe?",
    
    "measgate":         lambda status:          f":MEASure:GATE {status}",
    "measgate?":        lambda:                 ":MEASure:GATE?",
    "measgatea":        lambda gate:            f":MEASure:GATE:GA {gate}",
    "measgatea?":       lambda:                 ":MEASure:GATE:GA?",
    "measgateb":        lambda gate:            f":MEASure:GATE:GB {gate}",
    "measgateb?":       lambda:                 ":MEASure:GATE:GB?",
    

    "linenr":           lambda linenr:          f":MEASure:ADVanced:LINenumber {linenr}",
    "linenr?":          lambda:                 ":MEASure:ADVanced:LINenumber?",
    "measitem":         lambda nr, state:       f":MEASure:ADVanced:P{nr} {state}",
    "measitem?":        lambda nr:              f":MEASure:ADVanced:P{nr}?",
 
    "meassimpleitem":   lambda item, state:     f":MEASure: SIMPle:ITEM {item},{state}",
     
    "measitemsrc1":     lambda nr, src:         f":MEASure:ADVanced:P{nr}:SOURce1 {src}",
    "measitemsrc1?":    lambda nr:              f":MEASure:ADVanced:P{nr}:SOURce1?",
    "measitemsrc2":     lambda nr, src:         f":MEASure:ADVanced:P{nr}:SOURce2 {src}",
    "measitemsrc2?":    lambda nr:              f":MEASure:ADVanced:P{nr}:SOURce2?",

    
    "meassimplesrc":    lambda linenr:          f":MEASure:SIMPle:SOURce {linenr}",
    "meassimplesrc?":   lambda:                 ":MEASure:ADVanced:LINenumber?",
    
    "meassimpleval?":   lambda item:            f":MEASure:SIMPle:VALue? {item}",
    
    "measitemstat":     lambda nr, typestat:    f":MEASure:ADVanced:P{nr}:STATistics {typestat}",
    "measitemstat?":    lambda nr:              f":MEASure:ADVanced:P{nr}:STATistics?",
    
    "measitemtype":     lambda nr, mtype:       f":MEASure:ADVanced:P{nr}:TYPE {mtype}",
    "measitemtype?":    lambda nr:              f":MEASure:ADVanced:P{nr}:TYPE?",
    
    "measitemval?":     lambda nr:              f":MEASure:ADVanced:P{nr}:VALue?",
    
    "item":             lambda spec:            f":MEASure:ITEM {spec}",
    "item?":            lambda:                 ":MEASure:ITEM?",
    "auto?":            lambda:                 ":MEASure:AUTOn?",
    "list":             lambda:                 ":MEASure:LIST?",

    "measthresholdsrc": lambda src:             f":MEASure:THReshold:SOURce {src}",
    "measthresholdsrc?":lambda:                 f":MEASure:THReshold:SOURce?",

    "measthresholdtype":lambda thrtype:         f":MEASure:THReshold:TYPE {thrtype}",
    "measthresholtype?":lambda:                 ":MEASure:THReshold:TYPE?",

    "measabsthr":       lambda high, mid, low:  f":MEASure:THReshold:ABSolute {high},{mid},{low}",
    "measabsthr?":      lambda:                 ":MEASure:THReshold:ABSolute?",

    "measpercthr":      lambda high, mid, low:  f":MEASure:THReshold:PERCent {high},{mid},{low}",
    "measpercthr?":     lambda:                 ":MEASure:THReshold:PERCent?",

    # advanced measure items exist (PSLOPE, NSLOPE, TSR etc in E11C/E11D)
}

#
# FUNCtion (math/FFT/integrate)
#
FUNCTION = {
    "select":           lambda idx, src:   f":FUNCtion{idx}:SOURce {src}",
    "fft_span":         lambda idx, v:     f":FUNCtion{idx}:FFT:SPAN {v}",
    "intgate":          lambda idx, s:     f":FUNCtion{idx}:INTegrate:GATE {s}",
}

#
# DVM subsystem (if present)
#
DVM = {
    "on":               lambda s:          f":DVM {s}",
    "on?":              lambda:            ":DVM?",
    "range":            lambda r:          f":DVM:RANGe {r}",
    "range?":           lambda:            ":DVM:RANGe?"
}

#
# WGEN subsystem (if FG option present)
#
WGEN = {
    "output":           lambda ch, s:      f":WGEN:OUTPut{ch} {s}",
    "arbwave":          lambda name:       f":WGEN:ARbWaVe {name}",
    "storelist":        lambda l:          f":WGEN:SToreList {l}",
    # refer to SDG programming guide for full WGEN syntax (not fully consistent). :contentReference[oaicite:8]{index=8}
}

#
# HISTORY / MEMORY / MTEST / REF
#
HISTORY = {
    "on":               lambda s:          f":HISTory {s}",
    "count?":           lambda:            ":HISTory:COUNt?",
}

MEMORY = {
    "switch":           lambda n,s:        f":MEMory{n}:SWITch {s}",
    "vpos":             lambda n,v:        f":MEMory{n}:VERTical:POSition {v}",
    "vpos?":            lambda n:          f":MEMory{n}:VERTical:POSition?",
}

MTEST = {
    "selftest?":        lambda:            ":MTESt:SELF?"
}

REF = {
    "set":              lambda name, v:    f":REF:{name} {v}",
    "get":              lambda name:       f":REF:{name}?"
}

#
# Root / Common commands
#
ROOT = {
    "autoset":          lambda:            ":AUToset",
    "print?":           lambda t:          f":PRINt? {t}",
    "format_data":      lambda opt,d=None: f":FORMat:DATA {opt}" + (f",{d}" if d else ""),
    "*idn?":            lambda:            "*IDN?",
    "*opc?":            lambda:            "*OPC?",
    "*rst":             lambda:            "*RST",
}

# Aggregate SCPI dict
SCPI = {
    "CHANNEL": CHANNEL,
    "ACQUIRE": ACQUIRE,
    "TRIGGER": TRIGGER,
    "WAVEFORM": WAVEFORM,
    "CURSOR": CURSOR,
    "DISPLAY": DISPLAY,
    "SAVE": SAVE,
    "RECALL": RECALL,
    "SYSTEM": SYSTEM,
    "DIGITAL": DIGITAL,
    "DECODE": DECODE,
    "MEASURE": MEASURE,
    "FUNCTION": FUNCTION,
    "DVM": DVM,
    "WGEN": WGEN,
    "HISTORY": HISTORY,
    "MEMORY": MEMORY,
    "MTEST": MTEST,
    "REF": REF,
    "ROOT": ROOT,
}
