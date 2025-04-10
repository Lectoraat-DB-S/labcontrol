
#GPIB commands
"""
*CLS
*ESE <Value>
*ESR
*IDN
*OPC
*RST
*SRE 
*STB?
*TRG 
*TST?
*WAI 
"""

#system commands
"""
FETCh?]
READ?
SYSTem:BEEPer:STATe <State>
SYSTem:BEEPer:STATe?
SYSTem:BEEPer[:IMMediate]
SYSTem:ERRor[:NEXT]
SYSTem:LOCal
SYSTem:REMoteSYSTem:RWLock
SYSTem
"""

#Trigger commands
"""
TRIGger:COUNt {<Count>|MIN|MAX|DEFault}
TRIGger:COUNt? [MINimum|MAXimum]
TRIGger:INTerval {<Seconds>|MIN|MAX|DEF}
TRIGger:INTerval? [{MIN|MAX}]
TRIGger:LEVel {<Level>|MIN|MAX|DEF}
TRIGger:LEVel? [{MIN|MAX}]
TRIGger:LEVel:MODe {CONTinue | ABOVe|BELow}
TRIGger:LEVel:MODe
TRIGger:MODE {<Mode>}
TRIGger:MODE?
"""

#Measurement commands
"""
MEASure:CAPacitance? [{<Range>|AUTO|MIN|MAX|DEF}]....................................... 28
MEASure:CONTinuity?................................................................................................ 29
MEASure:CURRent:AC? [{<Range>|AUTO|MIN|MAX|DEF}]...................................... 29
MEASure:CURRent:DC? [{<Range>|AUTO|MIN|MAX|DEF}]...................................... 29
MEASure:DIODe?....................................................................................................... 30
MEASure:FREQuency[:VOLTAGE]? [{<Range>|AUTO|MIN|MAX|DEF}]..................... 30
MEASure:FREQuency:CURRent [{<Range>|AUTO|MIN|MAX|DEF}].......................... 30
MEASure:FRESistance? [{<Range>|AUTO|MIN|MAX|DEF}]....................................... 31
MEASure:RESistance? [{<Range>|AUTO|MIN|MAX|DEF}]......................................... 31
MEASure:TEMPerature? [{<Probe_Type>|DEF}[,{<Type>|DEF}]................................. 31
MEASure[:VOLTage]:AC? [{<Range>|AUTO|MIN|MAX|DEF}]..................................... 32
MEASure[:VOLTage][:DC]? [{<Range>|AUTO|MIN|MAX|DEF}]...................................
"""

#Capacitance configuration commands
"""
CONFigure:CAPacitance [{<Range>|AUTO|MIN|MAX|DEF}]...................................... 33
[SENSe:]CAPacitance:NULL[:STATe] {ON|OFF}........................................................... 33
[SENSe:]CAPacitance:NULL[:STATe]?......................................................................... 33
[SENSe:]CAPacitance:NULL:VALue {<Value>|MIN|MAX}........................................... 34
[SENSe:]CAPacitance:NULL:VALue? [{MIN|MAX}]..................................................... 34
[SENSe:]CAPacitance:RANGe:AUTO <Mode>...........................................................34
[SENSe:]CAPacitance:RANGe:AUTO?........................................................................ 34
[SENSe:]CAPacitance:RANGe[:UPPer] {<Range>|MIN|MAX|DEF}............................. 34
[SENSe:]CAPacitance:RANGe[:UPPer]? [{MIN|MAX|DEF}].........................................
"""
#Continuity configuration commands
"""
CONFigure:CONTinuity............................................................................................... 35
[SENSe:]CONTinuity:THReshold {<Threshold>|MIN|MAX|DEF}.................................. 35
[SENSe:]CONTinuity:THReshold? [{MIN|MAX|DEF}]................................................... 35
[SENSe:]CONTinuity:BEEPer[:STATe] {ON|OFF}.......................................................... 36
[SENSe:]CONTinuity:BEEPer[:STATe]?...........
"""

