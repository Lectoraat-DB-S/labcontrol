import pyvisa
import logging
import socket
from devices.siglent.spd.SupplyChannel import SPDChannel
from devices.BaseSupply import BaseSupply

logger = logging.getLogger(__name__)
#logging.basicConfig(filename='SiglentSupply.log', level=logging.INFO)
logger.setLevel(logging.INFO)

class SiglentPowerSupply(BaseSupply):
    KNOWN_MODELS = [
        "SPD3303X",
    ]

    MANUFACTURERS = {
        "SPD3303X": "Siglent",  
    }

    @classmethod
    def getSupplyClass(cls, rm:pyvisa.ResourceManager, urls:list, host:str):
        if rm == None:
            raise Exception("Siglent Powersupply: ERROR: VISA ResourceManager empty")
        mydev = None
        if host is None:
            pattern = "SPD"
            for url in urls:
                if pattern in url:
                    mydev = rm.open_resource(url)
                    mydev.timeout = 10000  # ms
                    mydev.read_termination = '\n'
                    mydev.write_termination = '\n'
                    #TODO: idn nog decoderen en aantal kanalen daarop instellen!
                    return (cls, 2, mydev)
                else:
                    return (None, None, None)
                    
        else:
            try:
                logger.info(f"Trying to resolve host {host}")
                ip_addr = socket.gethostbyname(host)
                mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                return (cls, 2, mydev)
            except socket.gaierror:
                logger.error(f"Couldn't resolve host {host}")
                mydev = None
                return (None, None, None)
        return (None, None, None)
    
    def __init__(self, nrOfChan : int = None, dev : pyvisa.resources.MessageBasedResource = None):
        super.__init__(nrOfChan, dev)
        
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
   
