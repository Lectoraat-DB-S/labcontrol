"""Hantek DSO-6022BL/BE driver - config-only wrapper around LibUsbScope."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add Hantek6022API to import path
_api_path = str(Path(__file__).parent.parent.parent / "src" / "devices" / "Hantek6022API")
if _api_path not in sys.path:
    sys.path.insert(0, _api_path)

from PyHT6022.LibUsbScope import Oscilloscope  # noqa: E402

from .registry import register_driver  # noqa: E402

# Voltage range mapping: vdiv threshold → range index
# VOLTAGE_RANGES from LibUsbScope: {1: '+/-5V', 2: '+/-2.5V', 5: '+/-1V', 10: '+/-500mV'}
VDIV_MAP = [
    (1.0, 1),    # >= 1.0 V/div → range 1 (+/- 5V, 2.5 V/div effective)
    (0.5, 2),    # >= 0.5 V/div → range 2 (+/- 2.5V, 1.25 V/div effective)
    (0.2, 5),    # >= 0.2 V/div → range 5 (+/- 1V, 0.5 V/div effective)
    (0.0, 10),   # < 0.2 V/div → range 10 (+/- 500mV, 0.25 V/div effective)
]

# Reverse lookup: range index → effective V/div
RANGE_TO_VDIV = {1: 2.5, 2: 1.25, 5: 0.5, 10: 0.25}


def _vdiv_to_range(vdiv: float) -> int:
    """Map V/div value to closest Hantek voltage range index."""
    for threshold, idx in VDIV_MAP:
        if vdiv >= threshold:
            return idx
    return 10


def _find_best_sample_rate(desired_hz: float = None, *, time_per_div: float = None) -> int:
    """Find closest sample rate index for a desired rate in Hz or time/div.

    Args:
        desired_hz: Desired sample rate in Hz.
        time_per_div: Time per division (assumes 10 divisions, rate = 10/time_per_div).

    Returns the sample rate index for Oscilloscope.set_sample_rate().
    """
    if time_per_div is not None:
        desired_hz = 10.0 / time_per_div
    if desired_hz is None:
        raise ValueError("Specify desired_hz or time_per_div")
    best_idx = 1
    best_diff = float("inf")
    for idx, (_name, rate) in Oscilloscope.SAMPLE_RATES.items():
        diff = abs(rate - desired_hz)
        if diff < best_diff:
            best_diff = diff
            best_idx = idx
    return best_idx


class HantekDriver:
    """Config-only driver for Hantek DSO-6022BL/BE oscilloscopes."""

    device_type = "scope"
    device_name = "Hantek DSO-6022"

    def __init__(self):
        self._scope: Oscilloscope | None = None
        self._connected = False
        self._ch_ranges = {1: 1, 2: 1}       # range index per channel
        self._ch_coupling = {1: "DC", 2: "DC"}
        self._sample_rate_idx = 1

    def connect(self) -> bool:
        """Find and connect to the Hantek scope, flashing firmware if needed."""
        try:
            scope = Oscilloscope()
            if not scope.setup():
                return False
            if not scope.open_handle():
                return False
            # Flash firmware if not already present
            if not scope.is_device_firmware_present:
                if not scope.flash_firmware():
                    return False
            self._scope = scope
            self._connected = True
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        """Close the USB handle."""
        if self._scope:
            try:
                self._scope.close_handle()
            except Exception:
                pass
        self._connected = False
        self._scope = None

    def set_channel_vdiv(self, channel: int, vdiv: float) -> str:
        """Set voltage/div for a channel. Returns description of what was set."""
        if not self._scope:
            raise RuntimeError("Not connected")
        range_idx = _vdiv_to_range(vdiv)
        if channel == 1:
            self._scope.set_ch1_voltage_range(range_idx)
        else:
            self._scope.set_ch2_voltage_range(range_idx)
        self._ch_ranges[channel] = range_idx
        actual_vdiv = RANGE_TO_VDIV[range_idx]
        label = Oscilloscope.VOLTAGE_RANGES[range_idx][0]
        return f"CH{channel} V/div: {vdiv} → {actual_vdiv} V/div ({label})"

    def set_channel_coupling(self, channel: int, coupling: str) -> str:
        """Set AC/DC coupling for a channel."""
        if not self._scope:
            raise RuntimeError("Not connected")
        ac_dc = Oscilloscope.AC if coupling.upper() == "AC" else Oscilloscope.DC
        if channel == 1:
            self._scope.set_ch1_ac_dc(ac_dc)
        else:
            self._scope.set_ch2_ac_dc(ac_dc)
        self._ch_coupling[channel] = coupling.upper()
        return f"CH{channel} coupling: {coupling.upper()}"

    def set_timebase(self, seconds_per_div: float) -> str:
        """Set timebase by selecting the closest sample rate."""
        if not self._scope:
            raise RuntimeError("Not connected")
        idx = _find_best_sample_rate(time_per_div=seconds_per_div)
        self._scope.set_sample_rate(idx)
        self._sample_rate_idx = idx
        label, rate = Oscilloscope.SAMPLE_RATES[idx]
        return f"Timebase: {seconds_per_div}s/div → {label}"

    def set_sample_rate(self, rate_idx: int) -> str:
        """Set sample rate by index. Returns description."""
        if not self._scope:
            raise RuntimeError("Not connected")
        self._scope.set_sample_rate(rate_idx)
        self._sample_rate_idx = rate_idx
        label, rate = Oscilloscope.SAMPLE_RATES[rate_idx]
        return f"Sample rate: {label}"

    def apply_config(self, config: dict) -> dict:
        """Apply a full scope configuration dict. Returns results per setting."""
        results = {}
        channels = config.get("channels", {})
        for ch_num, ch_cfg in channels.items():
            ch = int(ch_num)
            if "vdiv" in ch_cfg:
                results[f"ch{ch}_vdiv"] = self.set_channel_vdiv(ch, float(ch_cfg["vdiv"]))
            if "coupling" in ch_cfg:
                results[f"ch{ch}_coupling"] = self.set_channel_coupling(ch, ch_cfg["coupling"])
        if "timebase" in config and config["timebase"] is not None:
            results["timebase"] = self.set_timebase(float(config["timebase"]))
        return results

    # Max samples per single USB bulk read to avoid LIBUSB_ERROR_OVERFLOW
    MAX_SAMPLES = 2048

    # Streaming capture constants
    STREAM_BLOCK_SIZE = 6 * 1024    # bytes per USB transfer (matches record_wav.py)
    STREAM_OUTSTANDING = 10         # concurrent transfers for gapless sampling
    MAX_STREAM_DURATION = 30.0      # seconds; 30s @ 48 MS/s ≈ 1.4 GB

    def capture(self, num_samples: int = 1024) -> dict:
        """Single-shot capture with calibrated voltage data.

        Caps num_samples at MAX_SAMPLES (2048) to prevent USB overflow.
        Returns dict with time, ch1, ch2 (as lists of floats),
        sample_rate label, and current config.
        """
        if not self._scope:
            raise RuntimeError("Not connected")

        num_samples = min(num_samples, self.MAX_SAMPLES)

        # Load calibration if not yet done
        self._scope.get_calibration_values()

        ch1_raw, ch2_raw = self._scope.read_data(data_size=num_samples)

        # Scale to voltages
        ch1_volts = self._scope.scale_read_data(
            ch1_raw, voltage_range=self._ch_ranges[1], channel=1
        )
        ch2_volts = self._scope.scale_read_data(
            ch2_raw, voltage_range=self._ch_ranges[2], channel=2
        )

        # Time axis
        times, rate_label = self._scope.convert_sampling_rate_to_measurement_times(
            len(ch1_volts), self._sample_rate_idx
        )

        return {
            "time": times,
            "ch1": ch1_volts,
            "ch2": ch2_volts,
            "sample_rate": rate_label,
            "config": {
                "ch1_range": Oscilloscope.VOLTAGE_RANGES[self._ch_ranges[1]][0],
                "ch2_range": Oscilloscope.VOLTAGE_RANGES[self._ch_ranges[2]][0],
                "ch1_vdiv": RANGE_TO_VDIV[self._ch_ranges[1]],
                "ch2_vdiv": RANGE_TO_VDIV[self._ch_ranges[2]],
                "ch1_coupling": self._ch_coupling[1],
                "ch2_coupling": self._ch_coupling[2],
            },
        }

    def capture_stream(self, duration: float) -> dict:
        """Streaming capture for durations longer than single-shot allows.

        Uses the async USB transfer API (read_async + poll loop) to stream
        data continuously for the given duration. Proven pattern from
        capture_6022.py and record_wav.py examples.

        Returns same dict format as capture() for compatibility.
        """
        if not self._scope:
            raise RuntimeError("Not connected")
        if duration > self.MAX_STREAM_DURATION:
            raise ValueError(
                f"Duration {duration}s te lang. Max: {self.MAX_STREAM_DURATION}s"
            )

        self._scope.get_calibration_values()

        # Callback collects raw byte blocks
        ch1_blocks: list[bytes] = []
        ch2_blocks: list[bytes] = []
        skip_first = True

        def _callback(ch1_data, ch2_data):
            nonlocal skip_first
            if skip_first:
                skip_first = False
                return
            ch1_blocks.append(bytes(ch1_data))
            ch2_blocks.append(bytes(ch2_data))

        # Start streaming
        self._scope.start_capture()
        shutdown = self._scope.read_async(
            _callback,
            self.STREAM_BLOCK_SIZE,
            outstanding_transfers=self.STREAM_OUTSTANDING,
            raw=True,
        )

        start = time.time()
        while time.time() - start < duration:
            self._scope.poll()

        self._scope.stop_capture()
        shutdown.set()
        time.sleep(0.05)  # let pending transfers drain

        # Concatenate and convert raw bytes to integer list for scale_read_data
        ch1_raw = list(b"".join(ch1_blocks))
        ch2_raw = list(b"".join(ch2_blocks))
        ch1_volts = self._scope.scale_read_data(
            ch1_raw, voltage_range=self._ch_ranges[1], channel=1
        )
        ch2_volts = self._scope.scale_read_data(
            ch2_raw, voltage_range=self._ch_ranges[2], channel=2
        )

        # Time axis
        times, rate_label = self._scope.convert_sampling_rate_to_measurement_times(
            len(ch1_volts), self._sample_rate_idx
        )

        return {
            "time": times,
            "ch1": ch1_volts,
            "ch2": ch2_volts,
            "sample_rate": rate_label,
            "config": {
                "ch1_range": Oscilloscope.VOLTAGE_RANGES[self._ch_ranges[1]][0],
                "ch2_range": Oscilloscope.VOLTAGE_RANGES[self._ch_ranges[2]][0],
                "ch1_vdiv": RANGE_TO_VDIV[self._ch_ranges[1]],
                "ch2_vdiv": RANGE_TO_VDIV[self._ch_ranges[2]],
                "ch1_coupling": self._ch_coupling[1],
                "ch2_coupling": self._ch_coupling[2],
            },
        }

    def get_status(self) -> dict:
        """Return current configuration state."""
        status = {"connected": self._connected}
        if not self._connected:
            return status
        for ch in (1, 2):
            ridx = self._ch_ranges[ch]
            status[f"ch{ch}"] = {
                "vdiv": RANGE_TO_VDIV[ridx],
                "range": Oscilloscope.VOLTAGE_RANGES[ridx][0],
                "coupling": self._ch_coupling[ch],
            }
        sr_label, sr_rate = Oscilloscope.SAMPLE_RATES.get(
            self._sample_rate_idx, ("?", 0)
        )
        status["sample_rate"] = sr_label
        return status


# Auto-register when module is imported
register_driver("scope", HantekDriver)
