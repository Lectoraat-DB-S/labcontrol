"""
HantekBaseScope: Integration of Hantek 6022 scopes into the BaseScope framework
This module provides a wrapper around the Hantek6022API to make it compatible
with the BaseScope/BaseChannel interface used throughout labcontrol.

Supported models: DSO-6022BE, DSO-6022BL, DSO-6021
"""

import time
from threading import Event

import numpy as np
import usb1

from devices.BaseConfig import BaseScopeConfig
from devices.BaseScope import (
    BaseAcquisition,
    BaseChannel,
    BaseDisplay,
    BaseHorizontal,
    BaseScope,
    BaseTriggerUnit,
    BaseVertical,
    BaseWaveForm,
    BaseWaveFormPreample,
)
from devices.Hantek6022API.PyHT6022.LibUsbScope import Oscilloscope


class HantekWaveFormPreamble(BaseWaveFormPreample):
    """Waveform preamble for Hantek scopes"""

    @classmethod
    def getWaveFormPreableClass(cls, dev=None):
        if cls is HantekWaveFormPreamble:
            return cls
        return None

    def __init__(self, scope_obj=None):
        super().__init__(dev=None)  # Hantek doesn't use VISA
        self.scope_obj = scope_obj

    def queryPreamble(self, channel_num, voltage_range, sample_rate_index):
        """Set preamble data based on Hantek settings"""
        if self.scope_obj is None:
            return

        # Get voltage range info
        vr_info = Oscilloscope.VOLTAGE_RANGES.get(voltage_range, ('+/- 5V', 0.0390625, 2.5))
        sr_info = Oscilloscope.SAMPLE_RATES.get(sample_rate_index, ('1 MS/s', 1e6))

        self.sourceChanStr = f"CH{channel_num}"
        self.yUnitStr = "V"
        self.xUnitStr = "s"
        self.ymult = vr_info[1]  # V/div scaling factor
        self.yzero = 0  # Hantek centers around 0
        self.yoff = 128  # 8-bit ADC center
        self.vdiv = vr_info[2]  # Voltage per division
        self.xincr = 1.0 / sr_info[1]  # Time between samples
        self.nrOfSamples = 0  # Will be set when data is captured
        self.timeDiv = self.xincr * 100  # Approximation
        self.couplingstr = "AC"  # Default
        self.acqModeStr = "SAMPLE"
        self.probe = 1.0  # Default probe attenuation


