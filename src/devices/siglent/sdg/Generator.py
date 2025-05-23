import time
import struct
import numpy as np
from enum import Enum
import socket
import pyvisa as visa
import logging
import time
from devices.BaseGenerator import BaseGenerator
from devices.siglent.sdg.Channels import SDGChannel
#from sdg.util import IDN
from devices.siglent.sdg.util import IDN

logger = logging.getLogger("SiglentGenerator")
#logging.basicConfig(filename='siglentgenerator.log', level=logging.INFO)

class IDN():
   def __init__(self):
      self._frmt = None
      self._manufacturer = None
      self._model= None
      self._serialNr = None
      self._firmwareVer = None
      self._deviceId = None
      self._hardwareVer = None

   def decodeIDN(self, desc: str):
      if desc.find("*IDN") > -1: # it is a format 1 type of response
         return self.decodeFrmt1(desc)
         # buffer = np.fromstring(desc, sep=',')
      else:                       # it is a format 2 type of unknown response
         return self.decodeFrmt2(desc)
         
   def decodeFrmt1(self, desc: str):
      result = desc.split(",")
      length = len(result)
      self._manufacturer = None  # not available in this format
      self._frmt = 1
      match length:
         case 0:
               pass
         case 1:
               pass
         case 2:
               self._deviceId = result[1]
         case 3:
               self._deviceId = result[1]
               self._model = result[2]
         case 4:
               self._deviceId = result[1]
               self._model = result[2]
               self._serialNr = result[3]
         case 5:
               self._deviceId = result[1]
               self._model = result[2]
               self._serialNr = result[3]
               self._firmwareVer = result[4]
         case 6:
               self._deviceId = result[1]
               self._model = result[2]
               self._serialNr = result[3]
               self._firmwareVer = result[4]
               self._hardwareVer = result[5]
         case _:
               pass #strange situation.
               return False
      return True
    
   def decodeFrmt2(self, desc: str):
      result = desc.split(",")
      length = len(result)
      self._frmt = 2
      match length:
         case 0:
               pass
         case 1:
               self._manufacturer = result[0]
         case 2:
               self._manufacturer = result[0]
               self._model = result[1]
         case 3:
               self._manufacturer = result[0]
               self._model = result[1]
               self._serialNr = result[2]
         case 4:
               self._manufacturer = result[0]
               self._model = result[1]
               self._serialNr = result[2]
               self._firmwareVer = result[3]
         case _:
               self._manufacturer = result[0]
               self._model = result[1]
               self._serialNr = result[2]
               self._firmwareVer = result[3]
               self._deviceId = result[4]
      self._hardwareVer = None    # not available in this format
      return True
   
   def printIDN(self):
      retString = ""
      if self._manufacturer is not None:
         retString += " "+self._manufacturer
      if self._model is not None:
         retString += " " + self._model
      if self._deviceId is not None:
         retString += " " + self._deviceId
      if self._serialNr is not None:
         retString += " " + self._serialNr
      if self._hardwareVer is not None:
         retString += " " + self._hardwareVer

      return retString


class SiglentGenerator(BaseGenerator):
   KNOWN_MODELS = [
      "SDG1062X",
      "SDS1202X",
      "SDS1202X-E",
   ]

   MANUFACTURERS = {
      "SDS2504X Plus": "Siglent",
      "SDS1202X": "Siglent",
   }
   @classmethod 
   def decodeIDN(cls, idnquery):
      myidn = IDN()
      return myidn.decodeIDN(idnquery)


   @classmethod
   def getGeneratorClass(cls, rm, urls, host):
        """
            Tries to get (instantiate) this device, based on matched url or idn response
            This method will ONLY be called by the BaseScope class, to instantiate the proper object during
            creation by the __new__ method of BaseGenerator.     
        """    
        if cls is SiglentGenerator:
            urlPattern = "SDG" 
            if host == None:
                for url in urls:
                    if urlPattern in url:
                        mydev = rm.open_resource(url)
                        mydev.timeout = 10000  # ms
                        mydev.read_termination = '\n'
                        mydev.write_termination = '\n'
                        desc = mydev.query("*IDN?")
                        myidn = cls.decodeIDN(desc)
                        if myidn: #Found a valid Siglent Generator.
                            return (cls, mydev)
                        else:
                            return (None, None)
                            
            else:
                try:
                    ip_addr = socket.gethostbyname(host)
                    addr = 'TCPIP::'+str(ip_addr)+'::INSTR'
                    mydev = rm.open_resource('TCPIP::'+str(ip_addr)+'::INSTR')
                    cls.__init__(cls,mydev)
                    return (cls, mydev)
                except socket.gaierror:
                    print("Socket Error")
                    return (None, None)
        else:
            return (None, None)
    
   def __init__(self, host=None):
      self.visaInstr = None
      self.idn = None
      
      logger.info("SiglentGenerator found and generator object created.")
      self.CH1 = SDGChannel(1, self.visaInstr)
      self.CH2 = SDGChannel(2, self.visaInstr)

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