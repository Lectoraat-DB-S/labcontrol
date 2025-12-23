import time
import numpy as np
from enum import Enum
import socket

import pyvisa
import logging
import time
#from devices.BaseScope import BaseScope
from devices.siglent.sds.SDS1000.Channel import SDSChannel
from devices.siglent.sds.util import INR_HASHMAP
import devices.siglent.sds.util as util
from devices.siglent.sds.util import SiglentIDN 
from devices.BaseScope import BaseScope
from devices.siglent.sds.SDS2000.Vertical import SDS2kVertical
from devices.siglent.sds.SDS1000.Horizontal import SDSHorizontal
from devices.siglent.sds.SDS1000.Trigger import SDSTrigger
from devices.BaseConfig import BaseScopeConfig, BaseDeviceConfig
from devices.siglent.sds.SDS1000.Display import SDSDisplay
from devices.siglent.sds.SDS1000.Acquisition import SDSAcquisition 


KNOWN_MODELS = [
        "SDS5000X",         #0.9.0 and later
        "SDS2000X Plus",    #1.3.5R3 and later
        "SDS6000 Pro",      #1.1.7.0 and later
        "SDS6000A+",        #1.1.7.0 and later
        "SHS800X",          #1.1.9 and later
        "SHS1000X",         #1.1.9 and later
        "SDS2000X HD",    #1.2.0.2 and later
        "SDS6000L",     #1.0.1.0
    ]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SiglentWaveformWidth(Enum):
    BYTE = "BYTE"
    WORD = "WORD"

class SiglentScope(BaseScope):

    @classmethod
    def SocketConnect(cls, rm:pyvisa.ResourceManager = None, scopeConfig: BaseScopeConfig = None,
                timeOut = 10000, readTerm = '\n', writeTerm = '\n')->pyvisa.resources.MessageBasedResource:
        myConfig: BaseScopeConfig = scopeConfig
        mydev = super().SocketConnect(rm,myConfig)
        if mydev != None:
            mydev.chunk_size = 20480000 # set to bigsize to prevent time if nrofsamples is large.
        return mydev

    @classmethod
    def getScopeClass(cls, rm: pyvisa.ResourceManager, urls, host, scopeConfig: BaseScopeConfig = None):
        """
            Tries to get (instantiate) this device, based on matched url or idn response
            This method will ONLY be called by the BaseScope class, to instantiate the proper object during
            creation by the __new__ method of BaseScope.     
        """  
        TCPIP_OPEN_MSG_LONG ="Welcome to the SCPI Instrument 'Siglent SDS1202X-E'"
        TCPIP_OPEN_MSG_SHORT ="SDS"


        if cls is SiglentScope:
            # first try find the scope on USB,
            pattern = "SDS"
            for url in urls:
                if pattern in url:
                    mydev:pyvisa.resources.MessageBasedResource = rm.open_resource(url)
                    mydev.timeout = 10000  # ms
                    mydev.read_termination = '\n'
                    mydev.write_termination = '\n'
                    idnRespStr=str(mydev.query("*IDN?"))
                    myidn = util.checkIDN(idnstr=idnRespStr)
                    if myidn != None:
                        return (cls, mydev)
                    #else:
                    #    return (None, None)
                        
            if scopeConfig == None:
                return (None, None, None)
            myConfig: BaseDeviceConfig = None
            for myConfig in scopeConfig:
                if BaseScope.isRightmodel(myConfig.defName, KNOWN_MODELS): #check if the ini section corresponds with the models of this class
                    mydev = cls.SocketConnect(rm=rm, scopeConfig=myConfig)
                    if mydev != None:
                        idnRespStr=str(mydev.query("*IDN?"))
                        myidn = util.checkIDN(idnstr=idnRespStr, models=KNOWN_MODELS)
                        if myidn != None:
                            return (cls, mydev)
                        #No return here!
                    #No return here!
                #No return here!
            return (None, None, None)  # only return None here, after all options have been tried.              


        #        if util.checkIDN(mydev):
        #            cls.__init__(cls, mydev)
        #            return (cls, mydev)
        #        else:
        #           return (None, None)
            

    def __init__(self, visaResc: pyvisa.resources.MessageBasedResource = None, myconfig: BaseScopeConfig = None ):
        """ 
            init: initialise a newly  created SiglentScope object. Because the pyvisa resource handle will be saved
            during the initing of BaseScope, this method calls super().__init__() 
        """
        super().__init__(visaResc, myconfig)
        self.horizontal = SDSHorizontal(visaResc)
        self.vertical = SDS2kVertical(2, visaResc)
        self.trigger = SDSTrigger(self.vertical,visaResc)
        self.display = SDSDisplay(visaResc)
        self.acquisition = SDSAcquisition(visaResc)
    
   
    def __exit__(self, *args):
        self.visaInstr.close()

    
    def query(self, cmd: str):
        return self.visaInstr.query(cmd)
    
    def write(self, cmd: str):
        self.visaInstr.write(cmd)


    @property
    def idn(self):
        """
            The idn command query identifies the instrument type and software version. The
            response consists of four different fields providing information on the
            manufacturer, the scope model, the serial number and the firmware revision.

            return: Siglent Technologies,<model>,<serial_number>,<firmware>
        """
        return self.query("*IDN?")
    
    def inr(self):
        """
            The INR? query reads and clears the contents of the INternal state change Register (INR). 
            The INR register (see table programming manual) records the completion of various internal operations 
            and state transitions.
        """
        inrResp = self.query("*INR?")
        return INR_HASHMAP[inrResp]        
    
    def rst(self):
        """
            The RST command initiates a device reset. The RST sets recalls the default setup.
        """
        self.write("*RST")
    
    def sav(self, panelNr):
        """
            The SAV command stores the current state of the instrument in internal memory. The SAV command stores 
            the complete front-panel setup of the instrument at the time the command is issued."""
        self.write(f"*SAV{panelNr}")

    def rcl(self, panelNr):
        """
            The RCL command sets the state of the instrument, using one of the ten non-volatile panel setups, by 
            recalling the complete front-panel setup of the instrument. Panel setup 0 corresponds to the default panel 
            setup.
        """
        self.write(f"*RCL{panelNr}")

    def lock(self, enable):
        """
            The LOCK command enables or disables the panel keyboard of the instrument.
        """
        if (enable):
            self.write(f"LOCK ON")
        else:
            self.write(f"LOCK OFF")
    
    def isLocked(self):
        retstr = self.query(f"LOCK?")
        if (retstr=="LOCK ON"):
            return True
        else:
            return False
        
    def menu(self, enable):
        if (enable):
            self.write(f"MENU ON")
        else:
            self.write(f"MENU OFF")
    
    def define(self, funct, param):
        match funct:
            case util.MATH_FUNC_ADD:
                self.write(f"DEFine EQN,'C1+C2'")
            case util.MATH_FUNC_SUB:
                self.write(f"DEFine EQN,'C1-C2'")
            case util.MATH_FUNC_MUL:
                self.write(f"DEFine EQN,'C1*C2'")
            case util.MATH_FUNC_DIF:
                self.write(f"DEFine EQN,'C1/C2'")
            case util.MATH_FUNC_FFT:
                self.write(f"DEFine EQN,'FFT({param})'")
            case util.MATH_FUNC_INT:
                self.write(f"DEFine EQN,'INTG({param})'")
            case util.MATH_FUNC_DIF:
                self.write(f"DEFine EQN,'DIFF({param})'")
            case util.MATH_FUNC_SQR:
                self.write(f"DEFine EQN,'SQRT({param})'")


    
    @property
    def memory_depth(self) -> int:
        """The query returns the maximum memory depth.

        :return: int
                    Returns the maximum memory depth
        """
        return (self.query(":ACQuire:MDEPth?"))

    @memory_depth.setter
    def memory_depth(self, mdepth: int):
        mdepth = min(self.memory_depth_values, key=lambda x: abs(x - mdepth))
        self.write(":ACQuire:MDEPth {}".format(mdepth))

