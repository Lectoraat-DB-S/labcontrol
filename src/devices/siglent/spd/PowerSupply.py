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
    def getDevice(cls, rm, urls, host):
        mydev = None
        if host is None:
            pattern = "SPD"
            for url in urls:
                if pattern in url:
                    mydev = rm.open_resource(url)
                    mydev.timeout = 10000  # ms
                    mydev.read_termination = '\n'
                    mydev.write_termination = '\n'
                    break
        else:
            try:
                logger.info(f"Trying to resolve host {host}")
                ip_addr = socket.gethostbyname(host)
                mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
            except socket.gaierror:
                logger.error(f"Couldn't resolve host {host}")
                mydev = None
        
        if mydev != None:
            if cls is SiglentPowerSupply:
                cls.__init__(cls,dev=mydev)
                return cls
            else:
                return None  

        return mydev #always return something even it is None.

    def __init__(self, dev= None, host=None, nrOfChan=2):
        self.visaInstr : pyvisa.Resource = dev
        
        self.host = host
        self.nrOfChan = nrOfChan
        for i in range(1, self.nrOfChan+1):
            self.channels.append({i:SPDChannel(i, dev)})
        
    
    def __exit__(self, *args):
        self.visaInstr.close()
    
    def idn(self):
        """The command query identifies the instrument type and software version. The
        response consists of four different fields providing information on the
        manufacturer, the scope model, the serial number and the firmware revision.

        :return: Siglent Technologies,<model>,<serial_number>,<firmware>
        """
        return self.visaInstr.query("*IDN?")
   
