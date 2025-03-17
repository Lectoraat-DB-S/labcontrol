import pyvisa as visa
from devices.BaseScope import BaseTriggerUnit
from devices.tektronix.scope.Vertical import TekVertical, TekChannel

class TekTrigger(BaseTriggerUnit):
    
    def __init__(self, vertical = None, dev=None):
        super().__init__(vertical, dev)
        self.vertical: TekVertical = vertical
        self.source = 1
        
    def setLevel(self, level):
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
        source, and slope settings for the edge trigger
        This method retuns a dict."""
        retDict = {}
        respStr = str(self.visaInstr.writeself.visaInstr.query("TRIGGER:MAIN:EDGE?"))
        splitted = respStr.split(";")
        for prop in splitted:
            propSplit = str(prop).split(" ")
            retDict.update({str(propSplit[0]):str(propSplit[1])})
        return retDict        
