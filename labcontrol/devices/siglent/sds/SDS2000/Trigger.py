import pyvisa
from devices.BaseScope.BaseTrigger import TriggerUnit 
from devices.BaseLabDeviceUtils import SCPICommand
from devices.tektronix.scope.Vertical import TekVertical, TekChannel
from devices.siglent.sds.SDS2000.Vertical import SDS2kVertical, SDS2kChannel
from devices.siglent.sds.SDS2000.commands_full import SCPI

"""kleine studie naar dynamisch toevoegde code aan een object, zie:
1. https://stackoverflow.com/questions/77505812/dynamically-add-methods-to-a-python-class
2. https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6

"""

class SDS2kTrigger(TriggerUnit):

    TRIG_COUPLING_OPTIONS = ("AC","DC","HFREJ","LFREJ")
    TRIG_SLOPE_OPTIONS = ( "NEG", "POS", "WINDOW")
    TRIG_MODE_OPTIONS = ("AUTO", "NORM", "SINGLE", "STOP")
    TRIG_HOLDTYPE_OPTIONS = ("TI","PS","PL","P2","IS","IL","I2","OFF","EV")
    TRIG_TYPE_OPTIONS = ("EDGE", "GLIT","SLEW", "INTV")
    TRIG_SRC_OPTIONS = ("C1", "C2", "C3", "C4", "LINE","EX","EX5")

    @classmethod
    def getTriggerUnitObject(cls, vertical, dev):
        """ Tries to get (instantiate) the correct object."""
        if cls is SDS2kTrigger:
            cls.__init__(cls, vertical, dev)
            return cls
        else:
            return None      
    
    def __init__(self, vertical: SDS2kVertical = None, dev: pyvisa.resources.MessageBasedResource=None, scpiComm: SCPICommand = None):
        self.vertical = vertical
        self.source = 1
        self.visaInstr = dev
        self.type = None
        self.holdType = None
        self.holdValue = None
        self.scpiComm: SCPICommand = scpiComm # toegevoegd voor scpi command parsing en checking. TODO: wat als None? 
        #Dat is hier een error. Beste oplossingen 1. Exceptie 2. loggen. Waarschijnlijk beiden doen.
        #self.setSource(1)  #dit gaat niet goed.
        #self.auto()

    def query(self, cmd: str):
        return self.visaInstr.query(cmd)
    
    def write(self, cmd: str):
        self.visaInstr.write(cmd)

    def writeSCPICommand(self, spiDictIndex, newValue2Set):
        """Function for creating and writing SCPI commands, based on two (multi-levelled) dictionaries.
        Both dictionaries use the same method for indexing. One dict contains lambda functions of all available SCPI commands of a 
        measurement device, the other dict contains all valid parameter options if needed, of every corresponding command of the SCPI
        dict. Both dictionaries are set during the creation of a SCPICommand object, at the creation of the Python software object 
        representing the physically connected device. This SCPICommand will be passed to objects which needs to write commands to a
        device.
        Parameters:
        spiDictIndex: a list of which its elements define the correct index in the SCPI dict for getting the neede lambda function
        or for getting the available options of parameters for a command out of the PARAM dictionaries
        newValue2Set: the value a user want to set/write to the device for the given command at index spiDictIndex.
        """
        if self.scpiComm is None or spiDictIndex is None:
            raise TypeError("Invalid call to writeSCPICommand: No SCPICommand object or dictIndex has been set!")
        self.scpiComm.setIndex(spiDictIndex)
        mySCPIComm = self.scpiComm.getSCPIStr(paramIn=newValue2Set) #getSCPIStr throws an exception if no command has been found.
        self.write(mySCPIComm)
        
    def getCurrSettings(self):
        #TODO:controle of correct is -> zeer waarschijnlijk niet.
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
    
    def getSrcChannel(self, chanNr):
        chans = self.vertical.channels
        theChan : SDS2kChannel = None
        for  i, val in enumerate(chans):
                if (chanNr) in val.keys():
                    theChan = val[chanNr]
        
        return theChan
    
    def setSource(self, chanNr):
        """Sets his trigger source channel."""
        #TODO: convert to sds2000 commmand
        chans = self.vertical.channels
        theChan : SDS2kChannel = None
        for  i, val in enumerate(chans):
                if (chanNr) in val.keys():
                    theChan = val[chanNr]
        
        if theChan!=None:
            self.write(SCPI["TRIGGER"]["source"](theChan.name))
        else:
            return
        
    def getSource(self):
        return self.query(SCPI["TRIGGER"]["source?"]())

    def getFrequency(self):
        """Gets the value of the scope frequency counter of this Trigger unit."""
        return self.query(SCPI["TRIGGER"]["freq?"]())


    def setMode(self, newMode):
        """Sets the operating mode of this Trigger
        valid option for newMode: <mode>:= SINGle,NORMal,AUTO ,FTRIG"""
        #scpiCommIndex = ["TRIGGER","mode"]
        self.writeSCPICommand(["TRIGGER","mode"], newMode)

        
    def getMode(self):
        """Gets the current set mode of this Trigger"""
        self.write(SCPI["TRIGGER"]["mode?"]())

    def setState(self, newState):
        if  newState == "RUN" or newState == "run":
            self.write(["TRIGGER"]["run"]())
        else:
            self.write(["TRIGGER"]["stop"]())        
    
    def getState(self):
        return self.query(SCPI["TRIGGER"]["STATUS"]())
        
    def setType(self, newType):
        """:TRIGger:TYPE
        type>:= {EDGE,PULSE,SLOPe,INTerval,PATTern,
        WINDow,DROPout,VIDeo,QUALified,NTHEdge,DELay,SETup
        hold,IIC,SPI,UART,LIN,CAN,FLEXray,CANFd,IIS,1553B,SENT
        """
        self.writeSCPICommand(["TRIGGER","type"], newType)


    def getType(self):
        return self.query(SCPI["TRIGGER"]["type?"]())    
    
    ### EDGE COMMANDS ####

    def setCoupling(self, newCoupling):
        """<mode>:= {DC,AC,LFREJect,HFREJect}
        DC coupling allows dc and ac signals into the trigger path.
        AC coupling places a high pass filter in the trigger path,
        removing dc offset voltage from the trigger waveform. Use
        AC coupling to get a stable edge trigger w hen your
        waveform has a large dc offset.
        HFREJect which is a high frequency reject ion filter that
        adds a low pass filter in the trigger path to remove
        high frequency components from the trigger waveform.
        Use the high frequency reject ion filter to remove
        high frequency noise, such as AM or FM broadcast
        stations, from the trigger path.
        LFREJect which is a low frequency reject ion filter adds a
        high pass filter in series with the trigger waveform to
        remove any unwanted low frequency componen ts from a
        trigger waveform, such as power line frequencies, that can
        interfere with proper triggering.
        """
        self.writeSCPICommand(["TRIGGER","EDGE","coupling"], newCoupling)
        
    
    def getCoupling(self):
        return self.query(SCPI["TRIGGER"]["EDGE"]["coupling?"]())
    
    def setNrEvents(self, nrOfEvs):
        """This command sets the number of holdoff events of the edge trigger
        value>:= V alue in NR1 format, inclu ding an integer and nodecimal point, like 1. 
        The range of the value is [1, 100000000].
        """
        if nrOfEvs<1 or nrOfEvs > 100000000:
            return
        self.write(SCPI["TRIGGER"]["EDGE"]["events"](nrOfEvs))

    def getNrEvents(self):
        return self.query(SCPI["TRIGGER"]["EDGE"]["events?"]())

    def setHOTime(self, newTime):
        """The command sets the holdoff time of the edge trigger
        Parameter newTime : range [8.00E-09, 3.00E+01]"""
        if newTime<8e-9 or newTime > 3e1:
            return
        self.write(SCPI["TRIGGER"]["EDGE"]["hldtime"](newTime))
            
    def getHOTime(self):
        return self.query(SCPI["TRIGGER"]["EDGE"]["hldtime?"]())

    def setHOType(self, newType):
        """The command selects the holdoff type of the edge trigger.
        Parameter newType: <holdoff_type>:= OFF,EVENts,TIME}
        OFF means to turn off the holdoff
        EVENts means the number of trigger events that the
        oscilloscope counts before re arming the trigger circuitry
        TIME means the amount of time that the oscilloscope
        waits before re arming the trigger circuitry
        """
        #self.write(SCPI["TRIGGER"]["EDGE"]["hldtype"](newType)) TODO: oude code, moet eruit als onderstaande goed werkt

        self.writeSCPICommand(["TRIGGER","EDGE","hldtype"], newType)
            
    def getHOType(self):
        return self.query(SCPI["TRIGGER"]["EDGE"]["hldtype?"]())
    
    def setHOstart(self, holdoffStart):
        """The command defines the initial position of the edge trigger holdoff
        <start_holdoff>: holdoff>:= LAST_TRIG,ACQ_START}
        LAST_TRIG means the initial position of holdoff is the first
        time point satisfyin g the trigger condition
        ACQ_START means the initial position of holdoff is the
        time of the last trigger."""
        holdOffStartOptions = ["LAST_TRIG","ACQ_START"]
        if holdoffStart not in holdOffStartOptions:
            return
        self.write(SCPI["TRIGGER"]["EDGE"]["hldstart"](holdoffStart))

    def getHOStart(self):
        return self.query(SCPI["TRIGGER"]["EDGE"]["hldstart?"]())
    
    def setImpedance(self, theImp):
        """The command defines the initial position of the edge trigger holdoff
        <start_holdoff>: holdoff>:= LAST_TRIG,ACQ_START}
        LAST_TRIG means the initial position of holdoff is the first
        time point satisfyin g the trigger condition
        ACQ_START means the initial position of holdoff is the
        time of the last trigger.
        """
        self.writeSCPICommand(["TRIGGER","EDGE","impedance"], theImp)
        
    def getImpedance(self):
        return self.query(SCPI["TRIGGER"]["EDGE"]["impedance?"]())
    
    def setEdgeLeve(self, newLevel):
        """The command sets the trigger level of the edge trigger.
        Parameter newLevel:<level_value>:=[4.1*vertical_scale vertical_offset4.1*vertical_scale vertical_offset]
        """
        #TODO: check validity of value newLevel against range.
        self.write(SCPI["TRIGGER"]["EDGE"]["level"](newLevel))
            
    def getEdgeLeve(self):
        return self.query(SCPI["TRIGGER"]["level?"]())
    
    def setNoiseRej(self, newState):
        """The command sets the state of the noise rejection.
        <state>:= OFF,ON}
        """
        
        self.writeSCPICommand(["TRIGGER","EDGE","level"], newState)

    def getNoiseRej(self):
        return self.query(SCPI["TRIGGER"]["EDGE"]["level?"]())
        
    def setSlope(self, newSlope):
        """The command sets the slope of the edge trigger.
        RISing,FALLing,ALTernate}
        """
        
        self.writeSCPICommand(["TRIGGER","EDGE","slope"], newSlope)

