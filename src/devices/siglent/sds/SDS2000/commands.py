# siglent_scpi_commands.py
# Auto-generated mapping (main groups) based on Siglent SDS Series Programming Guide.
# Source: SDS-Series_ProgrammingGuide_EN11D.pdf. See file citations in the chat.

CHANNEL = {
    # set / query vertical scale (V/div)
    "scale":      lambda ch, value: f":CHANnel{ch}:SCALe {value}",
    "scale?":     lambda ch:         f":CHANnel{ch}:SCALe?",
    # offset
    "offset":     lambda ch, value: f":CHANnel{ch}:OFFSet {value}",
    "offset?":    lambda ch:        f":CHANnel{ch}:OFFSet?",
    # probe attenuation
    "probe":      lambda ch, mode, value=None: (
                        f":CHANnel{ch}:PROBe {mode}" + (f",{value}" if value is not None else "")
                   ),
    "probe?":     lambda ch:        f":CHANnel{ch}:PROBe?",
    # coupling
    "coupling":   lambda ch, mode:  f":CHANnel{ch}:COUPling {mode}",
    "coupling?":  lambda ch:        f":CHANnel{ch}:COUPling?",
    # bandwidth limit
    "bwlimit":    lambda ch, val:   f":CHANnel{ch}:BWLimit {val}",
    "bwlimit?":   lambda ch:        f":CHANnel{ch}:BWLimit?",
    # impedance
    "impedance":  lambda ch, val:   f":CHANnel{ch}:IMPedance {val}",
    "impedance?": lambda ch:        f":CHANnel{ch}:IMPedance?",
    # invert
    "invert":     lambda ch, state: f":CHANnel{ch}:INVert {state}",
    "invert?":    lambda ch:        f":CHANnel{ch}:INVert?",
    # label on/off and text
    "label":      lambda ch, state: f":CHANnel{ch}:LABel {state}",
    "label?":     lambda ch:        f":CHANnel{ch}:LABel?",
    "label_text": lambda ch, qstr:  f':CHANnel{ch}:LABel:TEXT "{qstr}"',
    "label_text?":lambda ch:        f":CHANnel{ch}:LABel:TEXT?",
    # skew, unit, switch, visible
    "skew":       lambda ch, v:     f":CHANnel{ch}:SKEW {v}",
    "skew?":      lambda ch:        f":CHANnel{ch}:SKEW?",
    "unit":       lambda ch, u:     f":CHANnel{ch}:UNIT {u}",
    "unit?":      lambda ch:        f":CHANnel{ch}:UNIT?",
    "switch":     lambda ch, s:     f":CHANnel{ch}:SWITch {s}",
    "switch?":    lambda ch:        f":CHANnel{ch}:SWITch?",
    "visible":    lambda ch, s:     f":CHANnel{ch}:VISible {s}",
    "visible?":   lambda ch:        f":CHANnel{ch}:VISible?",
}

ACQUIRE = {
    "amode":        lambda v:   f":ACQuire:AMODe {v}",
    "amode?":       lambda:      ":ACQuire:AMODe?",
    "csweep":       lambda:      ":ACQuire:CSWeep",
    "interpolation":lambda v:   f":ACQuire:INTerpolation {v}",
    "interpolation?":lambda:     ":ACQuire:INTerpolation?",
    "mmanagement":  lambda v:   f":ACQuire:MMANagement {v}",
    "mmanagement?": lambda:      ":ACQuire:MMANagement?",
    "mode":         lambda v:   f":ACQuire:MODE {v}",
    "mode?":        lambda:      ":ACQuire:MODE?",
    "mdepth":       lambda v:   f":ACQuire:MDEPth {v}",
    "mdepth?":      lambda:      ":ACQuire:MDEPth?",
    "numacq?":      lambda:      ":ACQuire:NUMAcq?",
    "points?":      lambda:      ":ACQuire:POINts?",
    "resolution":   lambda v:   f":ACQuire:RESolution {v}",
    "resolution?":  lambda:      ":ACQuire:RESolution?",
    "sequence":     lambda s:   f":ACQuire:SEQuence {s}",
    "sequence?":    lambda:      ":ACQuire:SEQuence?",
    "sequence_count":lambda v:  f":ACQuire:SEQuence:COUNt {v}",
    "sequence_count?":lambda:    ":ACQuire:SEQuence:COUNt?",
    "srate":        lambda v:   f":ACQuire:SRATe {v}",
    "srate?":       lambda:      ":ACQuire:SRATe?",
    "type":         lambda v:   f":ACQuire:TYPE {v}",
    "type?":        lambda:      ":ACQuire:TYPE?",
}

