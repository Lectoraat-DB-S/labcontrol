import pyvisa as visa
import enum
from devices.siglent.sdm.util import MeasType
import devices.siglent.sdm.util as util
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='Siglentscope.log', level=logging.INFO)
logger.setLevel(logging.DEBUG)

class SiglentDMM(object):
    KNOWN_MODELS = [
        "SDM3045X",
        "SDM3055",
        "SDM3065X",
    ]

    MANUFACTURERS = {
        "SDM3045X": "Siglent",
        "SDM3055": "Siglent",
        "SDM3065X": "Siglent",
    }

    #TODO: define how to handle unsuccessfull connection.
    def __init__(self, host=None):
        rm = visa.ResourceManager()
        self._inst = None
        if host is None:
            theList = rm.list_resources()
            pattern = "SDM"
            for url in theList:
                if pattern in url:
                    mydev = rm.open_resource(url)
                    self._inst = mydev
                    logger.info("Siglent SDM found")
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
        
        
    def close(self):
        self._inst.close()
        
    def abort(self):
        self._inst.write("ABOR")
        
    def __exit__(self, *args):
        self._inst.close() 
        
    
        
 
    """
        get_voltage: measure the voltage 
        parameters:
            No parameters: E.g. MEAS:VOLT:DC? Measures DC voltage in auto range.
    """
    def get_voltage(self, type=MeasType.DC):
            """
            see https://stackoverflow.com/questions/35407477/enums-in-python-how-to-enforce-in-method-arguments
            in how to handle enum as formal parameter.
            """
            meastype = util.checkMeasType(type)   
            """
            TODO:
            1. check the space between semicolon and the value. Space shown in example of SDM manual, but not in conmmandsyntax
            2. Incorperate the correct ranges per model DMM
            """
            return self._inst.query(f"MEAS:VOLT:{meastype}?") 
    
    def get_current(self, type=MeasType.DC):
        meastype = util.checkMeasType(type)   
        return self._inst.query(f"MEAS:CURR:{meastype}?")

    def get_capacitance(self, type=MeasType.DC):
        meastype = util.checkMeasType(type)   
        return self._inst.query(f"MEAS:CAP:{meastype}?")

    """
        get_resistance: measures resistance, TW = Two Wire, FW = Four Wire.
        
        TODO: add range per model number. See manual.
    """
    def get_resistanceTW(self):
        return float(self._inst.query(f"MEAS:RES?"))

    def get_resistanceFW(self):
        return self._inst.query(f"MEAS:FRES?")

    def get_frequency(self):
        return self._inst.query(f"MEAS:FREQ?")

    def get_peroid(self):
        return self._inst.query(f"MEAS:PER?")

    def get_diode(self):   
        return self._inst.query(f"MEAS:DIOD?")
    
    def get_temp(self):   
        print("Not implemented yet")
        return None
    