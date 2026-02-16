"""Tests for capture, plotting, and CSV export."""

import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from labcontrol.plotting import save_capture_plot, save_capture_csv
from labcontrol.commands.scope import MAX_SAMPLES, MAX_SINGLE_DURATION, MAX_STREAM_DURATION, MIN_RATE, MAX_RATE


# --- Fixtures ---

@pytest.fixture
def sample_data():
    """Realistic capture data dict."""
    import math
    n = 100
    dt = 1e-6  # 1 MHz sample rate
    times = [i * dt for i in range(n)]
    ch1 = [math.sin(2 * math.pi * 10000 * t) for t in times]
    ch2 = [0.5 * math.cos(2 * math.pi * 10000 * t) for t in times]
    return {
        "time": times,
        "ch1": ch1,
        "ch2": ch2,
        "sample_rate": "1 MS/s",
        "config": {
            "ch1_range": "+/-5V",
            "ch2_range": "+/-5V",
            "ch1_vdiv": 2.5,
            "ch2_vdiv": 2.5,
            "ch1_coupling": "DC",
            "ch2_coupling": "DC",
        },
    }


@pytest.fixture
def mock_scope():
    """Mocked Oscilloscope instance."""
    scope = MagicMock()
    scope.setup.return_value = True
    scope.open_handle.return_value = True
    scope.is_device_firmware_present = True
    scope.flash_firmware.return_value = True
    scope.read_data.return_value = (list(range(128, 138)), list(range(128, 138)))
    scope.scale_read_data.return_value = [0.1 * i for i in range(10)]
    scope.convert_sampling_rate_to_measurement_times.return_value = (
        [i * 1e-6 for i in range(10)],
        "1 MS/s",
    )
    scope.SAMPLE_RATES = {1: ("100 KS/s", 100000)}
    scope.VOLTAGE_RANGES = {1: ("+/-5V", 0.0390625, 5.0)}
    return scope


# --- HantekDriver.capture() tests ---

class TestCapture:
    def test_capture_returns_dict(self, mock_scope):
        with patch("labcontrol.drivers.hantek.Oscilloscope", return_value=mock_scope):
            from labcontrol.drivers.hantek import HantekDriver
            driver = HantekDriver()
            driver._scope = mock_scope
            driver._connected = True

            result = driver.capture(num_samples=10)

            assert "time" in result
            assert "ch1" in result
            assert "ch2" in result
            assert "sample_rate" in result
            assert "config" in result
            mock_scope.get_calibration_values.assert_called_once()
            mock_scope.read_data.assert_called_once_with(data_size=10)

    def test_capture_not_connected(self):
        from labcontrol.drivers.hantek import HantekDriver
        driver = HantekDriver()
        with pytest.raises(RuntimeError, match="Not connected"):
            driver.capture()

    def test_capture_scales_both_channels(self, mock_scope):
        with patch("labcontrol.drivers.hantek.Oscilloscope", return_value=mock_scope):
            from labcontrol.drivers.hantek import HantekDriver
            driver = HantekDriver()
            driver._scope = mock_scope
            driver._connected = True

            driver.capture(num_samples=10)

            assert mock_scope.scale_read_data.call_count == 2
            calls = mock_scope.scale_read_data.call_args_list
            assert calls[0].kwargs.get("channel", calls[0][1][2] if len(calls[0][1]) > 2 else None) is not None


# --- Streaming capture tests ---