TRIGGER = {
    # Generic trigger controls and some common subsystems
    "mode":         lambda v:   f":TRIGger:MODE {v}",
    "mode?":        lambda:      ":TRIGger:MODE?",
    "level":        lambda ch, v: f":TRIGger:LEVEl{ch} {v}" if isinstance(ch, int) else f":TRIGger:LEVEl {v}",
    "level?":       lambda ch=None: f":TRIGger:LEVEl{ch}?" if ch is not None else ":TRIGger:LEVEl?",
    "edge_source":  lambda src: f":TRIGger:EDGE:SOURce {src}",
    "edge_source?": lambda:      ":TRIGger:EDGE:SOURce?",
    "edge_slope":   lambda s:   f":TRIGger:EDGE:SLOPe {s}",
    "edge_slope?":  lambda:      ":TRIGger:EDGE:SLOPe?",
    # example bus triggers (IIS shown in manual)
    "iis_wssource":     lambda v: f":TRIGger:IIS:WSSource {v}",
    "iis_wssource?":    lambda:    ":TRIGger:IIS:WSSource?",
    "iis_wsthreshold":  lambda v: f":TRIGger:IIS:WSThreshold {v}",
    "iis_wsthreshold?": lambda:    ":TRIGger:IIS:WSThreshold?",
    # Add other TRIGger sub-systems similarly (FREQuency, EDGE:IMPedance etc.)
}

WAVEFORM = {
    "data?":        lambda:      ":WAVeform:DATA?",
    "source":       lambda src:   f":WAVeform:SOURce {src}",
    "source?":      lambda:      ":WAVeform:SOURce?",
    "preamble?":    lambda:      ":WAVeform:PREamble?",
    "points?":      lambda:      ":WAVeform:POINt?",
    "start":        lambda v:     f":WAVeform:STARt {v}",
    "start?":       lambda:      ":WAVeform:STARt?",
    "interval":     lambda v:     f":WAVeform:INTerval {v}",
    "interval?":    lambda:      ":WAVeform:INTerval?",
    "width":        lambda v:     f":WAVeform:WIDTh {v}",
    "width?":       lambda:      ":WAVeform:WIDTh?",
    "maxpoint?":    lambda:      ":WAVeform:MAXPoint?",
    "sequence":     lambda v1, v2=None: f":WAVeform:SEQuence {v1}" + (f",{v2}" if v2 is not None else ""),
    "sequence?":    lambda:      ":WAVeform:SEQuence?",
}

CURSOR = {
    "on":           lambda s:     f":CURSor {s}",
    "on?":          lambda:      ":CURSor?",
    "mode":         lambda v:     f":CURSor:MODE {v}",
    "mode?":        lambda:      ":CURSor:MODE?",
    "x1":           lambda v:     f":CURSor:X1 {v}",
    "x1?":          lambda:      ":CURSor:X1?",
    "x2":           lambda v:     f":CURSor:X2 {v}",
    "x2?":          lambda:      ":CURSor:X2?",
    "y1":           lambda v:     f":CURSor:Y1 {v}",
    "y1?":          lambda:      ":CURSor:Y1?",
    "y2":           lambda v:     f":CURSor:Y2 {v}",
    "y2?":          lambda:      ":CURSor:Y2?",
    "xdelta?":      lambda:      ":CURSor:XDELta?",
    "ydelta?":      lambda:      ":CURSor:YDELta?",
    "mitem":        lambda typ, src1, src2=None: f":CURSor:MITem {typ},{src1}" + (f",{src2}" if src2 else ""),
    "mitem?":       lambda:      ":CURSor:MITem?",
}

DISPLAY = {
    "print?":       lambda imgtype: f":PRINt? {imgtype}",  # BMP|PNG
    "format_data":  lambda opt, d=None: f":FORMat:DATA {opt}" + (f",{d}" if d is not None else ""),
    "format_data?": lambda:      ":FORMat:DATA?",
    # other display commands exist (axis label settings etc.)
}

