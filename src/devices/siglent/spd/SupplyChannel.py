import pyvisa as visa

class SPDChannel(object):
    def __init__(self, chan_no: int, dev):
        self._name = f"CH{chan_no}"
        self._inst = dev

    def set_output(self, status: bool):
        print(f"OUTP {self._name},{'ON' if status else 'OFF'}")
        self._inst.write(f"OUTP {self._name},{'ON' if status else 'OFF'}")

    def set_voltage(self, voltage: float):
        self._inst.write(f"{self._name}:VOLT {voltage:.3f}")

    def set_current(self, current: float):
        self._inst.write(f"{self._name}:CURR {current:.3f}")

    def get_voltage(self):
        return self._inst.query(f"{self._name}:VOLT?")

    def get_current(self):
        return self._inst.query(f"{self._name}:CURR?")

    def measure_voltage(self):
        return self._inst.query(f"MEAS:VOLT? {self._name}")

    def measure_current(self):
        return self._inst.query(f"MEAS:CURR? {self._name}")

    def measure_power(self):
        return self._inst.query(f"MEAS:POWE? {self._name}")
