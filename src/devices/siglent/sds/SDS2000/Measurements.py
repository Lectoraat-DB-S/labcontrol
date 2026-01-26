import pyvisa
from commands_full import SCPI

class SDS2kMeasurements(object):
    """Class for performing SDS2d built-in measurements.
     :MEASure
     :MEASure:ADVanced:LINenumber
     :MEASure:ADVanced:P<n>
     :MEASure:ADVanced:P<n>:SOURce1
     :MEASure:ADVanced:P<n>:SOURce2
     :MEASure:ADVanced:P<n>:STATistics
     :MEASure:ADVanced:P<n>:TYPE
     :MEASure:ADVanced:P<n>:VALue
     :MEASure:ADVanced:STATistics
     :MEASure:ADVanced:STATistics:HISTOGram
     :MEASure:ADVanced:STATistics:MAXCount
     :MEASure:ADVanced:STATistics:RESet
     :MEASure:ADVanced:STYLe
     :MEASure:GATE
     :MEASure:GATE:GA
     :MEASure:GATE:GB
     :MEASure:MODE
     :MEASure:SIMPle:ITEM
     :MEASure:SIMPle:SOURce
     :MEASure:SIMPle:VALue
    
    
    """
    
    def __init__(self, instr: pyvisa.resources.MessageBasedResource):
        self.visaInstr: pyvisa.resources.MessageBasedResource = instr

    def setMeasState(self, state: bool):
        "set state of measurement: on or off"
        mynewstate = "ON"
        if state or state == "ON" or state == "1":
            mynewstate = "ON"
        else:
            mynewstate = "OFF"
        self.visaInstr.write(SCPI["MEASURE"]["meas"](mynewstate))
    
    def getMeasState(self):
        """Gets the current measurement state
        TODO: find out if measurement is separate thing or is part of/driven by a channel"""
        return self.visaInstr.query(SCPI["MEASURE"]["meas?"]())

    def setMeasMode(self, mode):
        "Sets state of measurement mode: simple or advanded"
        measModeOptions = ["SIMPPLE", "simple", "ADVANCE", "advance", "SIMP", "simp", "ADV", "adv"]   
        if mode not in measModeOptions:
            return
        self.visaInstr.write(SCPI["MEASURE"]["measmode"](mode))
    
    def getMeasMode(self):
        """Get state of measurement mode: simple or advanded"""
        return self.visaInstr.query(SCPI["MEASURE"]["measmode?"]())


    def setNrOfMeasLines(self, newVal):
        """Sets the number of advanced measuredments to be displayed. param nemVal should be between 1-12"""
        if newVal > 0 and newVal < 13:
            self.visaInstr.write(SCPI["MEASURE"]["linenr"](newVal))
    
    def getNrOfMeasLines(self):
        """Gets the number of advanced measuredments to be displayed.
        TODO: find out if measurement is separate thing or is part of/driven by a channel"""
        return self.visaInstr.query(SCPI["MEASURE"]["linenr?"]())

    def setMeasItem(self, nr, state:bool):
        if nr < 1 or nr > 12:
            return
        mynewstate = "ON"
        if state or state == "ON" or state == "1":
            mynewstate = "ON"
        else:
            mynewstate = "OFF"
        self.visaInstr.write(SCPI["MEASURE"]["measitem"](nr)(mynewstate))

    def getMeasItem(self, nr):
        return self.visaInstr.query(SCPI["MEASURE"]["linenr?"](nr))
    
    def setMeasItemSrc1(self, nr, src:str):
        """Sets the source1 of the specified advanced measurement item.
        Parameters: nr = 1 to 12
                    src = {C<x>|Z<x>|F<x>|D<m>|ZD<m>|REFA|REFB|REFC|
                     C denotes an analog input channel.
                     Z denotes a zoomed input.
                     F denotes a math function.
                     D denotes a digital input channel.
                     ZD denotes a zoomed digital input channel.
                     REF denotes a reference wa veform.
                    <x>:= 1 to (# analog channels) in NR1 format, including an integer and no decimal point, like 1.
                    <m>:= 0 to (# digital channels 1) in NR1 format, including an integer and no decimal point, like 1.
                Note:
                • Z<x> and ZD<m> are optional only when Zo om is on.
                • The source can only be set to C<x> when the type is delay measurement.
        """
        srcOptions = ["C","X","F","D","ZD","REFA","REFB", "REFC"]
        numberedSrcOptions = ["C","X","F","D","ZD"]
        refSrcOptions = ["REFA","REFB", "REFC"]
        if nr < 1 or nr > 12:
            return
        if len(src)<2:
            return
        elif len(src) == 2:
            if src[1].isnumeric:
                if src[0] not in numberedSrcOptions:
                    return
            else: 
                return
        elif len(src) == 3:
            if src[1].isnumeric and src[2].isnumeric:
                if src[0] not in numberedSrcOptions:
                    return
            elif src[1].isalpha and src[2].isalpha:
                return
            else: # blijkbaar ZD
                if src[0:2] != "ZD":
                    return
        elif len(src) == 4:
            if src[1].isalpha and src[2].isalpha:
                return
            elif src[0:2] != "ZD":
                    return
            elif src[0:4] not in refSrcOptions:
                return
            else:
                return
        else: 
            return
        self.visaInstr.write(SCPI["MEASURE"]["measitemsrc1"](nr)(src))

    def getMeasItemSrc1(self, nr):
        """Gets the current source1 of the specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["measitemsrc1?"](nr))

    def setMeasItemSrc2(self, nr, src:str):
        """Sets the source2 of the specified advanced measurement item.
        Parameters: nr = 1 to 12
                    src = {C<x>|Z<x>|F<x>|D<m>|ZD<m>|REFA|REFB|REFC|
                     C denotes an analog input channel.
                     Z denotes a zoomed input.
                     F denotes a math function.
                     D denotes a digital input channel.
                     ZD denotes a zoomed digital input channel.
                     REF denotes a reference wa veform.
                    <x>:= 1 to (# analog channels) in NR1 format, including an integer and no decimal point, like 1.
                    <m>:= 0 to (# digital channels 1) in NR1 format, including an integer and no decimal point, like 1.
                Note:
                • Z<x> and ZD<m> are optional only when Zo om is on.
                • The source can only be set to C<x> when the type is delay measurement.
        """
        srcOptions = ["C","X","F","D","ZD","REFA","REFB", "REFC"]
        numberedSrcOptions = ["C","X","F","D","ZD"]
        refSrcOptions = ["REFA","REFB", "REFC"]
        if nr < 1 or nr > 12:
            return
        if len(src)<2:
            return
        elif len(src) == 2:
            if src[1].isnumeric:
                if src[0] not in numberedSrcOptions:
                    return
            else: 
                return
        elif len(src) == 3:
            if src[1].isnumeric and src[2].isnumeric:
                if src[0] not in numberedSrcOptions:
                    return
            elif src[1].isalpha and src[2].isalpha:
                return
            else: # blijkbaar ZD
                if src[0:2] != "ZD":
                    return
        elif len(src) == 4:
            if src[1].isalpha and src[2].isalpha:
                return
            elif src[0:2] != "ZD":
                    return
            elif src[0:4] not in refSrcOptions:
                return
            else:
                return
        else: 
            return
        self.visaInstr.write(SCPI["MEASURE"]["measitemsrc2"](nr)(src))

    def getMeasItemSrc2(self, nr):
        """Gets the current source1 of the specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["measitemsrc2?"](nr))
    
    def setMeasStat(self, status:bool):
        """The command sets the state of the measurement statistics.
        """
        mystatus = "ON" 
        if status or status == "ON" or status == "1":
            mystatus = "ON"
        else:
            mystatus = "OFF"
        self.visaInstr.write(SCPI["MEASURE"]["measstat"](mystatus))
        
    def getMeasStat(self):
        """Gets the current source1 of the specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["measstat?"]())

    def setMeasHisto(self, status:bool):
        """The command sets the state of the measurement statistics.
        """
        mystatus = "ON" 
        if status or status == "ON" or status == "1":
            mystatus = "ON"
        else:
            mystatus = "OFF"
        self.visaInstr.write(SCPI["MEASURE"]["meashisto"](mystatus))
        
    def getMeasHisto(self):
        """Gets the current source1 of the specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["meashisto?"]())
    
    def setMeasMaxCount(self, newCount):
        """The command sets the state of the measurement statistics.
        """
        if newCount <0 or newCount >1024:
            return
        self.visaInstr.write(SCPI["MEASURE"]["measmaxcnt"](newCount))
        
    def getMeasMaxCount(self):
        """Gets the current source1 of the specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["measmaxcnt?"]())

    def setMeasStyle(self, newStyle):
        """The command sets the state of the measurement statistics.
        """
        styleOptions = ["M1", "M2"]
        if newStyle not in styleOptions:
            return
        self.visaInstr.write(SCPI["MEASURE"]["measstyle"]())
        
    def getMeasStyle(self):
        """Gets the current source1 of the specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["measstyle?"]())
    
    def setMeasGate(self, newStatus):
        """This command sets the state of the measurement gate.
        <state>:= ON|OFF}
        """
        mystatus = "ON" 
        if newStatus or newStatus == "ON" or newStatus == "1":
            mystatus = "ON"
        else:
            mystatus = "OFF"
        self.visaInstr.write(SCPI["MEASURE"]["measgate"](mystatus))
        
    def getMeasGate(self):
        """This query returns the current position of gate A."""
        return self.visaInstr.query(SCPI["MEASURE"]["measgate?"]())

    def setMeasGateA(self, newGate):
        """This command sets the position of gate A.
        <value>:= Value in NR3 format, including a decimal point and exponent, like 1.23E+2. The range of the value 
        is [horizontal_grid/2*timebase, horizontal_grid/2*timebase].
        """
        #TODO: check range of the value newGate
        self.visaInstr.write(SCPI["MEASURE"]["measgatea"](newGate))
        
    def getMeasGateA(self):
        """This query returns the current position of gate A."""
        return self.visaInstr.query(SCPI["MEASURE"]["measgatea?"]())

    def setMeasGateB(self, newGate):
        """This command sets the position of gate B.
        <value>:= Value in NR3 format, including a decimal point and exponent, like 1.23E+2. The range of the value 
        is [horizontal_grid/2*timebase, horizontal_grid/2*timebase].
        """
        #TODO: check range of the value newGate
        self.visaInstr.write(SCPI["MEASURE"]["measgateb"](newGate))
        
    def getMeasGateB(self):
        """This query returns the current position of gate B."""
        return self.visaInstr.query(SCPI["MEASURE"]["measgateb?"]())


    def resetMeasStat(self):
        self.visaInstr.write(SCPI["MEASURE"]["measrststat"]())


    def setMeasItemStat(self, nr, typeStat):
        """<type>:={ALL|CURRent|MEAN|MAXimum|MINimum|STDev|COUNt}
        """
        if nr < 1 or nr > 12:
            return
        #TODO: check validity of type
        self.visaInstr.write(SCPI["MEASURE"]["measitemstat"](nr)(typeStat))
        
    def getMeasItemStat(self, nr):
        """Gets the current source1 of the specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["measitemsstat?"](nr))

    def setMeasItemType(self, nr, typeMeas):
        """<n>:= 1 to 12
            <parameter>:=
            {PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX CMEAN|MEAN|S
            TDEV | RMS|CRMS| MEDIAN|CMEDIAN| OVSN|FPRE|O
            VSP|RPRE|PER|FREQ| TMAX|TMIN|PWID|NWID|DUTY|NDU
            TY|WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE 1 0T 9 0|FALL 9
            0T 1 0|CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|REDGE
            S|FEDGES|EDGES|PPULSES|NPULSES|PHA|SKEW|FRR|F
            RF|FFR|FFF|LRR|LRF|LFR|LFF PACArea NACArea ACArea A
            BSACArea PSLOPE NSLOPE TSR TSF THR THF}
        """
        if nr < 1 or nr > 12:
            return
        #TODO: check validity of type
        self.visaInstr.write(SCPI["MEASURE"]["measitemtype"](nr)(typeMeas))
        
    def getMeasItemType(self, nr):
        """Gets the current source1 of the specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["measitemtype?"](nr))

    def getMeasItemVal(self, nr):
        """Gets the value of the current specified advanced measurement item."""
        return self.visaInstr.query(SCPI["MEASURE"]["measitemval?"](nr))
    
    
    def setSimpleMeasItem(self, item, status):
        """This command sets the type of simple measurement
        {PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX
        CMEAN|MEAN|STDEV | RMS|CRMS| MEDIAN|CMEDIAN| OVSN|FPRE|
        OVSP|RPRE|PER|FREQ| TMAX|TMIN|PWID|NWID|DUTY|NDUTY|
        WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE20T80|FALL80T20|
        CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|REDGES|
        FEDGES|EDGES|PPULSES |NPULSES|PACArea|NACArea
        ACArea|ABSACArea}
        """
        itemOptions = ["PKPK","MAX","MIN","AMPL","TOP","BASE","LEVELX",
                       "CMEAN","MEAN","STDEV","RMS","CRMS","MEDIAN","CMEDIAN","OVSN","FPRE","OVSP"
                       "RPRE","PER","FREQ","TMAX","TMIN","PWID","NWID","DUTY","NDUTY", "WID","NBWID",
                       "DELAY","TIMEL","RISE","FALL","RISE20T80","FALL80T20","CCJ","PAREA","NAREA","AREA","ABSAREA","CYCLES",
                       "REDGES","FEDGES","EDGES","PPULSES", "NPULSES","PACArea","NACArea","ACArea","ABSACArea"]
        if item not in itemOptions:
            return
        mystatus = "ON" 
        if status or status == "ON" or status == "1":
            mystatus = "ON"
        else:
            mystatus = "OFF"
        #TODO: check validity of type
        self.visaInstr.write(SCPI["MEASURE"]["meassimpleitem"](item)(mystatus))
        
    
    def setSimpleMeasSrc(self, newSrc, status):
        """ This command sets the source of the simple measurement.
            C< x >| x F<x>| D< m >| m >|REFA|REFB|REFC|
        """
        srcOptions = ["C", "F", "Z", "D", "ZD", "REFA", "REFB", "REFC", "REFD"]
        if newSrc not in srcOptions:
            return
           
        self.visaInstr.write(SCPI["MEASURE"]["meassimplesrc"](newSrc))

    def getSimpleMeasSrc(self):
        """This query returns the current position of gate B."""
        return self.visaInstr.query(SCPI["MEASURE"]["meassimplesrc?"]())

    def getSimpleMeasSrc(self, item):
        """This query returns the specified measurement value that appears on the simple measurement.
        {PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX
        CMEAN|MEAN|STDEV | RMS|CRMS| MEDIAN|CMEDIAN| OVSN|FPRE|
        OVSP|RPRE|PER|FREQ| TMAX|TMIN|PWID|NWID|DUTY|NDUTY|
        WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE20T80|FALL80T20|
        CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|REDGES|
        FEDGES|EDGES|PPULSES |NPULSES|PACArea|NACArea
        ACArea|ABSACArea}
        """
        itemOptions = ["PKPK","MAX","MIN","AMPL","TOP","BASE","LEVELX",
                       "CMEAN","MEAN","STDEV","RMS","CRMS","MEDIAN","CMEDIAN","OVSN","FPRE","OVSP"
                       "RPRE","PER","FREQ","TMAX","TMIN","PWID","NWID","DUTY","NDUTY", "WID","NBWID",
                       "DELAY","TIMEL","RISE","FALL","RISE20T80","FALL80T20","CCJ","PAREA","NAREA","AREA","ABSAREA","CYCLES",
                       "REDGES","FEDGES","EDGES","PPULSES", "NPULSES","PACArea","NACArea","ACArea","ABSACArea"]
        if item not in itemOptions:
            return
        return self.visaInstr.query(SCPI["MEASURE"]["meassimpleval?"](item))
    
    def setThresholdSrc(self, src):
        """This command sets the measurement threshold source.
        """
        #check src value validity
        self.visaInstr.write(SCPI["MEASURE"]["measthresholdsrc"](src))
        
    def getThresholdSrc(self):
        """This query gets the current measurement threshold source."""
        return self.visaInstr.query(SCPI["MEASURE"]["measthresholdsrc?"]())
    
    
    def setThresholdType(self, thrtype):
        """This command sets the measurement threshold type.
        Parameter thrtype : {PERCent|ABSolute}"""
        thrTypeOptions = ["PERCent","ABSolute","percent", "PERCENT","absolute", "ABSOLUTE"]
        thrPercOptions = ["PERCent","percent", "PERCENT"]
        thrAbsOptions = ["ABSolute","absolute", "ABSOLUTE"]
        
        if thrtype not in thrTypeOptions:
            return
        myType = ""
        if thrtype in thrPercOptions:
            myType = "PERCent"
        elif thrtype in thrAbsOptions:
            myType = "ABSolute"
        self.visaInstr.write(SCPI["MEASURE"]["measthresholdtype"](myType))
        
    def getThresholdType(self):
        """This query gets the current measurement threshold source."""
        return self.visaInstr.query(SCPI["MEASURE"]["measthresholdtype?"]())
    
    def setAbsThreshold(self, low, mid, high):
        """This command specifies the reference level when :MEASure:THReshold:TYPE is set to ABSolute.This 
        command affects the results of some measurements."""
        
        self.visaInstr.write(SCPI["MEASURE"]["measabsthr"](high)(mid)(low))
        
    def getAbsThreshold(self):
        """This query returns the reference level of the source"""
        return self.visaInstr.query(SCPI["MEASURE"]["measabsthr?"]())
    
    def setPercThreshold(self, low, mid, high):
        """This command specifies the reference level when :MEASure:THReshold:TYPE is set to ABSolute.This 
        command affects the results of some measurements."""
        
        self.visaInstr.write(SCPI["MEASURE"]["measabsthr"](high)(mid)(low))
        
    def getPercThreshold(self):
        """This query returns the reference level of the source"""
        return self.visaInstr.query(SCPI["MEASURE"]["measabsthr?"]())
    
    
