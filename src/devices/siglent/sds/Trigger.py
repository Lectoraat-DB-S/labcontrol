import pyvisa
from devices.BaseScope import BaseTriggerUnit
from devices.tektronix.scope.Vertical import TekVertical, TekChannel
from devices.siglent.sds.Vertical import SDSVertical, SDSChannel

class SDSTrigger(BaseTriggerUnit):

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
        #self.setSource(1)  #dit gaat niet goed.
        #self.auto()

    def query(self, cmd: str):
        return self.visaInstr.query(cmd)
    
    def write(self, cmd: str):
        self.visaInstr.write(cmd)

    def getChannel(self, chanNr):
        theChan : SDSChannel = None
        for  i, val in enumerate(chanNr):
                if (chanNr) in val.keys():
                    theChan = val[chanNr]
        
        return theChan
    
    def getCurrSrcChannel(self):
        return self.getChannel(self.source)
    
    def setSource(self, chanNr):
        """Sets his trigger source channel."""
        vertical = self.vertical
        chans = vertical.channels
        theChan : SDSChannel = None
        for  i, val in enumerate(chans):
                if (chanNr) in val.keys():
                    theChan = val[chanNr]
        
        if theChan!=None:
            self.write(f"TRSE EDGE, SR, C1, HT, OFF, HV, 1.43US {theChan.name}")

    def auto(self):
        self.write("TRMD AUTO")

    def normal(self):
        self.write("TRMD NORM")

    def single(self):
        self.write("TRMD SINGLE")

    def stop(self):
        self.write("TRMD STOP")
            
    def level(self):
        srcChan = self.getCurrSrcChannel()
        return self.query(f"{srcChan}:TRig_LeVel?")
        
    def level(self, level):
        srcChan = self.getCurrSrcChannel()
        self.write(f"{srcChan}:TRig_LeVel {level}") #Sets Trigger Level in V 

    def levelOf(self, chanNr):
        srcChan = self.getChannel(chanNr)
        return self.query(f"{srcChan}:TRig_LeVel?")

    def levelOf(self, chanNr, level):
        srcChan = self.getChannel(chanNr)
        self.write(f"{srcChan}:TRig_LeVel {level}") #Sets Trigger Level in V 

    def slope(self):
        srcChan = self.getCurrSrcChannel()
        return self.query(f"{srcChan}:TRig_Slope?")
    
    def slopePos(self):
        srcChan = self.getCurrSrcChannel()
        self.write(f"{srcChan}: TRig_Slope POS") 

    def slopeNeg(self):
        srcChan = self.getCurrSrcChannel()
        self.write(f"{srcChan}: TRig_Slope NEG") 

    def slopeWindow(self):
        srcChan = self.getCurrSrcChannel()
        self.write(f"{srcChan}: TRig_Slope WINDOW") 

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

    ##### copy paste for siglent.scopes: have to check this!####

    def set_trigger_run(self):
        """The command sets the oscilloscope to run
        """
        self.write(":TRIGger:RUN")

    def set_single_trigger(self):
        """The command sets the mode of the trigger.

        The backlight of SINGLE key lights up, the oscilloscope enters the
        waiting trigger state and begins to search for the trigger signal that meets
        the conditions. If the trigger signal is satisfied, the running state shows
        Trig'd, and the interface shows stable waveform. Then, the oscilloscope stops
        scanning, the RUN/STOP key becomes red, and the running status shows Stop.
        Otherwise, the running state shows Ready, and the interface does not display
        the waveform.

        :return: Nothing
        """
        self.write(":TRIGger:MODE SINGle")

    def set_normal_trigger(self):
        """The command sets the mode of the trigger.

        The oscilloscope enters the wait trigger state and begins to search for
        trigger signals that meet the conditions. If the trigger signal is satisfied,
        the running state shows Trig'd, and the interface shows stable waveform.
        Otherwise, the running state shows Ready, and the interface displays the last
        triggered waveform (previous trigger) or does not display the waveform (no
        previous trigger).

        :return: Nothing
        """
        self.write(":TRIGger:MODE NORMal")

    def set_auto_trigger(self):
        """The command sets the mode of the trigger.

        The oscilloscope begins to search for the trigger signal that meets the
        conditions. If the trigger signal is satisfied, the running state on the top
        left corner of the user interface shows Trig'd, and the interface shows stable
        waveform. Otherwise, the running state always shows Auto, and the interface
        shows unstable waveform.

        :return: Nothing
        """
        self.write(":TRIGger:MODE AUTO")

    def set_force_trigger(self):
        """The command sets the mode of the trigger.

        Force to acquire a frame regardless of whether the input signal meets the
        trigger conditions or not.

        :return: Nothing
        """
        self.write(":TRIGger:MODE FTRIG")

    def get_trigger_mode(self):
        """The query returns the current mode of trigger.

        :return: str
                    Returns either "SINGle", "NORMal", "AUTO", "FTRIG"
        """
        return self.query(":TRIGger:MODE?")

    def set_rising_edge_trigger(self):
        """The command sets the slope of the slope trigger to Rising Edge

        :return: Nothing
        """
        self.write(":TRIGger:SLOPe:SLOPe RISing")

    def set_falling_edge_trigger(self):
        """The command sets the slope of the slope trigger to Falling Edge

        :return: Nothing
        """
        self.write(":TRIGger:SLOPe:SLOPe FALLing")

    def set_alternate_edge_trigger(self):
        """The command sets the slope of the slope trigger to Falling Edge

        :return: Nothing
        """
        self.write(":TRIGger:SLOPe:SLOPe ALTernate")

    def get_edge_trigger(self):
        """The query returns the current slope of the slope trigger

        :return: str
                    Returns either "RISing", "FALLing", "ALTernate"
        """
        return self.query(":TRIGger:SLOPe:SLOPe?")

  
    def set_trigger_edge_level(self, level: float):
        """The command sets the trigger level of the edge trigger

        :param level: Trigger level
        """

        """
        TODO: trigger level needs to be between:
        [-4.1*vertical_scale-vertical_offset, 4.1*vertical_scale-vertical_offset]
        """
        self.write(":TRIGger:EDGE:LEVel {}".format(str(level)))

    