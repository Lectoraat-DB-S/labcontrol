import pyvisa
import logging
import socket
from devices.siglent.spd.SupplyChannel import SPDChannel
from devices.BaseSupply import BaseSupply
from devices.BaseConfig import BaseSupplyConfig
import devices.siglent.spd.util as util

logger = logging.getLogger(__name__)
#logging.basicConfig(filename='SiglentSupply.log', level=logging.INFO)
logger.setLevel(logging.INFO)

class SiglentPowerSupply(BaseSupply):
    KNOWN_MODELS = [
        "SPD3303X",
        "SPD3303X-E",
    ]

    MANUFACTURERS = {
        "SPD3303X": "Siglent",  
    }

    @classmethod
    def getSupplyClass(cls, rm: pyvisa.ResourceManager, urls, host, supplyConfigs: list = None):
        if cls is SiglentPowerSupply:
            # first try find the scope on USB,
            pattern = "SPD"
            for url in urls:
                if pattern in url:
                    mydev:pyvisa.resources.MessageBasedResource = rm.open_resource(url)
                    mydev.timeout = 10000  # ms
                    mydev.read_termination = '\n'
                    mydev.write_termination = '\n'
                    
                    #TODO: idn nog decoderen en aantal kanalen daarop instellen! Zie onderstaande
                    idnRespStr=str(mydev.query("*IDN?"))
                    myidn = util.decodeIDN(idnstr=idnRespStr)
                    if myidn == None:
                        return (None, None, None)
                    else:
                        if myidn == None:
                            return (None,None)
                        for amodel in SiglentPowerSupply.KNOWN_MODELS:
                            if myidn.isModelInRange(amodel):
                                return (cls, 2, mydev)
                        return (None, None, None)
                #no return here
            # no return here
            if supplyConfigs == None: #If USB connection fails and there is no config section: just quit trying.....
                return (None, None, None)
            
            for aconfig in supplyConfigs:
                # check whether the sectionname of the config contains "SIGLENT"
                myconfig : BaseSupplyConfig = aconfig
                if "Siglent" in myconfig.devName: 
                    mydev = cls.SocketConnect(rm=rm, supplyConfig=myconfig)
                    if mydev != None:
    
                        idnRespStr=str(mydev.query("*IDN?"))
                        myidn = util.decodeIDN(idnstr=idnRespStr)
                        if myidn == None:
                            return (None,None)
                        for amodel in SiglentPowerSupply.KNOWN_MODELS:
                            if myidn.isModelInRange(amodel):
                                return (cls, 2, mydev)     
                            #No return here!
                        #No return here!
                    #No return here!
                #No return here!
            return (None, None, None)  # only return None here, after all options have been tried.    
        else:
            (None, None, None)
        
    
    def __init__(self, nrOfChan : int = None, dev : pyvisa.resources.MessageBasedResource = None):
        super().__init__(nrOfChan, dev)
        
        self.channels = list()
        for i in range(1, self.nrOfChan+1):
            self.channels.append({i:SPDChannel(i, dev)})
        
    def __exit__(self, *args):
        self.visaInstr.close()
    
    def chan(self, chanNr)-> SPDChannel:
        """Gets a channel, based on its index: 1, 2 etc."""
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None     
    
    def idn(self):
        """The command query identifies the instrument type and software version. The
        response consists of four different fields providing information on the
        manufacturer, the scope model, the serial number and the firmware revision.

        :return: Siglent Technologies,<model>,<serial_number>,<firmware>
        """
        return self.visaInstr.query("*IDN?")
   
