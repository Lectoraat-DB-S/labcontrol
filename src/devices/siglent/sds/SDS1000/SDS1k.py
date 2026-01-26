import time
import numpy as np
from enum import Enum
import socket

import pyvisa
import logging
import time
#from devices.BaseScope import BaseScope
from devices.siglent.sds.Scopes import SiglentScope 
from devices.siglent.sds.SDS1000.Channel import SDSChannel
from devices.siglent.sds.util import INR_HASHMAP
import devices.siglent.sds.util as util
from devices.siglent.sds.util import SiglentIDN 
from devices.BaseScope import BaseScope
from devices.siglent.sds.SDS1000.Vertical import SDSVertical
from devices.siglent.sds.SDS1000.Horizontal import SDSHorizontal
from devices.siglent.sds.SDS1000.Trigger import SDSTrigger
from devices.BaseConfig import BaseScopeConfig, BaseDeviceConfig
from devices.siglent.sds.SDS1000.Display import SDSDisplay
from devices.siglent.sds.SDS1000.Acquisition import SDSAcquisition
from devices.siglent.sds.Scopes import SiglentScope 



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SiglentWaveformWidth(Enum):
    BYTE = "BYTE"
    WORD = "WORD"

class SiglentScope1k(SiglentScope):

    KNOWN_MODELS = [
        "SDS1000CFL",   #non-SPO model Series
        "SDS1000A",     #non-SPO model Series
        "SDS1000CML+",  #non-SPO model Series
        "SDS1000CNL+",  #non-SPO model Series
        "SDS1000DL+",   #non-SPO model Series
        "SDS1000E+",    #non-SPO model Series
        "SDS1000F+",    #non-SPO model Series
        "SDS1000X",     #SPO model Series
        "SDS1000X+",    #SPO model Series
        "SDS1000X-E",   #SPO model Series
        "SDS1000X-C",   #SPO model Series
        "SDS1202X",
        "SDS1202X-E",
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
        if cls is SiglentScope1k:
            if theIDN == None:
                return (None, None)
            
            for amodel in SiglentScope1k.KNOWN_MODELS:
                if theIDN.isModelInRange(amodel):
                    return (cls, mydev)
                #NO RETURN, trying next model of the 1k series.
            return(None, None)
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
    
    ### removed getScopeClass ####        

    def __init__(self, visaResc: pyvisa.resources.MessageBasedResource = None, myconfig: BaseScopeConfig = None ):
        """ 
            init: initialise a newly  created SiglentScope object. Because the pyvisa resource handle will be saved
            during the initing of BaseScope, this method calls super().__init__() 
        """
        super().__init__(visaResc, myconfig)
        self.horizontal = SDSHorizontal(visaResc)
        self.vertical = SDSVertical(2, visaResc)
        self.trigger = SDSTrigger(self.vertical,visaResc)
        self.display = SDSDisplay(visaResc)
        self.acquisition = SDSAcquisition(visaResc)
    

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



            