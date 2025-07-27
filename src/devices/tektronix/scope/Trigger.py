import pyvisa
from devices.BaseScope import BaseTriggerUnit
from devices.tektronix.scope.Vertical import TekVertical, TekChannel

class TekTrigger(BaseTriggerUnit):

    @classmethod
    def getTriggerUnitClass(cls, vertical:TekVertical, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """ Tries to get (instantiate) the correct object."""
        if cls is TekTrigger:
            return cls
        else:
            return None      
    
    def __init__(self, vertical: TekVertical = None, dev=None):
        super().__init__(vertical=vertical, visaInstr=dev)
        self.vertical: TekVertical = vertical
        self.source = 1
        
    def getTriggerSettings(self):
        return self.visaInstr.query("TRIGger?")
    
    def level(self):
        return self.visaInstr.query("TRIGger:MAIn:LEVel?")
        
    def level(self, level):
        self.visaInstr.write(f"TRIGGER:MAIN:LEVEL {level}") #Sets Trigger Level in V 
    
    def setSource(self, chanNr):
        """Sets his trigger source channel. An inheriting subclass wil have to implement this method by sending the proper SCPI commands to an actual oscilloscope to really set the correct level. 
        Remark: ths BaseChannel implementation will do nothing at all, as it is (very) empty"""
    
        vertical = self.vertical
        chans = vertical.channels
        theChan : TekChannel = None
        for  i, val in enumerate(chans):
                if (chanNr) in val.keys():
                    theChan = val[chanNr]
        
        if theChan!=None:
            self.visaInstr.write(f"TRIGger:MAIn:EDGE:SOUrce {theChan.name}")
            
    def getEdge(self):
        """Gets the current trigger setting of this oscilloscop, which will be consisiting of trigger coupling,
        source, and slope settings for the edge trigger.
        The Tektronix Programmer manual gives subsequent example:
        TRIGGER:MAIN:EDGE? might return SOURCE CH1;COUPLING DC;SLOPE RISE 
        This method retuns a dict."""
        retDict = {}
        respStr = str(self.visaInstr.query("TRIGGER:MAIN:EDGE?"))
        splitted = respStr.split(";")
        #check if length of splitted equals 3:
        if len(splitted) != 3:
            return "ERROR!"  #TODO temp solution. Better throw exception and retun null dict.
        for prop in splitted:
            propSplit = str(prop).split(" ")
            retDict.update({str(propSplit[0]):str(propSplit[1])}) #TODO: check if dict containt correct fields.
        return retDict        

    def setCoupling(self, coup:str):
        if coup == "AC" or coup == "DC" or coup == "HFRej" or coup == "LFRej":
            self.visaInstr.write(f"TRIGGER:MAIN:EDGE:COUPLING {coup}")
        #TODO: decide whether to log or to print an error message when coup is incorrect.
        
    def setSlope(self, slope:str):
        if slope == "FALL" or slope == "RISe":
            self.visaInstr.write(f"TRIGGER:MAIN:EDGE:SLOPe {slope}")
        #TODO: decide whether to log or to print an error message when coup is incorrect.
        
    def getFrequency(self):
        respStr = str(self.visaInstr.query("TRIGger:MAIn:FREQuency?"))
        freqResp = respStr.split(" ")
        return float(freqResp[1]) #TODO: handle error situations
    
    def getholdOff(self): #Trigger holdoff blz 215 TRIGger:MAIn:HOLDOff:VALue?
        respStr = str(self.visaInstr.query("TRIGger:MAIn:HOLDOff:VALue?"))
        holdOffResp = respStr.split(" ")
        return float(holdOffResp[1]) #TODO: handle error situations
    
    def mode(self): #trigger mode blz 216 TRIGger:MAIn:MODe?
        respStr = str(self.visaInstr.query("TRIGger:MAIn:MODe?"))
        modeResp = respStr.split(" ")
        return str(modeResp[1]) #TODO: handle error situations
    
    def mode(self, modeVal):
        if modeVal == "AUTO" :
            self.visaInstr.write(f"TRIGGER:MAIN:EDGE:SLOPe AUTO")
        if modeVal == "NORMAL":
            self.visaInstr.write(f"TRIGGER:MAIN:EDGE:SLOPe NORMal")
        #TODO: decide whether to log or to print an error message when coup is incorrect.
    
    def getState(self): #tigger state zie blz 223 TRIGger:STATE?
        respStr = str(self.visaInstr.query("TRIGger:STATE?"))
        
        return str(respStr) #TODO: handle error situations
    