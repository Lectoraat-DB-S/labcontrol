

CHANNEL = {
    # reference strategy
    "reference":        [],
    "reference?":       [],
    # per-channel commands (use ch(n) or integer)
    "scale":            [],
    "scale?":           [],
    "offset":           [],
    "offset?":          [],
    "probe":            [],
    "probe?":           [],
    "coupling":         [],
    "coupling?":        [],
    "bwlimit":          [],
    "bwlimit?":         [],
    #Zie onderstaande. Is een eerst idee om verschillende twee opties zo te structureren dat je verschlllende schrijfwijzen
    #kunt toestaan. Het nadeel van een list in een list is dat Python niet op eenvoudige (ingebouwde) wijze
    # kan aangeven of een list enkel- of multidimensionaal is. Misschien ander datastruct?
    "impedance":        [["ONEMeg","1M", 1e6],["FIFTy",50]], #index 0 heeft altijd de juist SCPI schrijfwijze.
    "impedance?":       [],
    "invert":           [],
    "invert?":          [],
    "label":            [],
    "label?":           [],
    "label_text":       [],
    "label_text?":      [],
    "skew":             [],
    "skew?":            [],
    "unit":             [],
    "unit?":            [],
    "switch":           [],
    "switch?":          [],
    "visible":          [],
    "visible?":         [],
}

MEASURE = {
    "meas?":            lambda:            ":MEASure:?",
    "meas":             lambda state:      f":MEASure: {state}",
    
    "measmode":             lambda mode:      f":MEASure:MODE {mode}",
    "measmode?":            lambda:            ":MEASure:MODE?",

    "measstat":           lambda status:     f":MEASure:ADVanced:STATistics {status}",
    "measstat?":          lambda:            ":MEASure:ADVanced:STATistics?",
    
    "meashisto":           lambda status:     f":MEASure:ADVanced:STATistics:HISTOGram {status}",
    "meashisto?":          lambda:            ":MEASure:ADVanced:STATistics:HISTOGram?",
    "measmaxcnt":           lambda status:     f":MEASure:ADVanced:STATistics:MAXCount {status}",
    "measmaxcnt?":          lambda:            ":MEASure:ADVanced:STATistics:MAXCount?",
  
    "measrststat":          lambda:            ":MEASure:ADVanced:STATistics:RESet",

    "measstyle":           lambda style:     f":MEASure:ADVanced:STYLe {style}",
    "measstyle?":          lambda:            ":MEASure:ADVanced:STYLe?",
    
    "measgate":           lambda status:     f":MEASure:GATE {status}",
    "measgate?":          lambda:            ":MEASure:GATE?",
    "measgatea":           lambda gate:     f":MEASure:GATE:GA {gate}",
    "measgatea?":          lambda:            ":MEASure:GATE:GA?",
    "measgateb":           lambda gate:     f":MEASure:GATE:GB {gate}",
    "measgateb?":          lambda:            ":MEASure:GATE:GB?",
    

    "linenr":           lambda linenr:     f":MEASure:ADVanced:LINenumber {linenr}",
    "linenr?":          lambda:            ":MEASure:ADVanced:LINenumber?",
    "measitem":         lambda nr, state:  f":MEASure:ADVanced:P{nr} {state}",
    "measitem?":        lambda nr:         f":MEASure:ADVanced:P{nr}?",
 
    "meassimpleitem":         lambda item, state:  f":MEASure: SIMPle:ITEM {item},{state}",
     
    "measitemsrc1":     lambda nr, src:    f":MEASure:ADVanced:P{nr}:SOURce1 {src}",
    "measitemsrc1?":    lambda nr:         f":MEASure:ADVanced:P{nr}:SOURce1?",
    "measitemsrc2":     lambda nr, src:    f":MEASure:ADVanced:P{nr}:SOURce2 {src}",
    "measitemsrc2?":    lambda nr:         f":MEASure:ADVanced:P{nr}:SOURce2?",

    
    "meassimplesrc":           lambda linenr:     f":MEASure:SIMPle:SOURce {linenr}",
    "meassimplesrc?":          lambda:            ":MEASure:ADVanced:LINenumber?",
    
    "meassimpleval?":    ["PKPK","MAX","MIN","AMPL","TOP","BASE","LEVELX",
                       "CMEAN","MEAN","STDEV","RMS","CRMS","MEDIAN","CMEDIAN","OVSN","FPRE","OVSP"
                       "RPRE","PER","FREQ","TMAX","TMIN","PWID","NWID","DUTY","NDUTY", "WID","NBWID",
                       "DELAY","TIMEL","RISE","FALL","RISE20T80","FALL80T20","CCJ","PAREA","NAREA","AREA","ABSAREA","CYCLES",
                       "REDGES","FEDGES","EDGES","PPULSES", "NPULSES","PACArea","NACArea","ACArea","ABSACArea"],
    
    "measitemstat":     lambda nr, typestat:    f":MEASure:ADVanced:P{nr}:STATistics {typestat}",
    "measitemstat?":    lambda nr:              f":MEASure:ADVanced:P{nr}:STATistics?",
    
    "measitemtype":     lambda nr, mtype:  f":MEASure:ADVanced:P{nr}:TYPE {mtype}",
    "measitemtype?":    lambda nr:         f":MEASure:ADVanced:P{nr}:TYPE?",
    
    "measitemval?":    lambda nr:         f":MEASure:ADVanced:P{nr}:VALue?",
    
    "item":             lambda spec:       f":MEASure:ITEM {spec}",
    "item?":            lambda:            ":MEASure:ITEM?",
    "auto?":            lambda:            ":MEASure:AUTOn?",
    "list":             lambda:            ":MEASure:LIST?",

    "measthresholdsrc":     lambda src:      f":MEASure:THReshold:SOURce {src}",
    "measthresholdsrc?":    lambda:         f":MEASure:THReshold:SOURce?",

    "measthresholdtype":     lambda thrtype:      f":MEASure:THReshold:TYPE {thrtype}",
    "measthresholtype?":    lambda:         ":MEASure:THReshold:TYPE?",

    "measabsthr":     lambda high, mid, low:      f":MEASure:THReshold:ABSolute {high},{mid},{low}",
    "measabsthr?":    lambda:         ":MEASure:THReshold:ABSolute?",

    "measpercthr":     lambda high, mid, low:      f":MEASure:THReshold:PERCent {high},{mid},{low}",
    "measpercthr?":    lambda:         ":MEASure:THReshold:PERCent?",

    # advanced measure items exist (PSLOPE, NSLOPE, TSR etc in E11C/E11D)
}

