import pyvisa
from devices.BaseSupply import BaseSupplyChannel

class SPDChannel(BaseSupplyChannel):
    def getSupplyChannelClass(cls,  chan_no, dev):
        if cls is SPDChannel:
            return cls
        else:
            return None     
         
    def __init__(self, chanNr : int = None, dev : pyvisa.resources.MessageBasedResource = None):
        super().__init__(chanNr=chanNr, dev=dev)
        self.name = f"CH{chanNr}"
        
    ####BaseClass methods######
    def enable(self, state: bool):
        """
            Turns this SupplyChannel object on or off
        """
        self.set_output(self, state)
    
    def measV(self):
        """
            Measures the actual voltage over the terminals of this channel.
        """
        return self.measure_voltage()
    
    def measI(self):
        """
            Measures the actual current delivered by this channel.
        """
        return self.measure_current()
    
    def setV(self, val):
        """
            Sets the desired voltage level of this channel.
        """
        self.set_voltage(val)
    
    def setV(self):
        """
            Gets the voltage setpoint of this channel.
        """
        self.get_voltage(val)
    
    def setI(self, val):
        """
            Sets the desired current level to be supplied bythis channel.
        """
        self.set_current(val)

    def setI(self):
        """
            Gets the current setpoint of this channel.
        """       
        self.get_current(val)

    #### SPD dedicated methods ######

    def set_output(self, status: bool):
        self.visaInstr.write(f"OUTP {self.name},{'ON' if status else 'OFF'}")

    def set_voltage(self, voltage: float):
        self.visaInstr.write(f"{self.name}:VOLT {voltage:.3f}")

    def set_current(self, current: float):
        self.visaInstr.write(f"{self.name}:CURR {current:.3f}")

    def get_voltage(self):
        return self.visaInstr.query(f"{self.name}:VOLT?")

    def get_current(self):
        return self.visaInstr.query(f"{self.name}:CURR?")

    def measure_voltage(self):
        return self.visaInstr.query(f"MEAS:VOLT? {self.name}")

    def measure_current(self):
        return self.visaInstr.query(f"MEAS:CURR? {self.name}")

    def measure_power(self):
        return self.visaInstr.query(f"MEAS:POWE? {self.name}")
