"""Tests for the preset system."""

import pytest
from labcontrol.preset import (
    parse_time_value,
    parse_freq_value,
    load_preset,
    list_presets,
    ChannelPreset,
    ScopePreset,
    Preset,
)


class TestParseTimeValue:
    def test_milliseconds(self):
        assert parse_time_value("1ms") == 0.001

    def test_microseconds(self):
        assert parse_time_value("100us") == pytest.approx(100e-6)

    def test_seconds(self):
        assert parse_time_value("2s") == 2.0

    def test_nanoseconds(self):
        assert parse_time_value("500ns") == pytest.approx(500e-9)

    def test_float_passthrough(self):
        assert parse_time_value(0.001) == 0.001

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="Unknown time unit"):
            parse_time_value("5km")

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_time_value("abc")


class TestParseFreqValue:
    def test_kilohertz(self):
        assert parse_freq_value("1kHz") == 1000.0

    def test_megahertz(self):
        assert parse_freq_value("10MHz") == 10e6

    def test_hertz(self):
        assert parse_freq_value("50Hz") == 50.0

    def test_float_passthrough(self):
        assert parse_freq_value(1000) == 1000.0


class TestChannelPreset:
    def test_defaults(self):
        ch = ChannelPreset()
        assert ch.vdiv == 1.0
        assert ch.coupling == "DC"
        assert ch.probe == 1

    def test_ac_coupling(self):
        ch = ChannelPreset(coupling="ac")
        assert ch.coupling == "AC"

    def test_invalid_coupling(self):
        with pytest.raises(ValueError):
            ChannelPreset(coupling="GND")


class TestScopePreset:
    def test_timebase_parsing(self):
        sp = ScopePreset(timebase="1ms")
        assert sp.timebase == 0.001

    def test_timebase_none(self):
        sp = ScopePreset()
        assert sp.timebase is None


class TestPreset:
    def test_full_preset(self):
        p = Preset(
            name="test",
            description="test preset",
            devices={
                "scope": ScopePreset(
                    channels={1: ChannelPreset(vdiv=0.5, coupling="AC")},
                    timebase="100us",
                )
            },
        )
        assert p.name == "test"
        assert p.devices["scope"].channels[1].vdiv == 0.5
        assert p.devices["scope"].timebase == pytest.approx(100e-6)


class TestListPresets:
    def test_finds_example_presets(self):
        presets = list_presets()
        names = [p["name"] for p in presets]
        assert "basic_scope" in names
        assert "rc_filter" in names


class TestLoadPreset:
    def test_load_basic_scope(self):
        preset = load_preset("basic_scope")
        assert preset.name == "Basic Scope Setup"
        assert 1 in preset.devices["scope"].channels
        assert preset.devices["scope"].timebase == 0.001

    def test_load_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            load_preset("does_not_exist")