"""
TRIGGER

trigger type : ["EDGE", "PULSE","SLOPe","INTerval","PATTern","WINDow","DROPout","VIDeo","QUALified",
                          "NTHEdge","DELay","SETup","hold","IIC","SPI","UART","LIN","CAN","FLEXray","CANFd",
                          "IIS","1553B","SENT"]

"""
#EDGE trigger subsubsystem
EDGE = {
    "level":        [],
    "level?":       [],
    "coupling":     [ "DC","AC","LFREJect","HFREJect"],
    "coupling?":    [],
    "events":       [],
    "events?":      [],
    
    "hldtime":      [],
    "hldtime?":     [],

    "hldtype":      [ "OFF","EVENts","TIME"],
    "hldtype?":     [],
    
    "hldstart":     ["LAST_TRIG","ACQ_START"],
    "hldstart?":    [],
    
    "impedance":    [],
    "impedance?":   [],
    
    "noise":        [],
    "noise?":       [],
    
    "source":       [],
    "source?":      [],
    "slope":        [],
    "slope?":       [],
}


TRIGGER = {
    "run":              [],
    "stop":             [],
    "type":             ["EDGE", "PULSE","SLOPe","INTerval","PATTern","WINDow","DROPout","VIDeo","QUALified",
                          "NTHEdge","DELay","SETup","hold","IIC","SPI","UART","LIN","CAN","FLEXray","CANFd",
                          "IIS","1553B","SENT"],
    
    "mode":             [],
    "mode?":            [],
    # frequency trigger (added in E11D)
    "freq":             [],
    "freq?":            [],
    "status?":          [],
    "EDGE": EDGE,    
    #"SLOPE":SLOPE,
    #"PULSE":PULSE,
    #"INTERVAL":INTERVAL,
    #"DROPOUT":DROPOUT,
    #"RUNT":RUNT,
    #"WINDOW":WINDOW,
    #"PATTERN":PATTERN,    
    #"DELAY":DELAY,
    #"NEDGE":NEDGE,            
    # add generic bus trigger factory
    "bus":  lambda b,cmd,*args: f":TRIGger:{b}:{cmd} " + ",".join(map(str,args)) if args else f":TRIGger:{b}:{cmd}"
}

PARAM = {
    "CHANNEL": CHANNEL,
#    "ACQUIRE": ACQUIRE,
    "TRIGGER": TRIGGER,
#    "WAVEFORM": WAVEFORM,
#    "CURSOR": CURSOR,
#    "DISPLAY": DISPLAY,
#    "SAVE": SAVE,
#    "RECALL": RECALL,
#    "SYSTEM": SYSTEM,
#    "DIGITAL": DIGITAL,
#    "DECODE": DECODE,
    "MEASURE": MEASURE,
#    "FUNCTION": FUNCTION,
#    "DVM": DVM,
#    "WGEN": WGEN,
#    "HISTORY": HISTORY,
#    "MEMORY": MEMORY,
#    "MTEST": MTEST,
#    "REF": REF,
#    "ROOT": ROOT,
}