class TestCaptureStream:
    def _make_streaming_scope(self):
        """Create a mock scope that simulates async streaming."""
        scope = MagicMock()
        scope.setup.return_value = True
        scope.open_handle.return_value = True
        scope.is_device_firmware_present = True
        scope.VOLTAGE_RANGES = {1: ("+/-5V", 0.0390625, 5.0)}

        # read_async: invoke callback with test data, return shutdown event
        def fake_read_async(callback, block_size, outstanding_transfers=3, raw=False):
            import threading
            shutdown = threading.Event()
            # Simulate 3 blocks of data (first skipped, 2 kept)
            block = bytes([128] * block_size)
            callback(block, block)  # skipped (first)
            callback(block, block)  # kept
            callback(block, block)  # kept
            return shutdown

        scope.read_async.side_effect = fake_read_async
        scope.poll.return_value = None
        scope.scale_read_data.return_value = [0.0] * 100
        scope.convert_sampling_rate_to_measurement_times.return_value = (
            [i * 1e-5 for i in range(100)],
            "100 KS/s",
        )
        return scope

    def test_capture_stream_returns_dict(self):
        scope = self._make_streaming_scope()
        with patch("labcontrol.drivers.hantek.Oscilloscope", return_value=scope):
            from labcontrol.drivers.hantek import HantekDriver
            driver = HantekDriver()
            driver._scope = scope
            driver._connected = True

            with patch("labcontrol.drivers.hantek.time") as mock_time:
                # Simulate instant timeout: first call returns 0, second > duration
                mock_time.time.side_effect = [0.0, 1.0]
                mock_time.sleep = MagicMock()
                result = driver.capture_stream(duration=0.5)

            assert "time" in result
            assert "ch1" in result
            assert "ch2" in result
            assert "sample_rate" in result
            assert "config" in result
            scope.start_capture.assert_called_once()
            scope.stop_capture.assert_called_once()

    def test_capture_stream_not_connected(self):
        from labcontrol.drivers.hantek import HantekDriver
        driver = HantekDriver()
        with pytest.raises(RuntimeError, match="Not connected"):
            driver.capture_stream(duration=1.0)

    def test_capture_stream_duration_too_long(self, mock_scope):
        with patch("labcontrol.drivers.hantek.Oscilloscope", return_value=mock_scope):
            from labcontrol.drivers.hantek import HantekDriver
            driver = HantekDriver()
            driver._scope = mock_scope
            driver._connected = True

            with pytest.raises(ValueError, match="te lang"):
                driver.capture_stream(duration=60.0)

    def test_capture_stream_skips_first_block(self):
        """Verify the first callback block is skipped (unstable data)."""
        scope = self._make_streaming_scope()
        with patch("labcontrol.drivers.hantek.Oscilloscope", return_value=scope):
            from labcontrol.drivers.hantek import HantekDriver
            driver = HantekDriver()
            driver._scope = scope
            driver._connected = True

            with patch("labcontrol.drivers.hantek.time") as mock_time:
                mock_time.time.side_effect = [0.0, 1.0]
                mock_time.sleep = MagicMock()
                driver.capture_stream(duration=0.5)

            # scale_read_data gets 2 blocks worth of data (first skipped), as list of ints
            ch1_arg = scope.scale_read_data.call_args_list[0][0][0]
            expected_size = 2 * 6 * 1024  # 2 kept blocks × STREAM_BLOCK_SIZE
            assert len(ch1_arg) == expected_size
            assert isinstance(ch1_arg, list)


# --- CSV export tests ---

class TestCSVExport:
    def test_csv_creates_file(self, tmp_path, sample_data):
        out = save_capture_csv(sample_data, tmp_path / "test.csv")
        assert out.exists()

    def test_csv_has_header_and_data(self, tmp_path, sample_data):
        out = save_capture_csv(sample_data, tmp_path / "test.csv")
        content = out.read_text()
        lines = content.strip().split("\n")
        # Metadata comments
        assert lines[0].startswith("# sample_rate:")
        # CSV header
        assert "time_s" in lines[3]
        # Data rows (100 samples)
        data_lines = [l for l in lines if not l.startswith("#") and "time_s" not in l]
        assert len(data_lines) == 100

    def test_csv_values_parseable(self, tmp_path, sample_data):
        out = save_capture_csv(sample_data, tmp_path / "test.csv")
        with open(out) as f:
            # Skip comment lines
            data_lines = [l for l in f if not l.startswith("#")]
        reader = csv.reader(data_lines)
        header = next(reader)
        assert header == ["time_s", "ch1_v", "ch2_v"]
        rows = list(reader)
        assert len(rows) == 100
        # Values should be parseable as floats
        float(rows[0][0])
        float(rows[0][1])
        float(rows[0][2])


# --- Plot tests ---

class TestPlot:
    def test_plot_creates_png(self, tmp_path, sample_data):
        out = save_capture_plot(sample_data, tmp_path / "test.png")
        assert out.exists()
        assert out.stat().st_size > 0

    def test_plot_creates_svg(self, tmp_path, sample_data):
        out = save_capture_plot(sample_data, tmp_path / "test.svg")
        assert out.exists()
        assert out.suffix == ".svg"

    def test_plot_custom_title(self, tmp_path, sample_data):
        out = save_capture_plot(sample_data, tmp_path / "test.png", title="My Test")
        assert out.exists()


