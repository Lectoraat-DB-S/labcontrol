import pyvisa

from devices.BaseScope.BaseVertical import Vertical

###################################### BASETRIGGERUNIT #########################################################
class TriggerUnit(object):
    """New: creation of an object, or instance. 
    Only BaseTriggerUnit may call this new method for creating an object based on the correct type, as a kind
    of factory pattern. To get the right type __new__ will call getTriggerUnitClass methods from every subclass
    known to BaseTriggerUnit
    See also: https://mathspp.com/blog/customising-object-creation-with-__new__ 
    This coding scheme requires (automatic) registration of subclasses according pep487:
    see: https://peps.python.org/pep-0487/      
    """
    triggerUnitList = []

    @classmethod
    def getTriggerUnitClass(cls, vertical:Vertical,visaInstr:pyvisa.resources.MessageBasedResource=None):
        """Method for getting the right Python type, or the proper subclass of BaseTriggerUnit, based on parameters
        passed. 
            """
        pass
    
    def __init_subclass__(cls, **kwargs):
        """Method for autoregistration of BaseTriggerUnit subclasses. Don't alter and don't override. Be sure this
        the"""
        super().__init_subclass__(**kwargs)
        cls.triggerUnitList.append(cls)
        
    def __init__(self, vertical:Vertical=None, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """This method takes care of the intialisation of a BaseTriggerUnit object. Subclasses must override this 
        method, by initialising the datamembers needed. Remark: if the subclass relies on the intialisation done 
        below, don't forget to call the subcalss' super().__init()__ !"""
        self.vertical :pyvisa.resources.MessageBasedResource = vertical
        self.visaInstr = visaInstr
        self.source = None #the channel to trigger on.
        self.level =None
        
    def level(self):
        pass
        
    def level(self, level):
        pass 
    
    def setSource(self, chanNr):
        pass

    def getEdge(self):
        pass
    
    def setCoupling(self, coup:str):
        pass

    def setSlope(self, slope:str):
        pass
        
    def getFrequency(self):
        pass
        
    def getholdOff(self): #Trigger holdoff blz 215 TRIGger:MAIn:HOLDOff:VALue?
        pass

    def mode(self): #trigger mode blz 216 TRIGger:MAIn:MODe?
        pass

    def mode(self, modeVal):
        pass

    def getState(self): #tigger state zie blz 223 TRIGger:STATE?
        pass