MEMORY = {
    "switch":       lambda n, s: f":MEMory{n}:SWITch {s}",
    "switch?":      lambda n:    f":MEMory{n}:SWITch?",
    "vertical_pos": lambda n, v: f":MEMory{n}:VERTical:POSition {v}",
    "vertical_pos?":lambda n:    f":MEMory{n}:VERTical:POSition?",
    "vertical_scale":lambda n, v:f":MEMory{n}:VERTical:SCALe {v}",
    "vertical_scale?":lambda n:  f":MEMory{n}:VERTical:SCALe?",
}

SYSTEM = {
    "autoset":      lambda:      ":AUToset",
    "reset":        lambda:      "*RST",
    "idn?":         lambda:      "*IDN?",
    "opc?":         lambda:      "*OPC?",
    "save_setup":   lambda path: f":SYSTem:... {path}",  # placeholder — see SAVE subsystem
    # Many SYSTem commands exist; add as needed
}

ROOT = {
    "autoset":      lambda:      ":AUToset",
    "print?":       lambda t:     f":PRINt? {t}",
    "format_data":  lambda opt,d=None: f":FORMat:DATA {opt}" + (f",{d}" if d else "")
}

MEASURE = {
    # measurement-related commands are numerous; include the basic pattern
    "measure_item": lambda spec: f":MEASure:ITEM {spec}",
    "measure?":     lambda:       ":MEASure:ITEM?",
    # advanced measurement commands follow same template style
}

SAVE = {
    "save_binary":  lambda path, src=None: f":SAVE:BINary {path}" + (f",{src}" if src else ""),
    "save_setup":   lambda path:  f":SAVE:SETup {path}",
    "save_default": lambda:       ":SAVE:DEFault",
    # MANY other save formats exist (PNG, BMP, CSV, MATLab, etc.)
}

RECALL = {
    "recall_setup": lambda path:  f":RECall:SETup {path}",
    "recall?":      lambda:       ":RECall:SETup?",
    "recall_default":lambda:      ":RECall:FDEFault",
}

FUNCTION = {
    # math functions, FFT, integration etc. templates
    "func_source":  lambda n, spec: f":FUNCtion{n}:... {spec}",
    # fill in specific function subcommands as needed
}

DIGITAL = {
    "srate?":       lambda:      ":DIGital:SRATe?",
    "skew":         lambda v:    f":DIGital:SKEW {v}",
    "skew?":        lambda:      ":DIGital:SKEW?",
    "threshold":    lambda n, t: f":DIGital:THReshold{n} {t}",
    "threshold?":   lambda n:    f":DIGital:THReshold{n}?",
    # other digital bus commands exist (DCLocks, DTrigger etc.)
}

DECODE = {
    # Bus decoding (I2C, SPI, CAN, LIN, 1553B, SENT, Manchester, etc.)
    "decode_on":    lambda typ, on: f":DECode:{typ} {on}",
    "decode?":      lambda typ:     f":DECode:{typ}?",
}

DVM = {
    "dvm_on":       lambda s:     f":DVM {s}",
    "dvm?":         lambda:       ":DVM?",
    # DVM has many measurement specifics; expand as needed
}

WGEN = {
    # Function generator (if present/license)
    "output":       lambda ch, s: f":WGEN:OUTPut{ch} {s}",
    "arbwave":      lambda name:  f":WGEN:ARbWaVe {name}",
    # WGEN follows SDG commands; see manual for full set
}

HISTORY = {
    "on":           lambda s:     f":HISTory {s}",
    "count?":       lambda:       ":HISTory:COUNt?",
}

REF = {
    "set":          lambda name, v: f":REF:{name} {v}",
    "get":          lambda name:    f":REF:{name}?",
}

MTEST = {
    # Built-in test functions
    "selftest?":    lambda:       ":MTESt:SELF?",
}

# Example dictionary grouping all the above so you can import a single object
SCPI = {
    "CHANNEL": CHANNEL,
    "ACQUIRE": ACQUIRE,
    "TRIGGER": TRIGGER,
    "WAVEFORM": WAVEFORM,
    "CURSOR": CURSOR,
    "DISPLAY": DISPLAY,
    "MEMORY": MEMORY,
    "SYSTEM": SYSTEM,
    "ROOT": ROOT,
    "MEASURE": MEASURE,
    "SAVE": SAVE,
    "RECALL": RECALL,
    "FUNCTION": FUNCTION,
    "DIGITAL": DIGITAL,
    "DECODE": DECODE,
    "DVM": DVM,
    "WGEN": WGEN,
    "HISTORY": HISTORY,
    "REF": REF,
    "MTEST": MTEST,
}
