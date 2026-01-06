import time
import numpy as np
from enum import Enum
import socket

import pyvisa
import logging
import time
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
#from devices.siglent.sds.SDS1000 import SDS1k 
#from devices.siglent.sds.SDS2000 import SDS2k


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SiglentWaveformWidth(Enum):
    BYTE = "BYTE"
    WORD = "WORD"

class SiglentScope(BaseScope):

    sigScopeList = []  

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseScope subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.sigScopeList.append(cls)
         

    @classmethod
    def SocketConnect(cls, rm:pyvisa.ResourceManager = None, scopeConfig: BaseScopeConfig = None,
                timeOut = 10000, readTerm = '\n', writeTerm = '\n')->pyvisa.resources.MessageBasedResource:
        myConfig: BaseScopeConfig = scopeConfig
        mydev = super().SocketConnect(rm,myConfig)
        if mydev != None:
            mydev.chunk_size = 20480000 # set to bigsize to prevent time if nrofsamples is large.
        return mydev    
    
    @classmethod
    def getSiglentScopeClass(cls, mydev:pyvisa.resources.MessageBasedResource, urls, host, theIDN: SiglentIDN, scopeConfigs: list = None):
        """Method for getting the right type of Siglent scope type based on the idn respons, so it can be created by the runtime.
        This Siglentscope implementation does nothing. The inheriting subclass should implement the needed logic"""
        pass
    
    @classmethod
    def getScopeClass(cls, rm: pyvisa.ResourceManager, urls, host, scopeConfigs: list = None):
        """
            Tries to get (instantiate) this device, based on matched url or idn response
            This method will ONLY be called by the BaseScope class, to instantiate the proper object during
            creation by the __new__ method of BaseScope.     
0        """  
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
                    myidn = util.decodeIDN(idnstr=idnRespStr)
                    if myidn == None:
                        return (None, None, None)
                    
                    for scope in cls.sigScopeList:
                        scopetype, dev, theConfig = scope.getSiglentScopeClass(mydev, urls, host, myidn, None)
                        if scopetype != None:
                            cls = scopetype
                            return (cls,dev, theConfig)
            
                    return  (None, None, None) # if getSiglentScopeClass can't find the proper instrument: return Nones.
                        
            #TODO: check below on creation of right siglentscope opject when using config.ini            
            if scopeConfigs == None: #If USB connection fails and there is no config section: just quit trying.....
                return (None, None, None)
            
            for aconfig in scopeConfigs:
                # check whether the sectionname of the config contains "SIGLENT"
                myconfig : BaseScopeConfig = aconfig
                if "Siglent" in myconfig.devName: 
                    modelNr, supplementalStr = util.getModel(myconfig.devName)
                    modelstr = str(modelNr)
                    mydev = cls.SocketConnect(rm=rm, scopeConfig=myconfig)
                    if mydev == None:
                        return (None, None, None)
                    
                    idnRespStr=str(mydev.query("*IDN?"))
                    myidn = util.decodeIDN(idnstr=idnRespStr)
                    if myidn == None:
                        return (None, None, None)
                    
                    idnRespStr=str(mydev.query("*IDN?"))
                    myidn = util.decodeIDN(idnstr=idnRespStr)

                    for scope in cls.sigScopeList:
                        scopetype, dev, theConfig = scope.getSiglentScopeClass(mydev, urls, host, myidn, None)
                        if scopetype != None:
                            cls = scopetype
                            return (cls,dev, theConfig)
            
                    return  (None, None, None) # if getSiglentScopeClass can't find the proper instrument: return Nones.
                    
                    if modelstr in SDS1k.KNOWN_MODELS or modelstr in SDS2k.KNOWN_MODELS:
                        mydev = cls.SocketConnect(rm=rm, scopeConfig=myconfig)
                        if mydev != None:
                            idnRespStr=str(mydev.query("*IDN?"))
                            myidn = util.decodeIDN(idnstr=idnRespStr)
                            if myidn == None:
                                return (None, None, None)
                                
                            if myidn.model in SDS1k.KNOWN_MODELS: #TODO: take range of modelnr into account.
                                return (SDS1k.SiglentScope1k, mydev, None)
                            elif myidn.model in SDS2k.KNOWN_MODELS:
                                return (SDS1k.SiglentScope1k, mydev, None)
                            else: # found a siglent but an unknown on, so return all None
                                return (None, None, None)

                        #No return here!
                    #No return here!
                #No return here!
            return (None, None, None)  # only return None here, after all options have been tried.     
            
    def __init__(self, visaResc: pyvisa.resources.MessageBasedResource = None, myconfig: BaseScopeConfig = None ):
        """ 
            init: initialise a newly  created SiglentScope object. Because the pyvisa resource handle will be saved
            during the initing of BaseScope, this method calls super().__init__() 
        """
        super().__init__(visaResc, myconfig)
        """
        self.horizontal = SDSHorizontal(visaResc)
        self.vertical = SDSVertical(2, visaResc)
        self.trigger = SDSTrigger(self.vertical,visaResc)
        self.display = SDSDisplay(visaResc)
        self.acquisition = SDSAcquisition(visaResc)
        """
   
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
        pass        
    
    def rst(self):
        pass
    
    def sav(self, panelNr):
        pass

    def rcl(self, panelNr):
        pass

    def lock(self, enable):
        pass 

    def isLocked(self):
        pass

    def menu(self, enable):
        pass
    
    def define(self, funct, param):
        pass
    
    @property
    def memory_depth(self) -> int:
        pass

    @memory_depth.setter
    def memory_depth(self, mdepth: int):
        pass

    def autosetup(self):
        pass
   
    def save_setup(self, file_location: str):
        pass

    def recall_setup(self, file_location: str):
        pass

    def set_waveform_format_width(self, waveform_width: SiglentWaveformWidth):
        pass
        
    def get_waveform_format_width(self) -> SiglentWaveformWidth:
        pass

    def arm(self):
        pass
    
    def default_setup(self):
        pass