##### SLOPE SUBSYSTEM COMMDANDS ######################
    def getSloped(self):
        return self.query(SCPI["TRIGGER"]["slope?"]())

    """:TRIGger:SLOPe Commands
    The :TRIGGER:SLOPe subsystem commands control the slope trigger parameters.
     :TRIGger:SLOPe:COUPling
     :TRIGger:SLOPe:HLDEVent
     :TRIGger:SLOPe:HLDTime
     :TRIGger:SLOPe:HLEVel
     :TRIGger:SLOPe:HOLDoff
     :TRIGger:SLOPe:HSTart
     :TRIGger:SLOPe:LIMit
     :TRIGger:SLOPe:LLEVel
     :TRIGger :SLOPe:NREJect
     :TRIGger:SLOPe:SLOPe
     :TRIGger:SLOPe:SOURce
     :TRIGger:SLOPe:TLOWer
     TRIGger:SLOPe:TUPPer
    """

##### PULSE SUBSYSTEM COMMDANDS ######################
    """:TRIGger:PULSe Commands
    The :TRIGGER:PULSe subsystem commands control the pulse trigger parameters.
     :TRIGger:PULSe:COUPling
     :TRIGger:PULSe:HLDEVent
     :TRIGger:PULSe:HLDTime
     TRIGger:PULSe:HOLDoff
     :TRIGger:PULSe:HSTart
     :TRIGger:PULSe:LEVel
     :TRIGger:PULSe:LIMit
     :TRIGger:PULSe:NR EJect
     :TRIGger:PULSe:POLarity
     :TRIGger:PULSe:SOURce
     :TRIGger:PULSe:TLOWer
     TRIGger:PULSe:TUPPer
    """
    


