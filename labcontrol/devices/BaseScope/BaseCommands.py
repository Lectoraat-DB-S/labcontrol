import pyvisa
from devices.BaseLabDeviceUtils import SCPICommand, SCPIParam

class Command(object):
    """A class for holding all kinds of oscilloscope commands"""
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource=None):
        self.visaInstr : pyvisa.resources.MessageBasedResource = visaInstr
        self.IEEE488 = IEEE488Command.getIEEE488CommandClass(visaInstr) #try to instantiate the proper subclass type object bij the factory
        self.scpiParam = SCPIParam()
        self.scpiCommand = SCPICommand()

class IEEE488Command(object):
    
    IEEE488CommandList = []        
    
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource=None):
        self.visaInstr : pyvisa.resources.MessageBasedResource = visaInstr
    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of Scope subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        Working principle: at run time, Python will traverse all objects in the path. If one supplies the path to the subclass in one of the files
        in the path, Python will find the class, and add it to the scopeList. This list will be traversed during a call to this baseclass getDevice method,
        which implements a factory kind of pattern in order to be able to return the correct driver object for a physically conntected oscilloscope.
        """
        super().__init_subclass__(**kwargs)
        cls.IEEE488CommandList.append(cls)
         
    @classmethod
    def getIEEE488CommandClass(cls, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """Method for getting the right (sub)classtype of IEEE$88Commands, in order for the runtime to instantiate the correct object.
        This base class implementation does absolutely nothing. Therefore, the subclass has to implement the logic for returning the property classtype."""
        pass
    
    def write(self, cmd):
        self.visaInstr.write(cmd)
        
    def query(self, cmd):
        return self.visaInstr.query(cmd)
    
    def STB(self):
        resp = self.visaInstr.query("*STB?")
        return resp

    def OPC(self):
        """Method for sending an *OPC? query to the instrument. The *OPC? query places a 1 in the Output Queue once an operation that  
        generates an OPC message is complete. The *OPC? query does not return until all pending OPC operations have completed. Therefore, 
        your time-out must be set to a time at least if the longest expected time for the operations to complete.
        """
        pass

    def SAV(self):
        pass

    def RST(self):
        pass

    def INR(self):
        pass
    
    def getINR(self):
        pass

    def STB(self):
        return self.visaInstr.read_stb()

    def SRE(self):
        pass

    def ESE(self, newValue = None):
        pass        
    
    def getESE(self):
        pass
    
    def CMR(self):
        pass
    
    def getCMR(self):
        pass
    
    def CLS(self):
        pass

    def DDR(self):
        pass


    def EXR(self):
        pass
    
    def getEXR(self):
        pass
    
    def ESR(self):
        pass
    
    def getESR(self):
        pass
    
    def URR(self):
        pass
    
    def getSTB(self):
        pass