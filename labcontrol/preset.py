"""Preset system - YAML loading + Pydantic validation."""

import re
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, field_validator

# Project root: where pyproject.toml lives
PROJECT_ROOT = Path(__file__).parent.parent
PRESET_DIRS = [
    PROJECT_ROOT / "presets" / "examples",
    PROJECT_ROOT / "presets" / "user",
]

# Engineering notation multipliers
_TIME_UNITS = {"s": 1, "ms": 1e-3, "us": 1e-6, "µs": 1e-6, "ns": 1e-9}
_FREQ_UNITS = {"hz": 1, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
_VALUE_RE = re.compile(r"^([0-9]*\.?[0-9]+)\s*([a-zµ]+)$", re.IGNORECASE)


def parse_time_value(value: str | float) -> float:
    """Parse time string with units to seconds. '1ms' → 0.001"""
    if isinstance(value, (int, float)):
        return float(value)
    m = _VALUE_RE.match(str(value).strip())
    if not m:
        raise ValueError(f"Cannot parse time value: {value!r}")
    num, unit = float(m.group(1)), m.group(2).lower()
    if unit not in _TIME_UNITS:
        raise ValueError(f"Unknown time unit: {unit!r} (valid: {', '.join(_TIME_UNITS)})")
    return num * _TIME_UNITS[unit]


def parse_freq_value(value: str | float) -> float:
    """Parse frequency string with units to Hz. '1kHz' → 1000"""
    if isinstance(value, (int, float)):
        return float(value)
    m = _VALUE_RE.match(str(value).strip())
    if not m:
        raise ValueError(f"Cannot parse frequency value: {value!r}")
    num, unit = float(m.group(1)), m.group(2).lower()
    if unit not in _FREQ_UNITS:
        raise ValueError(f"Unknown frequency unit: {unit!r} (valid: {', '.join(_FREQ_UNITS)})")
    return num * _FREQ_UNITS[unit]


class ChannelPreset(BaseModel):
    """Configuration for a single scope channel."""
    vdiv: float = 1.0
    coupling: str = "DC"
    probe: int = 1

    @field_validator("coupling")
    @classmethod
    def validate_coupling(cls, v: str) -> str:
        v = v.upper()
        if v not in ("AC", "DC"):
            raise ValueError(f"Coupling must be AC or DC, got {v!r}")
        return v


class TriggerPreset(BaseModel):
    """Trigger configuration."""
    source: str = "ch1"
    mode: str = "auto"
    level: float = 0.0


class ScopePreset(BaseModel):
    """Scope-specific preset configuration."""
    channels: dict[int, ChannelPreset] = {}
    timebase: Optional[float] = None
    trigger: Optional[TriggerPreset] = None

    @field_validator("timebase", mode="before")
    @classmethod
    def parse_timebase(cls, v):
        if v is None:
            return None
        return parse_time_value(v)


class Preset(BaseModel):
    """Top-level preset model."""
    name: str
    description: str = ""
    devices: dict[str, ScopePreset] = {}


def list_presets() -> list[dict[str, str]]:
    """List all available presets from all preset directories."""
    presets = []
    for d in PRESET_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.yaml")):
            try:
                data = yaml.safe_load(f.read_text())
                presets.append({
                    "name": f.stem,
                    "title": data.get("name", f.stem),
                    "description": data.get("description", ""),
                    "path": str(f),
                })
            except Exception:
                continue
    return presets


def load_preset(name: str) -> Preset:
    """Load and validate a preset by name (without .yaml extension)."""
    for d in PRESET_DIRS:
        path = d / f"{name}.yaml"
        if path.exists():
            data = yaml.safe_load(path.read_text())
            return Preset(**data)
    available = [p["name"] for p in list_presets()]
    raise FileNotFoundError(
        f"Preset {name!r} not found. Available: {', '.join(available) or 'none'}"
    )
