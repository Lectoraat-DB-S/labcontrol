import pyvisa as visa
from siglent.spd.SupplyChannel import SPDChannel

class SiglentPowerSupply(object):
    KNOWN_MODELS = [
        "SPD3303X",
    ]

    MANUFACTURERS = {
        "SPD3303X": "Siglent",
        
    }

    def __init__(self):
        rm = visa.ResourceManager()
        self._inst = None
        #self._idn = IDN()
        theList = rm.list_resources()
        pattern = "SPD"
        for url in theList:
            if pattern in url:
                mydev = rm.open_resource(url)
                #mydev.write_termination='\n' #Modify termination character
                #mydev.read_termination='\n' #Modify termination character
                self._inst = mydev
                #resp = self._inst.query("*IDN?\n")
                #print(resp)
                #self._idn.decodeIDN(resp)
                break
        self.CH1 = SPDChannel(1, self._inst)
        self.CH2 = SPDChannel(2, self._inst)

    
    def __exit__(self, *args):
        self._inst.close()


    #def query_raw(self, message, *args, **kwargs):
    #    """
    #    Write a message to the scope and read a (binary) answer.

    #    This is the slightly modified version of :py:meth:`vxi11.Instrument.ask_raw()`.
    #    It takes a command message string and returns the answer as bytes.

    #    :param str message: The SCPI command to send to the scope.
    #    :return: Data read from the device
     #   """
    #    data = message.encode('utf-8')
    #    return self._inst.ask_raw(data, *args, **kwargs)

    @property
    def idn(self):
        """The command query identifies the instrument type and software version. The
        response consists of four different fields providing information on the
        manufacturer, the scope model, the serial number and the firmware revision.

        :return: Siglent Technologies,<model>,<serial_number>,<firmware>
        """
        return self.query("*IDN?")
   