#AC I configuration commands
"""
CONFigure:CURRent:AC [{<Range>|AUTO|MIN|MAX|DEF}]...................................... 36
[SENSe:]CURRent:AC:BANDwidth {<Threshold>|MIN|MAX|DEF}............................. 37
[SENSe:]CURRent:AC:BANDwidth? [{MIN|MAX}]...................................................... 37
[SENSe:]CURRent:AC:NULL[:STATe] {ON|OFF}.......................................................... 37
[SENSe:]CURRent:AC:NULL[:STATe]?........................................................................ 37
[SENSe:]CURRent:AC:NULL:VALue {<Value>|MIN|MAX}.......................................... 38
[SENSe:]CURRent:AC:NULL:VALue? [{MIN|MAX}]..................................................... 38
[SENSe:]CURRent:AC:RANGe:AUTO <Mode>..........................................................38
[SENSe:]CURRent:AC:RANGe:AUTO?....................................................................... 38
[SENSe:]CURRent:AC:RANGe[:UPPer] {<Range>|MIN|MAX|DEF}............................. 38
[SENSe:]CURRent:AC:RANGe[:UPPer]? [{MIN|MAX}]..........................
"""

#AC V configuration commands
"""
CONFigure[:VOLTage]:AC [{<Range>|AUTO|MIN|MAX|DEF}].................................... 39
[SENSe:]VOLTage:AC:BANDwidth {<Filter>|MIN|MAX|DEF}...................................... 39
[SENSe:]VOLTage:AC:BANDwidth? [{MIN|MAX}]....................................................... 40
[SENSe:]VOLTage:AC:NULL[:STATe] {ON|OFF}........................................................... 40
[SENSe:]VOLTage:AC:NULL[:STATe]?......................................................................... 40
[SENSe:]VOLTage:AC:NULL:VALue {<Value>|MIN|MAX}........................................... 40
[SENSe:]VOLTage:AC:NULL:VALue? [{MIN|MAX}]...................................................... 40
[SENSe:]VOLTage:AC:RANGe:AUTO <Mode>........................................................... 41
[SENSe:]VOLTage:AC:RANGe:AUTO?........................................................................ 41
[SENSe:]VOLTage:AC:RANGe[:UPPer] {<Range>|MIN|MAX|DEF}.............................. 41
[SENSe:]VOLTage:AC:RANGe[:UPPer]? [{MIN|MAX}].................................................
"""

#DC I configuration commands
"""
CONFigure:CURRent[:DC] [{<Range>|AUTO|MIN|MAX|DEF}]................................... 42
[SENSe:]CURRent[:DC]:NULL[:STATe] {ON|OFF}........................................................ 42
[SENSe:]CURRent[:DC]:NULL[:STATe]?...................................................................... 42
[SENSe:]CURRent[:DC]:NULL:VALue {<Value>|MIN|MAX}........................................ 43
[SENSe:]CURRent[:DC]:NULL:VALue? [{MIN|MAX}]................................................... 43
[SENSe:]CURRent[:DC]:RANGe:AUTO <Mode>........................................................43
[SENSe:]CURRent[:DC]:RANGe:AUTO?..................................................................... 43
[SENSe:]CURRent[:DC]:RANGe[:UPPer] {<Range>|MIN|MAX|DEF}.......................... 43
[SENSe:]CURRent[:DC]:RANGe[:UPPer]? [{MIN|MAX}]..............................................
"""

#DC V configuration commands
"""
CONFigure[:VOLTage][:DC] [{<Range>|AUTO|MIN|MAX|DEF}].................................. 44
[SENSe:]VOLTage[:DC]:NULL[:STATe] {ON|OFF}......................................................... 44
[SENSe:]VOLTage[:DC]:NULL[:STATe]?....................................................................... 45
[SENSe:]VOLTage[:DC]:NULL:VALue {<Value>|MIN|MAX}......................................... 45
[SENSe:]VOLTage[:DC]:NULL:VALue? [{MIN|MAX}]................................................... 45
[SENSe:]VOLTage[:DC]:RANGe:AUTO <Mode>.........................................................45
[SENSe:]VOLTage[:DC]:RANGe:AUTO?...................................................................... 45
[SENSe:]VOLTage[:DC]:RANGe[:UPPer] {<Range>|MIN|MAX|DEF}........................... 46
[SENSe:]VOLTage[:DC]:RANGe[:UPPer]? [{MIN|MAX}]............................................... 46
[SENSe:]VOLTage[:DC]:ZERO:AUTO <Mode>...........................................................46
[SENSe:]VOLTage[:DC]:ZERO:AUTO?......................................................................... 4
"""

#Diode configuration commands
"""
CONFigure:DIODe...................................................................................................... 47
[SENSe:]DIODe:THReshold {<Threshold>|MIN|MAX|DEF}......................................... 47
[SENSe:]DIODe:THReshold? [{MIN|MAX|DEF}].......................................................... 47
[SENSe:]DIODe:BEEPer[:STATe] {ON|OFF}................................................................. 47
[SENSe:]DIODe:BEEPer[:STATe]?............................................................................... 48"
"""

