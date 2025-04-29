import time
import numpy as np
from enum import Enum
import socket
import pyvisa
import logging
import time
#from devices.BaseScope import BaseScope
from devices.siglent.sds.Channels import SDSChannel
from devices.siglent.sds.util import INR_HASHMAP
import devices.siglent.sds.util as util
from devices.BaseScope import BaseScope
from devices.siglent.sds.Vertical import SDSVertical
from devices.siglent.sds.Horizontal import SDSHorizontal
from devices.siglent.sds.Trigger import SDSTrigger

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SiglentWaveformWidth(Enum):
    BYTE = "BYTE"
    WORD = "WORD"

class SiglentScope(BaseScope):

    KNOWN_MODELS = [
        "SDS1000CFL",   #non-SPO model Series
        "SDS1000A",     #non-SPO model Series
        "SDS1000CML+",  #non-SPO model Series
        "SDS1000CNL+",  #non-SPO model Series
        "SDS1000DL+",   #non-SPO model Series
        "SDS1000E+",    #non-SPO model Series
        "SDS1000F+",    #non-SPO model Series
        "SDS2000",      #SPO model Series
        "SDS2000X",     #SPO model Series
        "SDS1000X",     #SPO model Series
        "SDS1000X+",    #SPO model Series
        "SDS1000X-E",   #SPO model Series
        "SDS1000X-C",   #SPO model Series
        #USED MODEL (TESTED) SHOWN BELOW
        "SDS2504X Plus",
        "SDS1202X",
        "SDS1202X-E",
    ]

    MANUFACTURERS = {
        "SDS2504X Plus": "Siglent",
        "SDS1202X": "Siglent",
    }
    
    @classmethod
    def getDevice(cls, rm: pyvisa.ResourceManager, urls, host):
        """
            Tries to get (instantiate) this device, based on matched url or idn response
            This method will ONLY be called by the BaseScope class, to instantiate the proper object during
            creation by the __new__ method of BaseScope.     
        """  
        if cls is SiglentScope:
            if host is None:
                pattern = "SDS"
                for url in urls:
                    if pattern in url:
                        mydev = rm.open_resource(url)
                        mydev.timeout = 10000  # ms
                        mydev.read_termination = '\n'
                        mydev.write_termination = '\n'
                        cls.__init__(cls, mydev)
                        return cls
                        
            else:
                try:
                    logger.info(f"Trying to resolve host {host}")
                    ip_addr = socket.gethostbyname(host)
                except socket.gaierror:
                    logger.error(f"Couldn't resolve host {host}")
                    return None
                mydev = rm.open_resource("TCPIP::"+str(ip_addr)+"::INSTR")
                cls.__init__(cls, mydev)
                return cls
        else:
            return None
            

    def __init__(self, dev = None, host = None):
        
        #self._inst = dev
        """ 
            Constructor for Tektronix TDS oscilloscoop. This class is a subclass of BaseScope. BaseScope implements
            the autoregristration scheme for subclasses of PEP487 which is available since python 3.6. 
        """
        #Edit 26-04-2025: commented line below. Calling super at this state will mess up the scope object creation
        #process.
        #super().__init__(dev) #baseclass will store referentie to the device.
        self.horizontal = SDSHorizontal(dev)
        self.vertical = SDSVertical(2, dev)
        self.trigger = SDSTrigger(self.vertical,dev)
    
    #TODO: move this to getDevice or to __init__
    def __enter__(self):
        try:
            dsc = self.query("*IDN?")
        except visa.errors.VisaIOError:
            self._inst.close()
            raise
        identity_items = dsc.split(",")
        if len(identity_items) == 3:
            model, _, _ = dsc.split(",")
            mnf = self.MANUFACTURERS.get(model, "[Unknown]")
        else:
            # Proper Siglent device probably.
            mnf, model, _, _ = identity_items
        logger.debug(f"Discovered {model} by {mnf}")
        if model not in self.KNOWN_MODELS:
            raise Exception(f"Device {model} not supported")
        return self

    def query(self, cmd: str):
        return self._inst.query(cmd)
    

    def __exit__(self, *args):
        self._inst.close()


    @property
    def idn(self):
        """
            The idn command query identifies the instrument type and software version. The
            response consists of four different fields providing information on the
            manufacturer, the scope model, the serial number and the firmware revision.

            return: Siglent Technologies,<model>,<serial_number>,<firmware>
        """
        return self._inst.query("*IDN?")
    
    def inr(self):
        """
            The INR? query reads and clears the contents of the INternal state change Register (INR). 
            The INR register (see table programming manual) records the completion of various internal operations 
            and state transitions.
        """
        inrResp = self._inst.query("*INR?")
        return INR_HASHMAP[inrResp]        
    
    def rst(self):
        """
            The RST command initiates a device reset. The RST sets recalls the default setup.
        """
        self._inst.write("*RST")
    
    def sav(self, panelNr):
        """
            The SAV command stores the current state of the instrument in internal memory. The SAV command stores 
            the complete front-panel setup of the instrument at the time the command is issued."""
        self._inst.write(f"*SAV{panelNr}")

    def rcl(self, panelNr):
        """
            The RCL command sets the state of the instrument, using one of the ten non-volatile panel setups, by 
            recalling the complete front-panel setup of the instrument. Panel setup 0 corresponds to the default panel 
            setup.
        """
        self._inst.write(f"*RCL{panelNr}")

    def lock(self, enable):
        """
            The LOCK command enables or disables the panel keyboard of the instrument.
        """
        if (enable):
            self._inst.write(f"LOCK ON")
        else:
            self._inst.write(f"LOCK OFF")
    
    def isLocked(self):
        retstr = self._inst.query(f"LOCK?")
        if (retstr=="LOCK ON"):
            return True
        else:
            return False
        
    def menu(self, enable):
        if (enable):
            self._inst.write(f"MENU ON")
        else:
            self._inst.write(f"MENU OFF")
    
    def define(self, funct, param):
        match funct:
            case util.MATH_FUNC_ADD:
                self._inst.write(f"DEFine EQN,'C1+C2'")
            case util.MATH_FUNC_SUB:
                self._inst.write(f"DEFine EQN,'C1-C2'")
            case util.MATH_FUNC_MUL:
                self._inst.write(f"DEFine EQN,'C1*C2'")
            case util.MATH_FUNC_DIF:
                self._inst.write(f"DEFine EQN,'C1/C2'")
            case util.MATH_FUNC_FFT:
                self._inst.write(f"DEFine EQN,'FFT({param})'")
            case util.MATH_FUNC_INT:
                self._inst.write(f"DEFine EQN,'INTG({param})'")
            case util.MATH_FUNC_DIF:
                self._inst.write(f"DEFine EQN,'DIFF({param})'")
            case util.MATH_FUNC_SQR:
                self._inst.write(f"DEFine EQN,'SQRT({param})'")


    """
    def timebase_scale(self, new_timebase):
        The command sets the horizontal scale per division for the main window.

        :param new_timebase: Value to set the horizontal timebase
    
        self.write(":TIMebase:SCALe {}".format(new_timebase))

    """
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

