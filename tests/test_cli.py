"""Tests for the CLI commands."""

from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from labcontrol.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_driver():
    """Mock driver to avoid USB access."""
    driver = MagicMock()
    driver.device_type = "scope"
    driver.device_name = "Hantek DSO-6022 (mock)"
    driver.connect.return_value = True
    driver.get_status.return_value = {
        "connected": True,
        "ch1": {"vdiv": 2.5, "range": "+/- 5V", "coupling": "DC"},
        "ch2": {"vdiv": 2.5, "range": "+/- 5V", "coupling": "DC"},
        "sample_rate": "1 MS/s",
    }
    driver.apply_config.return_value = {
        "ch1_vdiv": "CH1 V/div: 1.0 → 0.5 V/div (+/- 1V)",
        "ch2_vdiv": "CH2 V/div: 1.0 → 0.5 V/div (+/- 1V)",
        "timebase": "Timebase: 0.001s/div → 10 MS/s",
    }
    return driver


class TestVersion:
    def test_version_flag(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "2.0.0" in result.output


class TestListCommand:
    def test_list_shows_presets(self, runner):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "basic_scope" in result.output


class TestShowCommand:
    def test_show_preset(self, runner):
        result = runner.invoke(cli, ["show", "basic_scope"])
        assert result.exit_code == 0
        assert "Basic Scope Setup" in result.output

    def test_show_nonexistent(self, runner):
        result = runner.invoke(cli, ["show", "nonexistent"])
        assert result.exit_code == 0
        assert "not found" in result.output


class TestDevicesCommand:
    def test_devices_with_mock(self, runner, mock_driver):
        with patch("labcontrol.drivers.registry.discover_devices") as mock_discover:
            mock_discover.return_value = [
                {"type": "scope", "name": "Hantek DSO-6022 (mock)", "status": "connected"}
            ]
            result = runner.invoke(cli, ["devices"])
            assert result.exit_code == 0
            assert "Hantek" in result.output


class TestLoadCommand:
    def test_load_with_mock(self, runner, mock_driver):
        with patch("labcontrol.drivers.registry.get_device") as mock_get:
            mock_get.return_value = mock_driver
            result = runner.invoke(cli, ["load", "basic_scope"])
            assert result.exit_code == 0
            mock_driver.apply_config.assert_called_once()


class TestScopeStatusCommand:
    def test_status_with_mock(self, runner, mock_driver):
        with patch("labcontrol.drivers.registry.get_device") as mock_get:
            mock_get.return_value = mock_driver
            result = runner.invoke(cli, ["scope", "status"])
            assert result.exit_code == 0