#Frequency configuration commands
"""
CONFigure:FREQuency[:VOLTAGE]........................................................................... 48
CONFigure:FREQuency:CURRent.............................................................................. 48
[SENSe:]FREQuency:APERture {<Seconds>|MIN|MAX|DEF}.................................... 48
[SENSe:]FREQuency:APERture? [{MIN|MAX}]............................................................ 49
[SENSe:]FREQuency:CURRent:RANGe:AUTO <Mode>............................................49
[SENSe:]FREQuency:CURRent:RANGe:AUTO?......................................................... 49
[SENSe:]FREQuency:CURRent:RANGe[:UPPer] {<Current_Range>|MIN|MAX|DEF}.49
[SENSe:]FREQuency:CURRent:RANGe[:UPPer]? [{MIN|MAX}].................................. 49
[SENSe:]FREQuency:VOLTage:RANGe:AUTO <Mode>.............................................50
[SENSe:]FREQuency:VOLTage:RANGe:AUTO?.......................................................... 50
[SENSe:]FREQuency:VOLTage:RANGe[:UPPer] {<Voltlage_Range>|MIN|MAX|DEF}.50
[SENSe:]FREQuency:VOLTage:RANGe[:UPPer]? [{MIN|MAX}]................................... 50
"""

#4-wire resistance configuration commands
"""
CONFigure:FRESistance [{<Range>|AUTO|MIN|MAX|DEF}]...................................... 51
[SENSe:]FRESistance:NULL[:STATe] {ON|OFF}........................................................... 51
[SENSe:]FRESistance:NULL[:STATe]?......................................................................... 51
[SENSe:]FRESistance:NULL:VALue {<Value>|MIN|MAX}........................................... 52
[SENSe:]FRESistance:NULL:VALue? [{MIN|MAX}]..................................................... 52
[SENSe:]FRESistance:RANGe:AUTO <Mode>...........................................................52
[SENSe:]FRESistance:RANGe:AUTO?........................................................................ 52
[SENSe:]FRESistance:RANGe[:UPPer] {<Range>|MIN|MAX|DEF}............................. 52
[SENSe:]FRESistance:RANGe[:UPPer]? [{MIN|MAX}]................................................. 53
"""
#2-wire resistance configuration commands
"""
CONFigure:RESistance [{<Range>|AUTO|MIN|MAX|DEF}]........................................ 53
[SENSe:]RESistance:NULL[:STATe] {ON|OFF}............................................................. 53
[SENSe:]RESistance:NULL[:STATe]?........................................................................... 54
[SENSe:]RESistance:NULL:VALue {<Value>|MIN|MAX}............................................. 54
[SENSe:]RESistance:NULL:VALue? [{MIN|MAX}]....................................................... 54
[SENSe:]RESistance:RANGe:AUTO <Mode>.............................................................54
[SENSe:]RESistance:RANGe:AUTO?.......................................................................... 54
[SENSe:]RESistance:RANGe[:UPPer] {<Range>|MIN|MAX|DEF}............................... 55
[SENSe:]RESistance:RANGe[:UPPer]? [{MIN|MAX}]................................................... 55
"""

#Temperature configuration commands
"""
CONFigure:TEMPerature [{<Probe_Type>|DEF}[,{<Type>|DEF}[,1]............................ 55
[SENSe:]TEMPerature:NULL[:STATe] {ON|OFF}.......................................................... 56
[SENSe:]TEMPerature:NULL[:STATe]?........................................................................ 56
[SENSe:]TEMPerature:NULL:VALue {<Value>|MIN|MAX}.......................................... 56
[SENSe:]TEMPerature:NULL:VALue? [{MIN|MAX}].................................................... 56
[SENSe:]TEMPerature:TRANsducer:RTD:TYPE <Type>.............................................56
[SENSe:]TEMPerature:TRANsducer:RTD:TYPE?........................................................ 57
[SENSe:]TEMPerature:TRANsducer:TYPE <Probe_Type>.........................................57
[SENSe:]TEMPerature:TRANsducer:TYPE?................................................................ 57
UNIT:TEMPerature {C | K | F}....................................................................................... 57
UNIT:TEMPerature?.................................................................................................... 57
"""

#ADC rate configuration commands
"""
[SENSe:]ADCRate {SLOW | MEDium | FAST}............................................................. 58
[SENSe:]ADCRate?..................................................................................................... 58"
"""