# moved to SDSChannel, but should be method of the scope
    #def get_trigger_status(self):
    #    """The command query returns the current state of the trigger.
    #
    #    :return: str
    #                Returns either "Arm", "Ready", "Auto", "Trig'd", "Stop", "Roll"
    #    """
    #    return self.query(":TRIGger:STATus?")

    #def get_waveform_preamble(self):
    #    """The query returns the parameters of the source using by the command
    #    :WAVeform:SOURce.
    #   """
    #    params = self.query_raw(":WAVeform:PREamble?")
    #    params = params[11:]
    #    total_points = struct.unpack('i', params[116:120])[0]
    #    probe = struct.unpack('f', params[328:332])[0]
    #    vdiv = struct.unpack('f', params[156:160])[0] * probe
    #    voffset = struct.unpack('f', params[160:164])[0] * probe
    #    code_per_div = struct.unpack('f', params[164:168])[0] * probe
    #    timebase = struct.unpack('h', params[324:326])[0]
    #    delay = struct.unpack('d', params[180:188])[0]
    #    interval = struct.unpack('f', params[176:180])[0]

    #    return (total_points, vdiv, voffset, code_per_div, timebase, delay, interval, delay)

    def autosetup(self):
        """ This command attempts to automatically adjust the trigger, vertical, and
        horizontal controls of the oscilloscope to deliver a usable display of the
        input signal. Autoset is not recommended for use on low frequency events
        (< 100 Hz).

        :return: Nothing
        """
        self.write(":AUToset")

   
    def save_setup(self, file_location: str):
        """This command saves the current settings to internal or external memory
        locations.

        Users can recall from local,net storage or U-disk according to requirements

        :param file_location: string of path with an extension “.xml”.
        """
        if file_location.endswith(".xml"):
            self.write(':SAVE:SETup EXTernal,”{}”'.format(file_location))
        else:
            raise ValueError("Add in string that contains .xml")

    def recall_setup(self, file_location: str):
        """This command will recall the saved settings file from external sources.

        Users can recall from local,net storage or U-disk according to requirements

        :param file_location: string of path with an extension “.xml”.
        """
        if file_location.endswith(".xml"):
            self.write(':RECall:SETup EXTernal,”{}”'.format(file_location))
        else:
            raise ValueError("Add in string that contains .xml")

    def set_waveform_format_width(self, waveform_width: SiglentWaveformWidth):
        """The command sets the current output format for the transfer of waveform
        data.

        :param waveform_width:  SiglentWaveformWidth.BYTE or SiglentWaveformWidth.WORD
        """
        assert isinstance(waveform_width, SiglentWaveformWidth)

        self.write(":WAVeform:WIDTh {}".format(waveform_width.value))

    def get_waveform_format_width(self) -> SiglentWaveformWidth:
        """The query returns the current output format for the transfer of waveform
        data.
        """
        resp = self.query(":WAVeform:WIDTh?")

        match resp:
            case "BYTE":
                return SiglentWaveformWidth.BYTE
            case "WORD":
                return SiglentWaveformWidth.WORD

    def arm(self):
        """Sets up the trigger signal to single
        """

        self.set_single_trigger()
        self.set_trigger_run()
        self.query("*OPC?")

    def default_setup(self):
        pass



            