##### VIDEO SUBSYSTEM COMMDANDS ######################
    """:TRIGger:VIDeo Commands
    The :TRIGGER:VIDeo subsystem commands control the video trigger parameters.
     :TRIGger:VIDeo:FCNT
     :TRIGger:VIDeo:FIELd
     :TRIGger:VIDeo:FRATe
     :TRIGger:VIDeo:INTerlace
     :TRIGger:VIDeo:LCNT
     :TRIGger:VIDeo:LEVel
     :TRIGger:VIDeo:LINE
     TRIGger:VIDeo:SOURce
     :TRIGger:VIDeo:STANdard
     :TRIGger:VIDeo:SYNC
    """
    
##### WINDOW SUBSYSTEM COMMDANDS ######################

    """:TRIGger:WINDow Commands
    The :TRIGGER:WINDow subsystem commands control the window trigger parameters.
     :TRIGger:WINDow:CLEVel
     :TRIGger:WINDow:COUPling
     :TRIGger:WINDow:DLEVel
     :TRIGger:WINDow:HLDEVent
     :TRIGger:WINDow:HLDTime
     TRIGger:WINDow:HLEVel
     :TRIGger:WINDow:HOLDoff
     :TRIGger:WINDow:HSTart
     :TRIGger:WINDow:LLEVel
     :TRIGger:WINDow:NREJect
     :TRIGger:WINDow:SOURce
     :TRIGger:WINDow:TYPE
    """
    