#Miscellaneous
"""
CONFigure?................................................................................................................ 58
[SENSe:]FUNCtion[:ON] <Function>..........................................................................58
[SENSe:]FUNCtion[:ON]?............................................................................................ 59
"""

#Mathematic Functions
"""
CALCulate:FUNCtion {NULL | DB | DBM | AVERage | LIMit | POWer}........................ 59
CALCulate:FUNCtion?................................................................................................. 60
CALCulate[:STATe] {OFF | ON}.................................................................................... 60
CALCulate[:STATe]?.................................................................................................... 60
CALCulate:POWer?.................................................................................................... 60
CALCulate:LIMit:LOWer {<Value> | MINimum | MAXimum}...................................... 61
CALCulate:LIMit:LOWer? {MINimum | MAXimum}.................................................... 61
CALCulate:LIMit:UPPer {<Value> | MINimum | MAXimum}....................................... 61
CALCulate:LIMit:UPPer? {MINimum | MAXimum}..................................................... 61
CALCulate:DB:REFerence {<Value> | MINimum | MAXimum}................................... 61
CALCulate:DB:REFerence? {MINimum | MAXimum}................................................. 61
CALCulate:DBM:REFerence {<Value> | MINimum | MAXimum}................................ 61
CALCulate:DBM:REFerence? {MINimum | MAXimum}.............................................. 62
CALCulate:NULL:OFFSet {<Value> | MINimum | MAXimum}.................................... 62
CALCulate:NULL:OFFSet? {MINimum | MAXimum}................................................... 62
CALCulate:AVERage:AVERage?.................................................................................. 62
CALCulate:AVERage:CLEar......................................................................................... 62
CALCulate:AVERage:COUNt?..................................................................................... 62
CALCulate:AVERage:MAXimum?............................................................................... 62
CALCulate:AVERage:MINimum?................................................................................ 63
CALCulate:AVERage:PTPeak?.................................................................................... 63
CALCulate:AVERage:SDEViation?............................................................................... 63
"""

#Data and File Management
"""
DATA:LOG[:STATe] {0 | 1 | OFF | ON}.......................................................................... 64
DATA:LOG[:STATe]?.................................................................................................... 64
DATA:LOG:FNAMe {<“File_Name“>},[{INT | EXT | DEF}]........................................... 64
DATA:LOG:FNAMe?................................................................................................... 64
DATA:LOG:FORMat {CSV | TXT}................................................................................. 64
DATA:LOG:FORMat?.................................................................................................. 64
DATA:LOG:MODE {UNLimited | COUNt | TIME}......................................................... 65
DATA:LOG:MODE?..................................................................................................... 65
DATA:LOG:TIME <time in seconds>..........................................................................65
DATA:LOG:TIME?....................................................................................................... 65
DATA:LOG:COUNt <no of samples>..........................................................................65
DATA:LOG:COUNt?.................................................................................................... 65
DATA:LOG:INTerval <interval in seconds>.................................................................65
DATA:LOG:INTerval?................................................................................................... 66
DATA:DATA? {<“File_Name“>},[{INT| EXT | DEF}]...................................................... 66
DATA:DELete {<“File_Name“>},[{INT | EXT | DEF}]................................................... 66
DATA:POINts? {<“File_Name“>},[{INT | EXT | DEF}]................................................... 67
DATA:LIST? [{INT | EXT | DEF}].................................................................................... 67
HCOPy:DATA?............................................................................................................ 67
HCOPy:FORMat { BMP | PNG }.................................................................................. 67
HCOPy:FORMat?........................................................................................................ 68
HCOPy:SIZE:X?........................................................................................................... 68
HCOPy:SIZE:Y?........................................................................................................... 68
*SAV {0|1|2|3|4}........................................................................................................... 68
*RCL {0|1|2|3|4}........................................................................................................... 68

"""

#Status reporting
"""
STATus:OPERation:CONDition? ................................................................................. 69
STATus:OPERation:ENABle <Enable_Value> ............................................................. 69
STATus:OPERation:ENABle?....................................................................................... 69
STATus:OPERation[:EVENt]? ...................................................................................... 69
STATus:PRESet .......................................................................................................... 70
STATus:QUEStionable:CONDition? ............................................................................ 70
STATus:QUEStionable:ENABle <Enable_Value> ........................................................ 70
STATus:QUEStionable:ENABle?.................................................................................. 70
STATus:QUEStionable[:EVENt]? ................................................................................. 71
"""