# moved to SDSChannel, but should be method of the scope
    #def get_trigger_status(self):
    #    """The command query returns the current state of the trigger.
    #
    #    :return: str
    #                Returns either "Arm", "Ready", "Auto", "Trig'd", "Stop", "Roll"
    #    """
    #    return self.query(":TRIGger:STATus?")

    #def get_waveform_preamble(self):
    #    """The query returns the parameters of the source using by the command
    #    :WAVeform:SOURce.
    #   """
    #    params = self.query_raw(":WAVeform:PREamble?")
    #    params = params[11:]
    #    total_points = struct.unpack('i', params[116:120])[0]
    #    probe = struct.unpack('f', params[328:332])[0]
    #    vdiv = struct.unpack('f', params[156:160])[0] * probe
    #    voffset = struct.unpack('f', params[160:164])[0] * probe
    #    code_per_div = struct.unpack('f', params[164:168])[0] * probe
    #    timebase = struct.unpack('h', params[324:326])[0]
    #    delay = struct.unpack('d', params[180:188])[0]
    #    interval = struct.unpack('f', params[176:180])[0]

    #    return (total_points, vdiv, voffset, code_per_div, timebase, delay, interval, delay)

    def autosetup(self):
        """ This command attempts to automatically adjust the trigger, vertical, and
        horizontal controls of the oscilloscope to deliver a usable display of the
        input signal. Autoset is not recommended for use on low frequency events
        (< 100 Hz).

        :return: Nothing
        """
        self.write(":AUToset")

    def set_trigger_run(self):
        """The command sets the oscilloscope to run
        """
        self.write(":TRIGger:RUN")

    def set_single_trigger(self):
        """The command sets the mode of the trigger.

        The backlight of SINGLE key lights up, the oscilloscope enters the
        waiting trigger state and begins to search for the trigger signal that meets
        the conditions. If the trigger signal is satisfied, the running state shows
        Trig'd, and the interface shows stable waveform. Then, the oscilloscope stops
        scanning, the RUN/STOP key becomes red, and the running status shows Stop.
        Otherwise, the running state shows Ready, and the interface does not display
        the waveform.

        :return: Nothing
        """
        self.write(":TRIGger:MODE SINGle")

    def set_normal_trigger(self):
        """The command sets the mode of the trigger.

        The oscilloscope enters the wait trigger state and begins to search for
        trigger signals that meet the conditions. If the trigger signal is satisfied,
        the running state shows Trig'd, and the interface shows stable waveform.
        Otherwise, the running state shows Ready, and the interface displays the last
        triggered waveform (previous trigger) or does not display the waveform (no
        previous trigger).

        :return: Nothing
        """
        self.write(":TRIGger:MODE NORMal")

    def set_auto_trigger(self):
        """The command sets the mode of the trigger.

        The oscilloscope begins to search for the trigger signal that meets the
        conditions. If the trigger signal is satisfied, the running state on the top
        left corner of the user interface shows Trig'd, and the interface shows stable
        waveform. Otherwise, the running state always shows Auto, and the interface
        shows unstable waveform.

        :return: Nothing
        """
        self.write(":TRIGger:MODE AUTO")

    def set_force_trigger(self):
        """The command sets the mode of the trigger.

        Force to acquire a frame regardless of whether the input signal meets the
        trigger conditions or not.

        :return: Nothing
        """
        self.write(":TRIGger:MODE FTRIG")

    def get_trigger_mode(self):
        """The query returns the current mode of trigger.

        :return: str
                    Returns either "SINGle", "NORMal", "AUTO", "FTRIG"
        """
        return self.query(":TRIGger:MODE?")

    def set_rising_edge_trigger(self):
        """The command sets the slope of the slope trigger to Rising Edge

        :return: Nothing
        """
        self.write(":TRIGger:SLOPe:SLOPe RISing")

    def set_falling_edge_trigger(self):
        """The command sets the slope of the slope trigger to Falling Edge

        :return: Nothing
        """
        self.write(":TRIGger:SLOPe:SLOPe FALLing")

    def set_alternate_edge_trigger(self):
        """The command sets the slope of the slope trigger to Falling Edge

        :return: Nothing
        """
        self.write(":TRIGger:SLOPe:SLOPe ALTernate")

    def get_edge_trigger(self):
        """The query returns the current slope of the slope trigger

        :return: str
                    Returns either "RISing", "FALLing", "ALTernate"
        """
        return self.query(":TRIGger:SLOPe:SLOPe?")

    def set_trigger_source(self):
        """The query returns the current trigger source of the slope trigger

        :param trig_channel: Trigger source
        """
        self.write(":TRIGger:SLOPe:SOURce {}".format(self._name))

    def set_trigger_edge_level(self, level: float):
        """The command sets the trigger level of the edge trigger

        :param level: Trigger level
        """

        """
        TODO: trigger level needs to be between:
        [-4.1*vertical_scale-vertical_offset, 4.1*vertical_scale-vertical_offset]
        """
        self.write(":TRIGger:EDGE:LEVel {}".format(str(level)))

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
        self.query("*OPC?")

    def default_setup(self):
        pass