##### Interval SUBSYSTEM COMMDANDS ######################
    """:TRIGger:INTerval Commands
    The :TRIGGER:INTerval subsystem commands control the interval trigger parameters.
     :TRIGger:INTerval:COUPling
     :TRIGger:INTerval:HLDEVent
     :TRIGger:INTerval:HLDTime
     :TRIGger:INTerval:HOLDoff
     :TRIGger:INTerval:HSTart
     :TRIGger:INTerval:LEVel
     :TRIGger:INTerval:LIMit
     :TRIGger:INTerval:NREJect
     :TRIGger:INTerval:SLOPe
     :TRIGger:INTerval:SOURce
     :TRIGger:INTerval:TLOWer
     :TR IGger:INTerval:TUPPer
    """

##### Dropout SUBSYSTEM COMMDANDS ######################    
    """:TRIGger:DROPout Commands
    The :TRIGGER:DROPout subsystem commands control the dropout trigger parameters.
     :TRIGger:DROPout:COUPling
     :TRIGger:DROPout:HLDEVent
     :TRIGger:DROPout:HLDTime
     :TRIGger:DROPout:HOLDoff
     :TRIGger:DROPout:HSTart
     :TRIGger:DROPout:LEVel
     :TRIGger:DROPout:NREJect
     :TRIGger:DROPout:SLOPe
     :TRIGger:DROPout:SOURce
     :TRIGger:DROPout:TIME
     :TRIGger:DROPout:TYPE
    """


