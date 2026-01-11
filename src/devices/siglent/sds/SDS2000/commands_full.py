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
    "type_1":             lambda v:         f":ACQuire:TYPE {v}",
    "type_2":             lambda v1, v2:         f":ACQuire:TYPE {v1},{v2}",
    "type?":            lambda:            ":ACQuire:TYPE?",
    "points_to":        lambda v:         f":ACQuire:POINts {v}",  # some models accept set points
}

#
# TRIGGER subsystem (large, includes EDGE, FREQuency, BUS-specific)
#
TRIGGER = {
    "mode":             lambda v:         f":TRIGger:MODE {v}",
    "mode?":            lambda:            ":TRIGger:MODE?",
    "level":            lambda ch, v=None: (f":TRIGger:LEVEl{ch} {v}" if v is not None else f":TRIGger:LEVEl {ch}"),
    "level?":           lambda ch=None:    (f":TRIGger:LEVEl{ch}?" if ch is not None else ":TRIGger:LEVEl?"),
    "edge_source":      lambda s:         f":TRIGger:EDGE:SOURce {s}",
    "edge_source?":     lambda:            ":TRIGger:EDGE:SOURce?",
    "edge_slope":       lambda s:         f":TRIGger:EDGE:SLOPe {s}",
    "edge_slope?":      lambda:            ":TRIGger:EDGE:SLOPe?",
    # frequency trigger (added in E11D)
    "freq":             lambda v:         f":TRIGger:FREQuency {v}",
    "freq?":            lambda:            ":TRIGger:FREQuency?",
    "edge_impedance":   lambda v:         f":TRIGger:EDGE:IMPedance {v}",
    "edge_impedance?":  lambda:            ":TRIGger:EDGE:IMPedance?",
    # IIS bus example (many bus triggers exist; follow same pattern)
    "iis_wssource":     lambda v:         f":TRIGger:IIS:WSSource {v}",
    "iis_wssource?":    lambda:            ":TRIGger:IIS:WSSource?",
    "iis_wsthreshold":  lambda v:         f":TRIGger:IIS:WSThreshold {v}",
    "iis_wsthreshold?": lambda:            ":TRIGger:IIS:WSThreshold?",
    # add generic bus trigger factory
    "bus":              lambda b,cmd,*args: f":TRIGger:{b}:{cmd} " + ",".join(map(str,args)) if args else f":TRIGger:{b}:{cmd}"
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
    "idn?":             lambda:            "*IDN?",
    "opc?":             lambda:            "*OPC?",
    "reset":            lambda:            "*RST",
    "autoset":          lambda:            ":AUToset",
    "menu":             lambda s:          f":SYSTem:MENU {s}",
    "menu?":            lambda:            ":SYSTem:MENU?",
    "language":         lambda v:          f":SYSTem:LANGuage {v}",
    "language?":        lambda:            ":SYSTem:LANGuage?",
    "pon":              lambda s:          f":SYSTem:PON {s}",
    "pon?":             lambda:            ":SYSTem:PON?",
    "reboot":           lambda:            ":SYSTem:REBoot",
    "shutdown":         lambda:            ":SYSTem:SHUTdown",
    "remote":           lambda s:          f":SYSTem:REMote {s}",
    "remote?":          lambda:            ":SYSTem:REMote?",
    "selfcal":          lambda:            ":SYSTem:SELFCal",
    "selfcal?":         lambda:            ":SYSTem:SELFCal?",
    # network storage (NSTorage) group
    "nstorage":         lambda path,user,pwd,anon,auto_con,rem_path,rem_user,rem_pwd: f":SYSTem:NSTorage {qstr(path)},{qstr(user)},{qstr(pwd)},{anon},{auto_con},{rem_path},{rem_user},{rem_pwd}",
    "nstorage?":        lambda:            ":SYSTem:NSTorage?",
    "nstorage_connect": lambda:            ":SYSTem:NSTorage:CONNect",
    "nstorage_disconnect": lambda:         ":SYSTem:NSTorage:DISConnect",
    "nstorage_status?": lambda:            ":SYSTem:NSTorage:STATus?",
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
    "scale":           lambda n:            f":TIMebase:SCALe {n}",
    "scale?":          lambda:             ":TIMebase:SCALe?",
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
    "item":             lambda spec:       f":MEASure:ITEM {spec}",
    "item?":            lambda:            ":MEASure:ITEM?",
    "auto?":            lambda:            ":MEASure:AUTOn?",
    "list":             lambda:            ":MEASure:LIST?",
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