class SiglentSDSTriggerStatus(Enum):
    ARM = "Arm"
    READY = "Ready"
    AUTO = "Auto"
    TRIGD = "Trig'd"
    STOP = "Stop"
    ROLL = "Roll"


class EthernetDevice(SiglentScope):
    def __init__(self, host: str):
        self._host = host
        super().__init__()

    def __enter__(self):
        try:
            logger.debug(f"Trying to resolve host {self._host}")
            ip_addr = socket.gethostbyname(self._host)
        except socket.gaierror:
            logger.error(f"Couldn't resolve host {self._host}")
        #mydev = vxi11.Instrument(ip_addr)
        rm = visa.ResourceManager()
        mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
        self._inst = mydev
        return super().__enter__()

    def write(self, cmd: str):
        self._inst.write(cmd)
        time.sleep(0.1)

    def query(self, cmd: str):
        return self._inst.query(cmd)

    def query_raw(self, message, *args, **kwargs):
        """
        Write a message to the scope and read a (binary) answer.

        This is the slightly modified version of :py:meth:`vxi11.Instrument.ask_raw()`.
        It takes a command message string and returns the answer as bytes.

        :param str message: The SCPI command to send to the scope.
        :return: Data read from the device
        """
        data = message.encode('utf-8')
        return self._inst.query(data, *args, **kwargs)

class SiglentIDN(object):
    def __init__(self) -> None:
        self._brand = None
        self._model = None
        self._serial = None
        self._firmware = None
        
    def decode(self, idnstr:str):
        """
        example
        Siglent Technologies,SDS1204X-E,SDS1EBAC0L0098,7.6.1.15
        """
        splitted = idnstr.split(",")
        if len(splitted) != 4:
            return False
        brand  = "Siglent"
        if brand in splitted[0]:
            if SiglentScope.KNOWN_MODELS in splitted[1]:
                if len(splitted[2]==14):
                    self._brand = splitted[0]
                    self._model = splitted[1]
                    self._serial = splitted[2]
                    self._firmware = splitted[3]
                    return True
        return False
            