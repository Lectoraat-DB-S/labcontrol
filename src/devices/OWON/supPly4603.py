import pyvisa as visa

class OWONSupply(object):
    def __init__(self):
        self._dev = None
        #TODO state add.
        #self._state = NOTCONNECTED

    def open(self, url):
        #TODO: case url a) serieel b) usb c) TCP d) onbekend.
        rm = visa.ResourceManager()
        self._dev = rm.open_resource('TCPIP::' + str(url) + '::INSTR')

    """
    VOLTage <value>
    VOLTage?
    Sets and queries the voltage of the channel.
    Example
    VOLT 1          The command  sets the voltage of the channel to 1V.
    VOLT?           The command queries the voltage setting value of the channel.
    """
    def setVoltage(self, voltValue):
        command = f"VOLTage {voltValue}"
        self._dev.write(command)

    """
    VOLTage:LIMit <value>
    VOLTage:LIMit?
    Sets and queries the overvoltage protection (OVP) value of the channel.

    Example
    VOLT:LIM 1      The command sets the overvoltage protection (OVP) value of the channel to 1V.
    VOLT:LIM?       The command  queries the overvoltage protection (OVP) value of the channel.
    """

    def setVoltageLimit(self, voltValue):
        command = f"VOLTage:LIMit {voltValue}"
        self._dev.write(command)

    """
    MEASure:VOLTage?
    Query the voltage measured on the output terminal of the channel.
    Example
    The voltage measured on the output terminal of the channel is 1V.
    MEAS:VOLT?
    Returns
    1.000
    """
    def getVoltage(self, voltValue):
        return self._dev.query("MEASure:VOLTage?")

    """
    CURRent?
    CURRent <value>
    Sets and queries the current of the channel.

    example
    CURR? queries the current setting value of the channel.
    CURR 1  sets the output current to 1A

    """
    def setCurrent(self, voltValue):
        command = f"CURRent {voltValue}"
        self._dev.write(command)

    def getCurrent(self, voltValue):
        return self._dev.query("CURRent?")

    def idn(self):
        response = self._dev.query("*IDN?")
        #TODO decode response. Is probably a ASCII string.
        """
        split_list = response.split(",")
        nrOfElements = range(len(split_list))
        if nrOfElements = 4:
        
        for substr in splitted:
            
        """

"""
*IDN?
Return Format
OWON,<model>,<serial number>,FV:X.XX.XX
<model>：the model number of the instrument.
<serial number>：the serial number of the instrument.
FV:X.XX.XX：the software version of the instrument.

*RST
Resets the device


MEASure:CURRent?
Query the current measured on the output terminal of the channel.
Example
MEAS:CURR?

MEASure:POWer?
Query the power measured on the output terminal of the channel.
Example
MEAS:POW?

OUTPut

Syntax
OUTPut {0|1|ON|OFF}
Example
OUTP ON

OUTPut?
Example: OUTP? Returns 1 if on, 0 otherwise





CURRent:LIMit <value>
CURRent:LIMit?
Sets and queries the overcurrent protection (OCP) value of the channel.
Example
CURR:LIM 1      The command sets the overcurrent protection (OCP) value of the channel to 1A.
CURR:LIM?       The command queries the overcurrent protection (OCP) value of the channel.
"""
