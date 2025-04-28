import pyvisa as visa
from enum import Enum
from devices.siglent.sdm.util import MeasType
import devices.siglent.sdm.util as util
import logging
import socket
from devices.BaseDMM import BaseDMM

logger = logging.getLogger(__name__)
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
    
class SiglentDMM(BaseDMM):

    @classmethod
    def getDevice(cls, rm, urls, host):
        """ Tries to get (instantiate) the device, based on the url. REMARK: this baseclass implementation is empty.
        Inheriting subclasses must implement this functionality."""
        urlPattern = "SDM" 
        if host == None:
            for url in urls:
                if urlPattern in url:
                    mydev = rm.open_resource(url)
                    mydev.timeout = 10000  # ms
                    mydev.read_termination = '\n'
                    mydev.write_termination = '\n'
                    
                    if cls is SiglentDMM:
                        cls.__init__(cls, mydev)
                        return cls
                    else:
                        return None        
        else:
            try:
                ip_addr = socket.gethostbyname(host)
                addr = 'TCPIP::'+str(ip_addr)+'::INSTR'
                mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                cls.__init__(cls,mydev)
                return cls
            except socket.gaierror:
                
                return None


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
    
    ###### VISA SYSTEM FUNCTIONS ########

    #TODO: define how to handle unsuccessfull connection.
    def __init__(self, dev=None):
        self.visaInstr  = dev
        self._query_delay = 0.0
        self.nrOfAttemps = 2
        
    def setQueryDelay(self, delay):
        if self.visaInstr != None:
            self._query_delay = delay
        
    def setTimeOut(self, timeOutms):
        if self.visaInstr != None:
            self.visaInstr.timeout = timeOutms
            
    ###### End VISA system functions ############
    
    ### DMM SYSTEM functions #####
    def setTriggerSrcEXT(self):
        self.visaInstr.write(f"SYSTem:PRESet")
        
    def close(self):
        self.visaInstr.close()
        
    def abort(self):
        self.visaInstr.write("ABOR")
        
    def __exit__(self, *args):
        self.visaInstr.close() 

    ### Trigger unit functions ####
        
    def getTriggerDelay(self):
        return self.visaInstr.query(f"TRIG:DEL?")
    
    def setTriggerDelay(self, val):
        self.visaInstr.write(f"TRIG:DEL {val}")
        
    def setTriggerCount(self, count):
        if count > 0 and count <=1000000:
            self.visaInstr.write(f"TRIG:COUN {count}")
    
    def setTriggerCont(self):
        self.visaInstr.write(f"TRIG:COUN INF")
        
    def setTriggerSrcIMM(self):
        self.visaInstr.write(f"TRIG:SOUR IMM")
        
    def setTriggerSrcBUS(self):
        self.visaInstr.write(f"TRIG:SOUR BUS")
        
    def setTriggerSrcEXT(self):
        self.visaInstr.write(f"TRIG:SOUR EXT")
        
    def dmmQuery(self, querystr):
        nr = 1
        while True:
            try:
                val = self.visaInstr.query(querystr, delay=self._query_delay)
                return val
            except visa.errors.VisaIOError:
                logging.info(f"VisaIOError occured {nr} time(s). Retrying .....")
                nr+=1
                if nr > self.nrOfAttemps:
                    logging.error(f"VisiaIOError occurred too often, raising error")
                    raise
        
        
    def get_voltage(self, type=MeasType.DC):
        meastype = util.checkMeasType(type)
        querystr = f"MEAS:VOLT:{meastype}?"
        return float(self.dmmQuery(querystr))
        
    def get_current(self, type=MeasType.DC):
        meastype = util.checkMeasType(type)
        querystr = f"MEAS:CURR:{meastype}?"   
        return float(self.dmmQuery(querystr))

    def get_capacitance(self, type=MeasType.DC):
        meastype = util.checkMeasType(type)   
        querystr = f"MEAS:CAP:{meastype}?"   
        return float(self.dmmQuery(querystr))

    def get_resistanceTW(self):
        querystr = f"MEAS:RES?"   
        return float(self.dmmQuery(querystr))
    
    def get_resistanceFW(self):
        querystr = f"MEAS:FRES?"   
        return float(self.dmmQuery(querystr))
    
    def get_frequency(self):
        querystr = f"MEAS:FREQ?"   
        return float(self.dmmQuery(querystr))
    
    def get_peroid(self):
        querystr = f"MEAS:PER?"   
        return float(self.dmmQuery(querystr))
    
    def get_diode(self):   
        querystr = f"MEAS:DIOD?"   
        return float(self.dmmQuery(querystr))
    
    def get_temp(self):   
        print("Not implemented yet")
        return None
    
    def fetch_res(self, rangeVal):
        querystr = f"FETC?"
        self.visaInstr.write(f"CONF:RES {rangeVal}")
        self.visaInstr.write(f"INIT")
        return float(self.dmmQuery(querystr))
    
    def setContinuity(self):
        self.visaInstr.write(f"CONF:CONT")
        
    def doDCMeas(self, val):
        querystr = f"FETC?"
        self.visaInstr.write(f"CONF:VOLT:DC")
        self.visaInstr.write(f"TRIG:SOUR IMM")
        self.visaInstr.write(f"TRIG:COUN {val}")
        return float(self.dmmQuery(querystr))
        
    
    def set_autorange_volt(self):
        self.visaInstr.write("TRIG:SOUR IMM")
        self.visaInstr.write("CONF:VOLT:AC AUTO")
        self.visaInstr.write("CONF:VOLT:DC AUTO")
    
    def set_autorange_res(self):
        self.visaInstr.write("CONF:RES AUTO")
        self.visaInstr.write("CONF:FRES AUTO")
        
    def set_autorange_curr(self):
        self.visaInstr.write("CONF:CURR:AC AUTO")
        self.visaInstr.write("CONF:CURR:DC AUTO")
    
    def set_currRangeDC(self, vrange: SDM3045X_CURR_RANGE):
        if range in SDM3045X_CURR_RANGE:
            self.visaInstr.write(f"CONF:CURR:DC {vrange}")
            
    def set_currRangeAC(self, vrange: SDM3045X_CURR_RANGE):
        if range in SDM3045X_CURR_RANGE:
            if vrange != SDM3045X_CURR_RANGE.R600muA or vrange != SDM3045X_CURR_RANGE.R6miA:
                self.visaInstr.write(f"CONF:CURR:DC {vrange}")
                
    def fetch_voltage(self):
        #self._inst.write("INIT")
        querystr = f"FETC?"
        self.visaInstr.write("CONF:VOLT:DC")
        self.visaInstr.write("TRIG:SOUR IMM") 
        self.visaInstr.write("INIT")
        return float(self.dmmQuery(querystr))