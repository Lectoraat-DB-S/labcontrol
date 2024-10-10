import pyvisa as visa
from enum import Enum
from devices.siglent.sdm.util import MeasType
import devices.siglent.sdm.util as util
import logging
import socket

logger = logging.getLogger(__name__)
logging.basicConfig(filename='Siglentscope.log', level=logging.INFO)
logger.setLevel(logging.DEBUG)

class SDM3045X_CURR_RANGE(Enum):
    R600muA = 1
    R6miA   = 2
    R60miA  = 3
    R600miA = 4
    R6A     = 5
    R10A    = 6
    AUTO    = 7 
    
#   According to SDM programming manual page 44:
# Storing measurements in reading memory with INITiate
# is faster than sending measurements to the
# instrument's output buffer using READ? (provided you do not send FETCh? until done). The INITiate
# command is also an "overlapped" command. This means that after executing INITiate, you can send other
# commands tha t do not affect the measurements. This allows you to check for data availability before
# initiating a read attempt that might otherwise time out. Note that the FETCh? query waits until all
# measurements are complete to terminate. You can store up to 1,000 0 m easurements in the reading
# memory of the SDM.
    
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

    ### Trigger unit functions ####
        
    def getTriggerDelay(self):
        return self._inst.query(f"TRIG:DEL?")
    
    def setTriggerDelay(self, val):
        self._inst.write(f"TRIG:DEL {val}")
        
    def setTriggerCount(self, count):
        if count > 0 and count <=1000000:
            self._inst.write(f"TRIG:COUN {count}")
    
    def setTriggerCont(self):
        self._inst.write(f"TRIG:COUN INF")
        
    def setTriggerSrcIMM(self):
        self._inst.write(f"TRIG:SOUR IMM")
        
    def setTriggerSrcBUS(self):
        self._inst.write(f"TRIG:SOUR BUS")
        
    def setTriggerSrcEXT(self):
        self._inst.write(f"TRIG:SOUR EXT")
        
    def get_voltage(self, type=MeasType.DC):
        meastype = util.checkMeasType(type)   
        return self._inst.query(f"MEAS:VOLT:{meastype}?") 
    
    def get_current(self, type=MeasType.DC):
        meastype = util.checkMeasType(type)   
        return float(self._inst.query(f"MEAS:CURR:{meastype}?"))

    def get_capacitance(self, type=MeasType.DC):
        meastype = util.checkMeasType(type)   
        return self._inst.query(f"MEAS:CAP:{meastype}?")

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
    
    def fetch_res(self, rangeVal):
        self._inst.write(f"CONF:RES {rangeVal}")
        self._inst.write(f"INIT")
        return self._inst.query(f"FETC?")
    
    def setContinuity(self):
        self._inst.write(f"CONF:CONT")
        
    def doNDCMeas(self, val):
        self._inst.write(f"CONF:VOLT:DC")
        self._inst.write(f"TRIG:SOUR IMM")
        self._inst.write(f"TRIG:COUN {val}")
        return self._inst.query(f"FETC?")
        
    
    def set_autorange_volt(self):
        self._inst.write("TRIG:SOUR IMM")
        self._inst.write("CONF:VOLT:AC AUTO")
        self._inst.write("CONF:VOLT:DC AUTO")
    
    def set_autorange_res(self):
        self._inst.write("CONF:RES AUTO")
        self._inst.write("CONF:FRES AUTO")
        
    def set_autorange_curr(self):
        self._inst.write("CONF:CURR:AC AUTO")
        self._inst.write("CONF:CURR:DC AUTO")
    
    def set_currRangeDC(self, vrange: SDM3045X_CURR_RANGE):
        if range in SDM3045X_CURR_RANGE:
            self._inst.write(f"CONF:CURR:DC {vrange}")
            
    def set_currRangeAC(self, vrange: SDM3045X_CURR_RANGE):
        if range in SDM3045X_CURR_RANGE:
            if vrange != SDM3045X_CURR_RANGE.R600muA or vrange != SDM3045X_CURR_RANGE.R6miA:
                self._inst.write(f"CONF:CURR:DC {vrange}")
                
    def fetch_voltage(self):
        #self._inst.write("INIT")
        
        self._inst.write("CONF:VOLT:DC")
        self._inst.write("TRIG:SOUR IMM") 
        self._inst.write("INIT")
        return self._inst.query("FETCh?")