class HantekChannel(BaseChannel):
    """Hantek scope channel implementation"""

    @classmethod
    def getChannelClass(cls, dev):
        if cls is HantekChannel:
            return cls
        return None

    def __init__(self, chan_no: int, scope_obj: Oscilloscope):
        super().__init__(chan_no, None)  # No VISA instrument
        self.scope_obj = scope_obj
        self.name = f"CH{chan_no}"
        self.chanNr = chan_no
        self.WFP = HantekWaveFormPreamble(scope_obj)
        self.WF = BaseWaveForm()
        self._voltage_range = 1  # Default: +/- 5V
        self._coupling = self.scope_obj.DC
        self._visible = True

    def capture(self) -> BaseWaveForm:
        """Capture waveform from this channel"""
        # Request single capture
        self.scope_obj.start_capture()

        # Read data synchronously
        data_available = Event()
        captured_data = []

        def callback(ch1_data, ch2_data):
            if self.chanNr == 1:
                captured_data.append(ch1_data)
            else:
                captured_data.append(ch2_data)
            data_available.set()

        # Start async read with callback
        shutdown = self.scope_obj.read_async(callback, 6*1024, outstanding_transfers=1, raw=True)

        # Wait for data (with timeout)
        data_available.wait(timeout=2.0)
        shutdown.set()

        if not captured_data:
            raise RuntimeError(f"No data captured from {self.name}")

        # Process raw data
        raw_data = np.array(captured_data[0], dtype=np.uint8)

        # Update preamble
        sample_rate_idx = getattr(self.scope_obj, '_sample_rate_index', 1)
        self.WFP.queryPreamble(self.chanNr, self._voltage_range, sample_rate_idx)
        self.WFP.nrOfSamples = len(raw_data)

        # Scale data to voltage
        vr_info = Oscilloscope.VOLTAGE_RANGES[self._voltage_range]
        scale_factor = vr_info[1]  # V per ADC step
        offset_volts = vr_info[2]  # Zero offset

        scaled_data = (raw_data.astype(np.float32) - 128) * scale_factor

        # Create time axis
        time_data = np.arange(len(raw_data)) * self.WFP.xincr

        # Update waveform
        self.WF.setWaveForm(self.WFP)
        self.WF.rawYdata = raw_data.tolist()
        self.WF.rawXdata = list(range(len(raw_data)))
        self.WF.scaledYdata = scaled_data.tolist()
        self.WF.scaledXdata = time_data.tolist()

        return self.WF

    def setVdiv(self, value):
        """Set voltage range - map to closest Hantek range"""
        # Map voltage/div to Hantek voltage ranges
        # Hantek ranges: 1=5V, 2=2.5V, 5=1V, 10=0.5V
        if value >= 1.0:
            self._voltage_range = 1  # +/- 5V
        elif value >= 0.5:
            self._voltage_range = 2  # +/- 2.5V
        elif value >= 0.2:
            self._voltage_range = 5  # +/- 1V
        else:
            self._voltage_range = 10  # +/- 500mV

        if self.chanNr == 1:
            self.scope_obj.set_ch1_voltage_range(self._voltage_range)
        else:
            self.scope_obj.set_ch2_voltage_range(self._voltage_range)

    def getVdiv(self):
        """Get current voltage per division"""
        vr_info = Oscilloscope.VOLTAGE_RANGES[self._voltage_range]
        return vr_info[2]  # Return voltage per division

    def setCoupling(self, coupling):
        """Set AC/DC coupling"""
        if coupling.upper() == "AC":
            self._coupling = self.scope_obj.AC
        else:
            self._coupling = self.scope_obj.DC

        # Update scope AC/DC settings using the correct Hantek API method
        if self.chanNr == 1:
            self.scope_obj.set_ch1_ac_dc(self._coupling)
        else:
            self.scope_obj.set_ch2_ac_dc(self._coupling)

    def getCoupling(self):
        """Get coupling mode"""
        return "AC" if self._coupling == self.scope_obj.AC else "DC"

    def setVisible(self, state: bool):
        """Set channel visibility (cosmetic only for Hantek)"""
        self._visible = state

    def isVisible(self):
        """Get channel visibility"""
        return self._visible

    def getMean(self):
        """Calculate mean voltage of last waveform"""
        if self.WF.scaledYdata:
            return np.mean(self.WF.scaledYdata)
        return 0.0

    def getMax(self):
        """Get maximum voltage of last waveform"""
        if self.WF.scaledYdata:
            return np.max(self.WF.scaledYdata)
        return 0.0

    def getMin(self):
        """Get minimum voltage of last waveform"""
        if self.WF.scaledYdata:
            return np.min(self.WF.scaledYdata)
        return 0.0


class HantekVertical(BaseVertical):
    """Vertical control for Hantek scopes"""

    @classmethod
    def getVerticalClass(cls, dev):
        if cls is HantekVertical:
            return cls
        return None

    def __init__(self, nrOfChan: int, scope_obj: Oscilloscope):
        super().__init__(nrOfChan, None)
        self.scope_obj = scope_obj
        self.nrOfChan = nrOfChan
        self.channels = []

        for i in range(1, nrOfChan + 1):
            self.channels.append({i: HantekChannel(i, scope_obj)})


class HantekHorizontal(BaseHorizontal):
    """Horizontal control for Hantek scopes"""

    @classmethod
    def getHorizontalClass(cls, dev):
        if cls is HantekHorizontal:
            return cls
        return None

    def __init__(self, scope_obj: Oscilloscope):
        super().__init__(None)
        self.scope_obj = scope_obj
        self._sample_rate_index = 1  # Default 1 MS/s

    def setTimeDiv(self, value):
        """Set time/div by selecting appropriate sample rate"""
        # Map time/div to sample rate
        # This is approximate - Hantek has fixed sample rates
        desired_rate = 10.0 / value  # Assume ~10 divs on screen

        # Find closest sample rate
        best_idx = 1
        best_diff = float('inf')

        for idx, (name, rate) in Oscilloscope.SAMPLE_RATES.items():
            diff = abs(rate - desired_rate)
            if diff < best_diff:
                best_diff = diff
                best_idx = idx

        self._sample_rate_index = best_idx
        self.scope_obj.set_sample_rate(best_idx)
        self.SR = Oscilloscope.SAMPLE_RATES[best_idx][1]

    def getTimeDivs(self):
        """Get available time/div settings"""
        return [name for name, _ in Oscilloscope.SAMPLE_RATES.values()]


