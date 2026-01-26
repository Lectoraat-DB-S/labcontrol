import time
import numpy as np
from enum import Enum
import socket

import pyvisa
import logging
import time
from devices.siglent.sds.Scopes import SiglentScope 
from devices.siglent.sds.SDS2000.Channel import SDS2kChannel
from devices.siglent.sds.util import INR_HASHMAP
import devices.siglent.sds.util as util
from devices.siglent.sds.util import SiglentIDN 
from devices.BaseScope import BaseScope
from devices.siglent.sds.SDS2000.Vertical import SDS2kVertical
from devices.siglent.sds.SDS2000.Horizontal import SDS2kHorizontal
from devices.siglent.sds.SDS2000.Trigger import SDSTrigger
from devices.BaseConfig import BaseScopeConfig, BaseDeviceConfig
from devices.siglent.sds.SDS2000.Display import SDSDisplay
from devices.siglent.sds.SDS2000.Acquisition import SDS2kAcquisition 



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SiglentWaveformWidth(Enum):
    BYTE = "BYTE"
    WORD = "WORD"

class SiglentScope2k(SiglentScope):

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

    @classmethod
    def getScopeClass(cls, rm: pyvisa.ResourceManager, urls, host, scopeConfigs: list = None):
        """
        This method is added for comptability with the Basescope class. As this class gets somehow registered     
        by Basescope's __init_subclass__ method, this method will be called by the Basescope class, resulting  
        in a crash of the object factory process.
        """  
        return (None, None, None)

    @classmethod
    def getSiglentScopeClass(cls, mydev:pyvisa.resources.MessageBasedResource, urls, host, theIDN: SiglentIDN, scopeConfigs: list = None):
        """Method for return the right SiglentScope (sub)type based on the idn respons, so it can be instantiated
        by the factory process in the SiglentScope class. This implementation only returns the proper type of class 
        when cls is of right type and if the IDN of the connected device fits the models covered by this class. 
        """
        if cls is SiglentScope2k:

            if theIDN == None:
                return (None, None)
            for amodel in SiglentScope2k.KNOWN_MODELS:
                if theIDN.isModelInRange(amodel):
                    return (cls, mydev)
            else:
                return (None, None)
        else:
            return (None, None)


    @classmethod
    def SocketConnect(cls, rm:pyvisa.ResourceManager = None, scopeConfig: BaseScopeConfig = None,
                timeOut = 10000, readTerm = '\n', writeTerm = '\n')->pyvisa.resources.MessageBasedResource:
        myConfig: BaseScopeConfig = scopeConfig
        mydev = super().SocketConnect(rm,myConfig)
        if mydev != None:
            mydev.chunk_size = 20480000 # set to bigsize to prevent time if nrofsamples is large.
        return mydev

    ###### Removed getScopeclass, moved functionality to SiglentScope class #########################

    def __init__(self, visaResc: pyvisa.resources.MessageBasedResource = None, myconfig: BaseScopeConfig = None ):
        """ 
            init: initialise a newly  created SiglentScope object. Because the pyvisa resource handle will be saved
            during the initing of BaseScope, this method calls super().__init__() 
        """
        super().__init__(visaResc, myconfig)
        self.horizontal = SDS2kHorizontal(visaResc)
        self.vertical = SDS2kVertical(2, visaResc)
        self.trigger = SDSTrigger(self.vertical,visaResc)
        self.display = SDSDisplay(visaResc)
        self.acquisition = SDS2kAcquisition(visaResc)
    
   
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
        return self.query("*OPC?")

    def default_setup(self):
        pass



            