# --- CLI command tests ---

class TestCaptureCommand:
    def _make_mock_driver(self, sample_data):
        driver = MagicMock()
        driver.capture.return_value = sample_data
        return driver

    def test_capture_summary(self, sample_data):
        from labcontrol.commands.scope import scope

        driver = self._make_mock_driver(sample_data)
        runner = CliRunner()
        with patch("labcontrol.drivers.registry.get_device", return_value=driver):
            with patch.dict("sys.modules", {"labcontrol.drivers.hantek": MagicMock()}):
                result = runner.invoke(scope, ["capture"])
        assert result.exit_code == 0
        assert "CH1" in result.output
        assert "CH2" in result.output

    def test_capture_with_save(self, tmp_path, sample_data):
        from labcontrol.commands.scope import scope

        driver = self._make_mock_driver(sample_data)
        png_path = str(tmp_path / "out.png")
        runner = CliRunner()
        with patch("labcontrol.drivers.registry.get_device", return_value=driver):
            with patch.dict("sys.modules", {"labcontrol.drivers.hantek": MagicMock()}):
                result = runner.invoke(scope, ["capture", "--save", png_path])
        assert result.exit_code == 0
        assert Path(png_path).exists()

    def test_capture_with_csv(self, tmp_path, sample_data):
        from labcontrol.commands.scope import scope

        driver = self._make_mock_driver(sample_data)
        csv_path = str(tmp_path / "out.csv")
        runner = CliRunner()
        with patch("labcontrol.drivers.registry.get_device", return_value=driver):
            with patch.dict("sys.modules", {"labcontrol.drivers.hantek": MagicMock()}):
                result = runner.invoke(scope, ["capture", "--csv", csv_path])
        assert result.exit_code == 0
        assert Path(csv_path).exists()

    def test_capture_no_scope(self):
        from labcontrol.commands.scope import scope

        runner = CliRunner()
        with patch("labcontrol.drivers.registry.get_device", return_value=None):
            with patch.dict("sys.modules", {"labcontrol.drivers.hantek": MagicMock()}):
                result = runner.invoke(scope, ["capture"])
        assert "not found" in result.output.lower() or result.exit_code != 0


# --- Hardware constraint validation tests ---

class TestCaptureValidation:
    """Test that invalid hardware combinations are rejected with helpful errors."""

    def _invoke_capture(self, args):
        """Invoke capture with validation-only args (no driver needed)."""
        from labcontrol.commands.scope import scope
        runner = CliRunner()
        # Mock the hantek module import but don't need driver for validation errors
        with patch.dict("sys.modules", {"labcontrol.drivers.hantek": MagicMock()}):
            result = runner.invoke(scope, ["capture"] + args)
        return result

    def test_samples_too_high_without_duration(self):
        result = self._invoke_capture(["--samples", "5000"])
        assert "5000 samples te veel" in result.output
        assert "--duration" in result.output

    def test_duration_too_long(self):
        result = self._invoke_capture(["--duration", "50.0"])
        assert "te lang" in result.output
        assert f"Max: {MAX_STREAM_DURATION}s" in result.output
        assert f"--duration {MAX_STREAM_DURATION}" in result.output

    def test_interval_too_large(self):
        result = self._invoke_capture(["--interval", "1.0"])
        assert "te groot" in result.output
        assert "kS/s" in result.output

    def test_interval_too_small(self):
        result = self._invoke_capture(["--interval", "0.00000001"])
        assert "te klein" in result.output
        assert "MS/s" in result.output

    def test_interval_and_duration_conflict(self):
        result = self._invoke_capture(["--interval", "0.00005", "--duration", "0.1"])
        assert "not both" in result.output

    def test_valid_samples_passes(self, sample_data):
        from labcontrol.commands.scope import scope
        driver = MagicMock()
        driver.capture.return_value = sample_data
        runner = CliRunner()
        with patch("labcontrol.drivers.registry.get_device", return_value=driver):
            with patch.dict("sys.modules", {"labcontrol.drivers.hantek": MagicMock()}):
                result = runner.invoke(scope, ["capture", "--samples", "2048"])
        assert result.exit_code == 0
        assert "CH1" in result.output


