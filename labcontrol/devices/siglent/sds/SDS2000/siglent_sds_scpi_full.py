# siglent_sds_scpi_full.py
# Auto-generated SCPI mapping for Siglent SDS Series (EN11D Programming Guide).
# Source: SDS-Series_ProgrammingGuide_EN11D.pdf

from typing import Any

def qstr(s: str) -> str:
    """Return a quoted SCPI string (double quotes)."""
    return f'"{s}"'

def ch(n: int) -> str:
    return f"CHANnel{n}"

# CHANNEL subsystem
CHANNEL = {
    "scale": lambda n, v: f":CHANnel{n}:SCALe {v}",
    "scale?": lambda n: f":CHANnel{n}:SCALe?",
    "offset": lambda n, v: f":CHANnel{n}:OFFSet {v}",
    "offset?": lambda n: f":CHANnel{n}:OFFSet?",
    "probe": lambda n, mode, value=None: f":CHANnel{n}:PROBe {mode}" + (f",{value}" if value is not None else ""),
    "probe?": lambda n: f":CHANnel{n}:PROBe?",
    "coupling": lambda n, mode: f":CHANnel{n}:COUPling {mode}",
    "coupling?": lambda n: f":CHANnel{n}:COUPling?",
    "bwlimit": lambda n, v: f":CHANnel{n}:BWLimit {v}",
    "bwlimit?": lambda n: f":CHANnel{n}:BWLimit?",
    "impedance": lambda n, v: f":CHANnel{n}:IMPedance {v}",
    "impedance?": lambda n: f":CHANnel{n}:IMPedance?",
    "invert": lambda n, s: f":CHANnel{n}:INVert {s}",
    "invert?": lambda n: f":CHANnel{n}:INVert?",
    "label": lambda n, s: f":CHANnel{n}:LABel {s}",
    "label?": lambda n: f":CHANnel{n}:LABel?",
    "label_text": lambda n, text: f":CHANnel{n}:LABel:TEXT {qstr(text)}",
    "label_text?": lambda n: f":CHANnel{n}:LABel:TEXT?",
    "skew": lambda n, v: f":CHANnel{n}:SKEW {v}",
    "skew?": lambda n: f":CHANnel{n}:SKEW?",
    "unit": lambda n, u: f":CHANnel{n}:UNIT {u}",
    "unit?": lambda n: f":CHANnel{n}:UNIT?",
    "switch": lambda n, s: f":CHANnel{n}:SWITch {s}",
    "switch?": lambda n: f":CHANnel{n}:SWITch?",
    "visible": lambda n, s: f":CHANnel{n}:VISible {s}",
    "visible?": lambda n: f":CHANnel{n}:VISible?",
}

# ACQUIRE subsystem
ACQUIRE = {
    "mode": lambda v: f":ACQuire:MODE {v}",
    "mode?": lambda: ":ACQuire:MODE?",
    "type": lambda v: f":ACQuire:TYPE {v}",
    "type?": lambda: ":ACQuire:TYPE?",
    "mdepth": lambda v: f":ACQuire:MDEPth {v}",
    "mdepth?": lambda: ":ACQuire:MDEPth?",
    "srate?": lambda: ":ACQuire:SRATe?",
    "points?": lambda: ":ACQuire:POINts?",
}

# TRIGGER subsystem
TRIGGER = {
    "mode": lambda v: f":TRIGger:MODE {v}",
    "mode?": lambda: ":TRIGger:MODE?",
    "level": lambda ch, v: f":TRIGger:LEVEl{ch} {v}",
    "level?": lambda ch=None: f":TRIGger:LEVEl{ch}?" if ch else ":TRIGger:LEVEl?",
    "edge_source": lambda s: f":TRIGger:EDGE:SOURce {s}",
    "edge_source?": lambda: ":TRIGger:EDGE:SOURce?",
    "edge_slope": lambda s: f":TRIGger:EDGE:SLOPe {s}",
    "edge_slope?": lambda: ":TRIGger:EDGE:SLOPe?",
}

# WAVEFORM subsystem
WAVEFORM = {
    "data?": lambda: ":WAVeform:DATA?",
    "source": lambda src: f":WAVeform:SOURce {src}",
    "source?": lambda: ":WAVeform:SOURce?",
    "preamble?": lambda: ":WAVeform:PREamble?",
    "points?": lambda: ":WAVeform:POINt?",
    "start": lambda v: f":WAVeform:STARt {v}",
    "start?": lambda: ":WAVeform:STARt?",
    "interval": lambda v: f":WAVeform:INTerval {v}",
    "interval?": lambda: ":WAVeform:INTerval?",
    "width": lambda v: f":WAVeform:WIDTh {v}",
    "width?": lambda: ":WAVeform:WIDTh?",
}

# CURSOR subsystem
CURSOR = {
    "on": lambda s: f":CURSor {s}",
    "on?": lambda: ":CURSor?",
    "mode": lambda v: f":CURSor:MODE {v}",
    "mode?": lambda: ":CURSor:MODE?",
    "x1": lambda v: f":CURSor:X1 {v}",
    "x1?": lambda: ":CURSor:X1?",
    "x2": lambda v: f":CURSor:X2 {v}",
    "x2?": lambda: ":CURSor:X2?",
}

# SYSTEM subsystem
SYSTEM = {
    "idn?": lambda: "*IDN?",
    "opc?": lambda: "*OPC?",
    "rst": lambda: "*RST",
    "autoset": lambda: ":AUToset",
    "language": lambda v: f":SYSTem:LANGuage {v}",
    "language?": lambda: ":SYSTem:LANGuage?",
}

# ROOT subsystem
ROOT = {
    "autoset": lambda: ":AUToset",
    "print?": lambda t: f":PRINt? {t}",
    "format_data": lambda opt, d=None: f":FORMat:DATA {opt}" + (f",{d}" if d else ""),
    "*idn?": lambda: "*IDN?",
    "*opc?": lambda: "*OPC?",
    "*rst": lambda: "*RST",
}

# Combine
SCPI = {
    "CHANNEL": CHANNEL,
    "ACQUIRE": ACQUIRE,
    "TRIGGER": TRIGGER,
    "WAVEFORM": WAVEFORM,
    "CURSOR": CURSOR,
    "SYSTEM": SYSTEM,
    "ROOT": ROOT,
}