class HantekTrigger(BaseTriggerUnit):
    """Trigger control for Hantek scopes (limited functionality)"""

    @classmethod
    def getTriggerUnitClass(cls, vertical, visaInstr=None):
        if cls is HantekTrigger:
            return cls
        return None

    def __init__(self, vertical: HantekVertical, scope_obj: Oscilloscope):
        super().__init__(vertical, None)
        self.scope_obj = scope_obj
        self._source_channel = 1
        self._trigger_level = 0

    def setSource(self, chanNr):
        """Set trigger source channel"""
        self._source_channel = chanNr
        # Note: Hantek 6022 doesn't support software trigger source selection

    def level(self, level=None):
        """Set/get trigger level"""
        if level is not None:
            self._trigger_level = level
            # Convert voltage to ADC value (0-255)
            # This is simplified - real implementation needs voltage range
            adc_level = int((level / 5.0) * 128 + 128)
            adc_level = max(0, min(255, adc_level))
            self.scope_obj.set_trigger(self._source_channel, adc_level, is_rim=True)
        return self._trigger_level


class HantekScope(BaseScope):
    """Hantek 6022 series scope integrated into BaseScope framework"""

    # Class variable to store singleton Oscilloscope instance
    _oscilloscope_instance = None
    _instance_vid = None
    _instance_pid = None

    @classmethod
    def getScopeClass(cls, rm, urls, host=None, scopeConfig: BaseScopeConfig = None):
        """
        Detect and initialize Hantek scope via USB (not VISA)
        Uses singleton pattern to reuse the same Oscilloscope object
        """
        if cls is not HantekScope:
            return (None, None, None)

        try:
            # Try to find Hantek scope via USB
            context = usb1.USBContext()

            # Look for Hantek devices (with or without firmware)
            # Check firmware-loaded devices first (most common case)
            for vid in [Oscilloscope.FIRMWARE_PRESENT_VENDOR_ID, Oscilloscope.NO_FIRMWARE_VENDOR_ID]:
                for pid in [Oscilloscope.PRODUCT_ID_BL, Oscilloscope.PRODUCT_ID_BE, Oscilloscope.PRODUCT_ID_21]:
                    try:
                        device = context.getByVendorIDAndProductID(vid, pid)
                        if device is not None:
                            # Found a Hantek scope!
                            # Verify device is actually accessible before proceeding
                            try:
                                # Quick accessibility check - try to get device descriptor
                                # This will fail fast if device is not accessible
                                handle = device.open()
                                handle.close()
                            except usb1.USBError as check_err:
                                # Device exists but is not accessible - skip it
                                print(f"Hantek device found but not accessible: {check_err}")
                                continue

                            # Reuse existing instance if it matches VID/PID
                            if (cls._oscilloscope_instance is not None and
                                cls._instance_vid == vid and
                                cls._instance_pid == pid):
                                # Return existing instance
                                return (cls, cls._oscilloscope_instance, scopeConfig)
                            else:
                                # Create new instance and store it
                                scope_obj = Oscilloscope(VID=vid, PID=pid)
                                cls._oscilloscope_instance = scope_obj
                                cls._instance_vid = vid
                                cls._instance_pid = pid
                                return (cls, scope_obj, scopeConfig)
                    except Exception as inner_e:
                        # Continue trying other VID/PID combinations
                        print(f"Error checking device VID={vid:04x} PID={pid:04x}: {inner_e}")
                        continue

            # No Hantek scope found
            return (None, None, None)

        except Exception as e:
            # Silently fail - this is expected if no Hantek scope is connected
            print(f"Hantek scope detection failed: {e}")
            return (None, None, None)

    def __init__(self, scope_obj: Oscilloscope, scopeConfig: BaseScopeConfig = None):
        """Initialize Hantek scope wrapper"""
        super().__init__(None, scopeConfig)  # No VISA instrument

        self.scope_obj = scope_obj

        # Try to open and initialize the scope
        # The Hantek API's open_handle() checks if handle is already open (line 221-222)
        # and returns True if so. We just need to call it safely.
        try:
            # If device_handle already exists, open_handle will just return True
            # Otherwise it will try to open it
            success = scope_obj.open_handle()
            if not success:
                raise RuntimeError("Device is busy. Unplug the Hantek scope, wait 3 seconds, and plug it back in.")
        except usb1.USBErrorBusy:
            raise RuntimeError("Device is busy. Unplug the Hantek scope, wait 3 seconds, and plug it back in.")
        except usb1.USBErrorAccess:
            raise RuntimeError("Permission denied. Run: sudo chmod 666 /dev/bus/usb/*/*")
        except usb1.USBErrorNoDevice:
            raise RuntimeError("USB device not found or disconnected. Check the connection and try again.")
        except usb1.USBError as e:
            # Catch all USB errors and wrap them in RuntimeError for consistent handling
            error_msg = str(e)
            if "BUSY" in error_msg or "busy" in error_msg:
                raise RuntimeError("Device is busy. Unplug the Hantek scope, wait 3 seconds, and plug it back in.")
            raise RuntimeError(f"USB Error: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            if "BUSY" in error_msg or "busy" in error_msg:
                raise RuntimeError("Device is busy. Unplug the Hantek scope, wait 3 seconds, and plug it back in.")
            raise RuntimeError(f"Unexpected error: {error_msg}")

        # Flash firmware if needed
        # This is now safe because device discovery runs in a separate thread
        if not scope_obj.is_device_firmware_present:
            print("Hantek scope needs firmware - flashing now...")
            try:
                scope_obj.flash_firmware()
                print("Firmware flash successful!")
            except Exception as e:
                # If flash_firmware fails, check if device re-enumerated anyway
                time.sleep(2)
                # Try to reconnect - device may have re-enumerated with new VID
                try:
                    scope_obj.close_handle()
                except:
                    pass

                # Create new context and look for device with firmware
                import usb1
                context = usb1.USBContext()
                for pid in [Oscilloscope.PRODUCT_ID_BL, Oscilloscope.PRODUCT_ID_BE, Oscilloscope.PRODUCT_ID_21]:
                    device = context.getByVendorIDAndProductID(Oscilloscope.FIRMWARE_PRESENT_VENDOR_ID, pid)
                    if device:
                        # Found device with firmware - update scope_obj
                        scope_obj.VID = Oscilloscope.FIRMWARE_PRESENT_VENDOR_ID
                        scope_obj.PID = pid
                        scope_obj.is_device_firmware_present = True
                        if not scope_obj.setup():
                            raise RuntimeError("Failed to setup device after firmware flash")
                        if not scope_obj.open_handle():
                            raise RuntimeError("Failed to open device after firmware flash")
                        print("Device reconnected with firmware!")
                        break
                else:
                    raise RuntimeError(
                        f"Firmware flash failed: {e}\n\n"
                        "Please run: python src/flash_hantek_firmware.py"
                    )

        # Set device info
        self.brand = "Hantek"
        if scope_obj.PID == Oscilloscope.PRODUCT_ID_BL:
            self.model = "DSO-6022BL"
        elif scope_obj.PID == Oscilloscope.PRODUCT_ID_BE:
            self.model = "DSO-6022BE"
        else:
            self.model = "DSO-6021"

        # Determine number of channels
        nrOfChan = 2  # Hantek 6022 has 2 channels

        # Initialize subsystems
        self.horizontal = HantekHorizontal(scope_obj)
        self.vertical = HantekVertical(nrOfChan, scope_obj)
        self.trigger = HantekTrigger(self.vertical, scope_obj)

        # Store sample rate index for channels to access
        scope_obj._sample_rate_index = 1  # Default

        # Configure default settings
        scope_obj.set_num_channels(2)
        scope_obj.set_ch1_voltage_range(1)  # +/- 5V
        scope_obj.set_ch2_voltage_range(1)
        scope_obj.set_sample_rate(1)  # 1 MS/s

        # Grid divisions
        self.nrOfHoriDivs = 10
        self.nrOfVertDivs = 8
        self.visibleHoriDivs = 10
        self.visibleVertDivs = 8

    def __del__(self):
        """Cleanup when scope object is destroyed"""
        try:
            if hasattr(self, 'scope_obj') and self.scope_obj:
                self.scope_obj.close_handle()
        except:
            pass
