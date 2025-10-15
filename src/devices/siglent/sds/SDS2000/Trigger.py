import pyvisa
from devices.BaseScope import BaseTriggerUnit
from devices.tektronix.scope.Vertical import TekVertical, TekChannel
from devices.siglent.sds.SDS1000.Vertical import SDSVertical, SDSChannel

class SDSTrigger(BaseTriggerUnit):

    TRIG_COUPLING_OPTIONS = ("AC","DC","HFREJ","LFREJ")
    TRIG_SLOPE_OPTIONS = ( "NEG", "POS", "WINDOW")
    TRIG_MODE_OPTIONS = ("AUTO", "NORM", "SINGLE", "STOP")
    TRIG_HOLDTYPE_OPTIONS = ("TI","PS","PL","P2","IS","IL","I2","OFF","EV")
    TRIG_TYPE_OPTIONS = ("EDGE", "GLIT","SLEW", "INTV")
    TRIG_SRC_OPTIONS = ("C1", "C2", "C3", "C4", "LINE","EX","EX5")

    @classmethod
    def getTriggerUnitObject(cls, vertical, dev):
        """ Tries to get (instantiate) the correct object."""
        if cls is SDSTrigger:
            cls.__init__(cls, vertical, dev)
            return cls
        else:
            return None      
    
    def __init__(self, vertical: SDSVertical = None, dev: pyvisa.resources.MessageBasedResource=None):
        self.vertical = vertical
        self.source = 1
        self.visaInstr = dev
        self.type = None
        self.holdType = None
        self.holdValue = None
        #self.setSource(1)  #dit gaat niet goed.
        #self.auto()

    def getCurrSettings(self):
        resp = self.query("TRSE?")
        # See page 132 of SDS programming manual: 
        # Response format will be structurized like this
        # TRig_Select <trig_type>, SR, <source>, HT, <hold_type>, HV, <hold_value>
        splittedResp =  resp.split(",")
        if len(splittedResp) != 7:
            #error
            return None
        trigType = splittedResp[0].split()
        self.type = trigType[1].strip()
        self.source = splittedResp[2].strip()
        self.source = self.source.removeprefix("C")
        self.source = int(self.source)

        self.holdType = splittedResp[4].strip()
        self.holdValue = splittedResp[6].strip()
    def query(self, cmd: str):
        return self.visaInstr.query(cmd)
    
    def write(self, cmd: str):
        self.visaInstr.write(cmd)

    def getChannel(self, chanNr):
        chans = self.vertical.channels
        theChan : SDSChannel = None
        for  i, val in enumerate(chans):
                if (chanNr) in val.keys():
                    theChan = val[chanNr]
        
        return theChan
    
    def getCurrSrcChannel(self):
        return self.getChannel(self.source)
    
    def setSource(self, chanNr):
        """Sets his trigger source channel."""
        chans = self.vertical.channels
        theChan : SDSChannel = None
        for  i, val in enumerate(chans):
                if (chanNr) in val.keys():
                    theChan = val[chanNr]
        
        if theChan!=None:
            self.write(f"TRSE EDGE, SR, {theChan.name}, HT, OFF, HV, 1.43US")

    def setSlope(self, slope):
        theChan:SDSChannel = None
        theChan = self.getCurrSrcChannel()
        if theChan !=None:

            if slope in SDSTrigger.TRIG_SLOPE_OPTIONS:
                self.write(f"{theChan.name}: TRSL {slope}")
        #TODO: decide if we log something if one is asking for an unkown slope or the source was somehow not set.

    def setMode(self, mode):
        if mode in SDSTrigger.TRIG_MODE_OPTIONS:
            self.write(f"TRMD {mode}")
        #TODO: decide if we log something if one is asking for an unkown mode

    def setLevel(self, level):  
        theChan:SDSChannel = self.getCurrSrcChannel()
        if theChan != None:
            self.write(f"{theChan.name}: TRLV {level}")
        #TODO: decide if we log something if one is asking for an unkown mode

    def Auto(self):
        self.write("TRMD AUTO")

    def normal(self):
        self.write("TRMD NORM")

    def single(self):
        self.write("TRMD SINGLE")

    def stop(self):
        self.write("TRMD STOP")
   
    def getlevel(self, chanNr):
        srcChan = self.getChannel(chanNr)
        return self.query(f"{srcChan.name}:TRSL?")

    def getSlope(self):
        srcChan = self.getCurrSrcChannel()
        return self.query(f"{srcChan}:TRSL?")
    
    def setPosSlope(self):
        srcChan = self.getCurrSrcChannel()
        self.write(f"{srcChan.name}: TRSL POS") 

    def setNegSlope(self):
        srcChan = self.getCurrSrcChannel()
        self.write(f"{srcChan.name}: TRSL NEG") 

    def setWindowSlope(self):
        srcChan = self.getCurrSrcChannel()
        self.write(f"{srcChan.name}: TRSL WINDOW") 
    
    def setCoupling(self, coup:str):
        """Sets the coupling of this trigger for the current trigger source
        Valid coupling settings are: {AC,DC,HFREJ,LFREJ}
        """
        if coup in SDSTrigger.TRIG_COUPLING_OPTIONS:
            srcChan = self.getCurrSrcChannel()
            if srcChan != None:
                self.write(f"{srcChan.name}: TRCP {coup}")

    def getFrequency(self):
        response = self.query("CYMOMETER?")
        splitted = response.split()
        freq = splitted[1].removesuffix("Hz")
        return float(freq)

    def getholdOff(self): 
        pass

    def setDelay(self, delay):
        self.write(f"TRDL {delay}")

    def getDelay(self):
        return self.query("TRDL?")

  
  

  
    
    