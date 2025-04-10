import pyvisa as visa

class SPDChannel(object):
    def __init__(self, chan_no: int, dev):
        self._name = f"CH{chan_no}"
        self.visaInstr = dev

    ####BaseClass methods######
    def enable(self, state: bool):
        """
            Turns this channel on or off
        """
        self.set_output(self, state)
    
    def setOCP(self, val):
        pass
    
    def setOVP(self, val):
        pass
    
    def measV(self):
        return self.get_voltage()
    
    def measI(self):
        return self.get_current()
    
    def setV(self, val):
        self.set_voltage(val)
    
    def setI(self, val):
        self.set_current(val)

    #### SPD dedicated methods ######

    def set_output(self, status: bool):
        self.visaInstr.write(f"OUTP {self._name},{'ON' if status else 'OFF'}")

    def set_voltage(self, voltage: float):
        self.visaInstr.write(f"{self._name}:VOLT {voltage:.3f}")

    def set_current(self, current: float):
        self.visaInstr.write(f"{self._name}:CURR {current:.3f}")

    def get_voltage(self):
        return self.visaInstr.query(f"{self._name}:VOLT?")

    def get_current(self):
        return self.visaInstr.query(f"{self._name}:CURR?")

    def measure_voltage(self):
        return self.visaInstr.query(f"MEAS:VOLT? {self._name}")

    def measure_current(self):
        return self.visaInstr.query(f"MEAS:CURR? {self._name}")

    def measure_power(self):
        return self.visaInstr.query(f"MEAS:POWE? {self._name}")
