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
from devices.siglent.sdg.Channels import SDGChannel
#from sdg.util import IDN
from devices.siglent.sdg.util import IDN
from devices.siglent.sdg.Commands import WaVeformTyPe

logger = logging.getLogger("SiglentGenerator")
logging.basicConfig(filename='siglentgenerator.log', level=logging.INFO)


class SiglentGenerator(object):
   KNOWN_MODELS = [
      "SDG1062X",
      "SDS1202X",
      "SDS1202X-E",
   ]

   MANUFACTURERS = {
      "SDS2504X Plus": "Siglent",
      "SDS1202X": "Siglent",
   }

   def __init__(self, host=None):
      self._inst = None
      rm = visa.ResourceManager()
      self._idn = IDN()
      if host is None:
         theList = rm.list_resources()
         pattern = "SDG"
         for url in theList:
            if pattern in url:
               mydev = rm.open_resource(url)
               self._inst = mydev
               resp = self._inst.query("*IDN?")
               self._idn.decodeIDN(resp)
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
            
      logger.info("SiglentGenerator found and generator object created.")
      self.CH1 = SDGChannel(1, self._inst)
      self.CH2 = SDGChannel(2, self._inst)

   def __enter__(self):
      return self

   def getIDN(self):
      desc = self._inst.query("*IDN?")
      self._idn.decodeIDN(desc)
      return self._idn.printIDN()

   def __exit__(self, *args):
        self._inst.close()

   def query(self, cmd: str):
      return self._inst.query(cmd)