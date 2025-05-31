import sys

class HantekScope(object):

    def __init__(self):
        self.scope = Oscilloscope()
        self.scope.setup()
        if not self.scope.open_handle():
            sys.exit( -1 )

        # upload correct firmware into device's RAM
        if (not self.scope.is_device_firmware_present):
            self.scope.flash_firmware()

        # read calibration values from EEPROM
        calibration = self.scope.get_calibration_values()

        # set interface: 0 = BULK, >0 = ISO, 1=3072,2=2048,3=1024 bytes per 125 us
        self.scope.set_interface( 0 ) # use BULK unless you have specific need for ISO xfer

        self.scope.set_num_channels( channels )
        self.scope.set_sample_rate(1)
        self.scope.set_ch1_voltage_range(1)
        self.scope.set_ch2_voltage_range(1)

