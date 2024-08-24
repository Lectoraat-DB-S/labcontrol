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

consoleHandler = logging.StreamHandler()
logger = logging.getLogger("sdg1025")
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)



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

   def __init__(self):
      rm = visa.ResourceManager()
      self._inst = None
      self._idn = IDN()
      theList = rm.list_resources()
      pattern = "SDG"
      for url in theList:
         if pattern in url:
            mydev = rm.open_resource(url)
            self._inst = mydev
            resp = self._inst.query("*IDN?")
            print(resp)
            self._idn.decodeIDN(resp)
            break
      self.CH1 = SDGChannel(1, self._inst)
      self.CH2 = SDGChannel(2, self._inst)
   """
   def __init__(self, url):
      pattern = "SDG"
      self._inst = None
      self._idn = IDN()
      rm = visa.ResourceManager()
      if pattern in url:
         mydev = rm.open_resource(url)
         self._inst = mydev
         self._idn.getIDN()
   """
   def __enter__(self):
      self._myIDN=IDN()
      try:
         dsc = self.query("*IDN?")
      except visa.errors.VisaIOError:
         self._inst.close()
         raise
      """ orginele code, maar die werkt niet goed.
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
      """
      self._myIDN = self._myIDN.getIDN(dsc)
      self.CH1 = SDGChannel(1, self)
      self.CH2 = SDGChannel(2, self)
      return self

   def getIDN(self):
      desc = self._inst.query("*IDN?")
      self._idn.decodeIDN(desc)
      return self._idn.printIDN()

       
   @classmethod
   def ethernet_device(cls, host: str):
      return EthernetDevice(host)

   @classmethod
   def usb_device(cls, visa_rscr: str = None):
      return USBDevice(visa_rscr)

   def __exit__(self, *args):
        self._inst.close()


class USBDevice(SiglentGenerator):
   def __init__(self, visa_rscr: str = None):
      self._visa_rscr = visa_rscr

   def __enter__(self):
      rm = visa.ResourceManager()
      if self._visa_rscr is None:
         logger.debug("Trying to auto-detect USB device")
         resources = rm.list_resources()
         for res_str in resources:
            if "SDG" in res_str:
               self._visa_rscr = res_str
         if self._visa_rscr is None:
            raise Exception("No device found")

      self._inst = rm.open_resource(self._visa_rscr)
      self._inst.write_termination = "\n"
      self._inst.read_termination = "\n"
      return super().__enter__()


   def write(self, cmd: str):
      self._inst.write(cmd)
      time.sleep(0.1)

   def query(self, cmd: str):
      self.write(cmd)
      rep = self._inst.read()
      time.sleep(0.1)
      return rep

class EthernetDevice(SiglentGenerator):
   def __init__(self, host: str):
      self._host = host

   def __enter__(self):
      try:
         logger.debug(f"Trying to resolve host {self._host}")
         ip_addr = socket.gethostbyname(self._host)
      except socket.gaierror:
         logger.error(f"Couldn't resolve host {self._host}")
      # mydev = vxi11.Instrument(ip_addr)
      print(ip_addr)
      rm = visa.ResourceManager()
      mydev = rm.open_resource('TCPIP::' + str(ip_addr) + '::INSTR')
      # print(mydev.query("*IDN?"))
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