##### RUNT SUBSYSTEM COMMDANDS ######################
    """:TRIGger:RUNT Commands
    The :TRIGGER:RUNT subsystem commands control the runt trigger parameters.
     :TRIGger:RUNT:COUPling
     :TRIGger:RUNT:HLDEVent
     :TRIGger:RUNT:HLDTime
     :TRIGger:RUNT:HLEVel
     :TRIGger:RUNT:HOLDoff
     :TRIGger:RUNT:HSTart
     :TRIGger:RUNT:LIMit
     :TRIGger:RUNT:LLEVel
     TRIGger:RUNT:NREJect
     :TRIGger:RUNT:POLarity
     :TRIGger:RUNT:SOURce
     :TRIGger:RUNT:TLOWer
     TRIGger:RUNT:TUPPer"""
    
    """:TRIGger:PATTern Commands
    The :TRIGGER:PATTern subsystem commands control the pattern trigger parameters.
     :TRIGger:PATTern:HLDEVent
     :TRIGger:PATTern:HLDTime
     :TRIGger:PATTern:HOLDoff
     :TRIGger:PATTern:HSTart
     :TRIGger:PATTern:INPut
     :TRIGger:PATTern:LEVel
     :TRIGger:PATTern:LIMit
     :TRIGger:PATTern:LOGic
     :TRIGger:PATTern:TLOWer
     TRIGger:PATTern:TUPPer"""
    
    """:TRIGger:QUALified Commands
    The :TRIGGER:QUALified subsystem commands control the qualified trigge r parameters.
     :TRIGger:QUALified:ELEVel
     :TRIGger:QUALified:ESLope
     :TRIGger:QUALified:ESource
     :TRIGger:QUALified:LIMit
     :TRIGger:QUALified:QLEVel
     :TRIGger:QUALified:QSource
     :TRIGger:QUALified:TLOWer
     :TRIGger:QUALified:TUPPer
     :TRIGger:QUALified:TYPE"""
    
    """:TRIGger:DELay Commands
    The :TRIGGER: DELay subsystem commands control the delay trigger parameters.
     : DEL ay :COUPling
     TRIGger:DELay:SOURce
     TRIGger:DELay:SOURce2
     TRIGger:DELay:SLOPe
     TRIGger:DELay:SLOPe2
     TRIGger:DELay:LEVel
     :TRIGger:DELay:LEVel2
     TRIGger:DELay:LIMit
     TRIGger:DELay:TUPP er
     TRIGger:DELay:TLOWer"""
    
    """:TRIGger:NEDGe Commands
    The:TRIGGER:NEDGe subsystem commands control the Nth Edge trigger parameters.
     : NEDGe :SOURce
     : NEDGe: SLOPe
     : NEDGe :IDLE
     : NEDGe :EDGE
     : NEDGe :LEVel
     : NEDGe :HOLDoff
     : NEDGe :HLDTime
     : NEDGe :HLDEVent
     : NEDGe :HSTart
     : NEDGe :NREJect"""
    
    """:TRIGger:SHOLd Commands
    The :TRIGGER:SHOLd subsystem commands control the setup/hold trigger parameters.
     : SHOLd :TYPE
     : SHOLd :CSource
     : SHOLd :CTHReshold
     : SHOLd :SLOPe
     : SHOLd :DSource
     : SHOLd :DTHReshold
     : SHOLd :LEVel
     : SHOLd :LIMit
     : SHOLd :TUPPer
     : SHOLd :TLOWer"""
    
    """ :TRIGger:IIC Commands
    The :TRIGGER:IIC subsystem commands control the IIC bus trigger parameters.
     :TRIGger:IIC:ADDRess
     :TRIGger:IIC:ALENgth
     :TRIGger:IIC:CONDition
     :TRIGger:IIC:DAT2
     :TRIGger:IIC:DATA
     :TRIGger:IIC:DLENgth
     :TRIGger:IIC:LIMit
     :TRIGger:IIC:RWBit
     :TRIGger:IIC:SCLSource
     :TRIGger:IIC:SCLThreshold
     :TRIGger:IIC:SDASource
     :TRIGger:IIC:SDAThreshold"""
    
    """:TRIGger:SPI Commands 
    The :TRIGGER:SPI subsyste commands control the SPI bus trigger modes and parameters.
     :TRIGger: BIT ord er
     :TRIGger:SPI:CLKSource
     :TRIGger:SPI:CLKThreshold
     :TRIGger:SPI:CSSource
     :TRIGger:SPI:CSThreshold
     :TRIGger:SPI:CSTYpe
     :TRIGger:SPI:DATA
     :TRIGger:SPI:DLENgth
     :TRIGger:SPI:LATChedge
     :TRIGger:SPI:MISOSource
     :TRIGger:SPI:MISOThreshold
     :TRIGger:SPI:MOSISource
     :TRIGger:SPI:MOSIThreshold
     :TRIGger:SPI:NCSSource
     :TRIGger:SPI:NCSThreshold
     :TRIGger:SPI:TTYPe"""
    
    """The :TRIGGER:UART subsystem
    commands control the UART bus trigger parameters.
     TRIGger:UART:BAUD
     :TRIGger: BITorder
     :TRIGger:UART:CONDition
     :TRIGger:UART:DATA
     :TRIGger:UART:DLENgth
     :TRIGger:UART:IDLE
     :TRIGger:UART:LIMit
     :TRIGger:UART:PARity
     :TRIGger:UART:RXSource
     :TRIGger:UART:RXThreshold
     :TRIGger:UART:STOP
     :TRIGger:UART:TTYPe
     :TRIGger:UART:TXSource
     :TRIGger:UART:TXThreshold"""
    
    """:TRIGger:CAN Commands
    The :TRIGGER:CAN subsystem commands control the CAN bus trigger parameters.
     :TRIGger:CAN:BAUD
     :TRIGger:CAN:CONDition
     :TRIGger:CAN:DAT2
     :TRIGger:CAN:DATA
     :TRIGger:CAN:ID
     :TRIGger:CAN:IDLength
     :TRIGger:CAN:SOURce
     :TRIGger:CAN:THReshold"""
    
    """:TRIGger:LIN Commands
    The :TRIGGER:LIN subsystem commands control the LIN bus trigger parameters.
     :TRIGger:LIN:BA UD
     :TRIGger:LIN:CONDition
     :TRIGger:LIN:DAT2
     :TRIGger:LIN:DATA
     :TRIGger:LIN:ERRor:CHECksum
     :TRIGger:LIN:ERRor:DLENgth
     :TRIGger:LIN:ERRor:ID
     :TRIGger:LIN:ERRor:PARity
     :TRIGger:LIN:ERRor:SYNC
     :TRIGger:LIN:ID
     :TRIGger:LIN:SOURce
     :TRIGger:LIN:STANdard
     :TRIGger:LIN:THReshold"""
    
    """:TRIGger:FLEXray Commands [Option]
    The :TRIGGER:FLEXray subsystem commands control the FlexRay bus trigger parameters.
     :TRIGger:FLEXray:BAUD
     :TRIGger:FLEXray:CONDition
     :TRIGger:FLEXray:FRAMe:COMPare
     :TRIGger:FLEXray:FRAMe:CYCLe
     :TRIGger:FLEXray:FRAMe:ID
     :TRIGger:FLEXray:FRAMe:REPetition
     :TRIGger:FLEXray:SOURce
     :TRIGger:FLEXray:THReshold"""
    
    """:TRIGger:CANFd Commands [Option]
    The :TRIGGER:CANFd subsystem commands control the CAN FD bus trigger parameters.
     :TRIGger:CANFd:BAUDData
     : CANFd:BAUDNominal
     :TRIGger:CANFd:C ONDition
     :TRIGger:CANFd:DAT2
     :TRIGger:CANFd:DATA
     :TRIGger:CANFd:FTYPe
     :TRIGger:CANFd:ID
     :TRIGger:CA NFd:IDLength
     :TRIGger:CANFd:SOURce
     :TRIGger:CANFd:THReshold"""

    """:TRIGger:IIS Commands [Option]
    The :TRIGGER:IIS subsystem  commands control the IIS bus trigger parameters.
     :TRIGger:IIS:AVARiant
     :TRIGger:IIS:BCLKSource
     :TRIGger:IIS:BCLKThreshold
     :TRIGger: BITorder
     :TRIGger:IIS:CHANnel
     :TRIGger:IIS:COMPare
     :TRIGger:IIS:CONDition
     :TRIGger:IIS:DLENgth
     :TRIGger:IIS:DSource
     :TRIGger:IIS:DTHReshold
     :TRIGger:IIS:LATChedge
     :TRIGger:IIS:LCH
     :TRIGger:IIS:VALue
     :TRIGger:IIS:WSSource
     :TRIGger:IIS:WSTHreshold"""
    """"""