class TestCaptureSamplesCap:
    """Test that HantekDriver.capture() caps samples at MAX_SAMPLES."""

    def test_capture_caps_at_max(self, mock_scope):
        with patch("labcontrol.drivers.hantek.Oscilloscope", return_value=mock_scope):
            from labcontrol.drivers.hantek import HantekDriver
            driver = HantekDriver()
            driver._scope = mock_scope
            driver._connected = True

            driver.capture(num_samples=5000)

            # Should have been capped to 2048
            mock_scope.read_data.assert_called_once_with(data_size=2048)

    def test_capture_normal_samples_unchanged(self, mock_scope):
        with patch("labcontrol.drivers.hantek.Oscilloscope", return_value=mock_scope):
            from labcontrol.drivers.hantek import HantekDriver
            driver = HantekDriver()
            driver._scope = mock_scope
            driver._connected = True

            driver.capture(num_samples=512)

            mock_scope.read_data.assert_called_once_with(data_size=512)


class TestCLIStreamRouting:
    """Test that CLI correctly routes to single-shot vs streaming."""

    def _make_mock_driver(self, sample_data):
        driver = MagicMock()
        driver.capture.return_value = sample_data
        driver.capture_stream.return_value = sample_data
        return driver

    def _mock_hantek_module(self):
        """Create a mock hantek module with working _find_best_sample_rate."""
        mock_mod = MagicMock()
        # _find_best_sample_rate always returns rate index 1
        mock_mod._find_best_sample_rate.return_value = 1
        return mock_mod

    def _mock_oscilloscope(self):
        """Create mock Oscilloscope class with SAMPLE_RATES."""
        mock_osc = MagicMock()
        mock_osc.SAMPLE_RATES = {1: ("100 KS/s", 100000)}
        return mock_osc

    def test_short_duration_also_uses_streaming(self, sample_data):
        """Even short --duration uses streaming (async API more reliable)."""
        from labcontrol.commands.scope import scope
        driver = self._make_mock_driver(sample_data)
        mock_osc = self._mock_oscilloscope()
        runner = CliRunner()
        with patch("labcontrol.drivers.registry.get_device", return_value=driver):
            with patch.dict("sys.modules", {
                "labcontrol.drivers.hantek": self._mock_hantek_module(),
                "PyHT6022": MagicMock(),
                "PyHT6022.LibUsbScope": MagicMock(Oscilloscope=mock_osc),
            }):
                result = runner.invoke(scope, ["capture", "--duration", "0.01"])
        assert result.exit_code == 0, result.output
        driver.capture_stream.assert_called_once_with(duration=0.01)
        driver.capture.assert_not_called()

    def test_long_duration_uses_streaming(self, sample_data):
        """Duration exceeding single-shot should use capture_stream()."""
        from labcontrol.commands.scope import scope
        driver = self._make_mock_driver(sample_data)
        mock_osc = self._mock_oscilloscope()
        runner = CliRunner()
        with patch("labcontrol.drivers.registry.get_device", return_value=driver):
            with patch.dict("sys.modules", {
                "labcontrol.drivers.hantek": self._mock_hantek_module(),
                "PyHT6022": MagicMock(),
                "PyHT6022.LibUsbScope": MagicMock(Oscilloscope=mock_osc),
            }):
                result = runner.invoke(scope, ["capture", "--duration", "1.0"])
        assert result.exit_code == 0, result.output
        driver.capture_stream.assert_called_once_with(duration=1.0)
        driver.capture.assert_not_called()


class TestRatesCommand:
    """Test the scope rates info command."""

    def test_rates_output(self):
        from labcontrol.commands.scope import scope
        runner = CliRunner()
        mock_osc = MagicMock()
        mock_osc.SAMPLE_RATES = {
            1: ("20 KS/s", 20000),
            2: ("1 MS/s", 1000000),
        }
        with patch("PyHT6022.LibUsbScope.Oscilloscope", mock_osc):
            with patch.dict("sys.modules", {
                "PyHT6022": MagicMock(),
                "PyHT6022.LibUsbScope": MagicMock(Oscilloscope=mock_osc),
            }):
                result = runner.invoke(scope, ["rates"])
        assert result.exit_code == 0
        assert "20 KS/s" in result.output
        assert "1 MS/s" in result.output
