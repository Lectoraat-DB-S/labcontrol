#wil er nog een factory iets in programmeren, zie voorbeeld en uitleg op https://realpython.com/factory-method-python/
import time
import vxi11
import struct
import numpy as np
from enum import Enum
import socket
import pyvisa as visa
import logging
import time
import xdrlib
import sds
import pyvisa
#from sds.Scopes import SiglentScope

class Device(object)

    def write(self, cmd: str):
        pass

    def query(self, cmd: str):
        pass

class USBDevice(Device):
    def __init__(self, visa_rscr: str = None):
        self._visa_rscr = visa_rscr

    def __enter__(self):
        rm = pyvisa.ResourceManager("@py")
        if self._visa_rscr is None:
            logger.debug("Trying to auto-detect USB device")
            resources = rm.list_resources()
            for res_str in resources:
                if "SPD3XID" in res_str:
                    self._visa_rscr = res_str
            if self._visa_rscr is None:
                raise Exception("No device found")

        self._inst = rm.open_resource(self._visa_rscr)
        self._inst.write_termination = "\n"
        self._inst.read_termination = "\n"
        return self._inst

    def write(self, cmd: str):
        self._inst.write(cmd)
        time.sleep(0.1)

    def query(self, cmd: str):
        self.write(cmd)
        rep = self._inst.read()
        time.sleep(0.1)
        return rep

class EthernetDevice(Device):
    def __init__(self, host: str):
        self._host = host
        self._inst = None

    def __enter__(self):
        try:
            logger.debug(f"Trying to resolve host {self._host}")
            ip_addr = socket.gethostbyname(self._host)
        except socket.gaierror:
            logger.error(f"Couldn't resolve host {self._host}")
        mydev = vxi11.Instrument(ip_addr)
        self._inst = mydev
        return mydev

    def write(self, cmd: str):
        self._inst.write(cmd)
        time.sleep(0.1)
        
    def query(self, cmd: str):
        return self._inst.ask(cmd)
