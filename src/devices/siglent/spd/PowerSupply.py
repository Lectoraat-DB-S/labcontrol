import pyvisa as visa
import logging
import socket
from devices.siglent.spd.SupplyChannel import SPDChannel

logger = logging.getLogger(__name__)
logging.basicConfig(filename='SiglentSupply.log', level=logging.INFO)
logger.setLevel(logging.INFO)


class SiglentPowerSupply(object):
    KNOWN_MODELS = [
        "SPD3303X",
    ]

    MANUFACTURERS = {
        "SPD3303X": "Siglent",
        
    }

    def __init__(self, host=None):
        rm = visa.ResourceManager()
        self._inst = None
        #self._idn = IDN()
        if host is None:
         theList = rm.list_resources()
         pattern = "SPD"
         for url in theList:
            if pattern in url:
               mydev = rm.open_resource(url)
               self._inst = mydev
               resp = self._inst.query("*IDN?")
               #self._idn.decodeIDN(resp)
               break
        else:
            self._host = host
            try:
                logger.info(f"Trying to resolve host {self._host}")
                ip_addr = socket.gethostbyname(self._host)
                mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                self._inst = mydev
            except socket.gaierror:
                logger.error(f"Couldn't resolve host {self._host}")

        self.CH1 = SPDChannel(1, self._inst)
        self.CH2 = SPDChannel(2, self._inst)

    
    def __exit__(self, *args):
        self._inst.close()

    def query(self, cmd: str):
        return self._inst.query(cmd)

    @property
    def idn(self):
        """The command query identifies the instrument type and software version. The
        response consists of four different fields providing information on the
        manufacturer, the scope model, the serial number and the firmware revision.

        :return: Siglent Technologies,<model>,<serial_number>,<firmware>
        """
        return self.query("*IDN?")
   
