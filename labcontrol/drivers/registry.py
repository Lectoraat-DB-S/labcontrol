"""Device registry - discovery and management."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import DeviceDriver

_drivers: dict[str, type] = {}
_instances: dict[str, "DeviceDriver"] = {}


def register_driver(device_type: str, driver_class: type) -> None:
    """Register a driver class for a device type."""
    _drivers[device_type] = driver_class


def discover_devices() -> list[dict[str, str]]:
    """Probe all registered drivers and return found devices."""
    found = []
    for device_type, cls in _drivers.items():
        try:
            driver = cls()
            if driver.connect():
                found.append({
                    "type": device_type,
                    "name": driver.device_name,
                    "status": "connected",
                })
                _instances[device_type] = driver
            else:
                found.append({
                    "type": device_type,
                    "name": driver.device_name,
                    "status": "not found",
                })
        except Exception as e:
            found.append({
                "type": device_type,
                "name": cls.device_name if hasattr(cls, "device_name") else device_type,
                "status": f"error: {e}",
            })
    return found


def get_device(device_type: str) -> "DeviceDriver | None":
    """Get a connected device instance by type. Tries to connect if not cached."""
    if device_type in _instances:
        return _instances[device_type]
    if device_type not in _drivers:
        return None
    driver = _drivers[device_type]()
    if driver.connect():
        _instances[device_type] = driver
        return driver
    return None


def get_registered_types() -> list[str]:
    """Return list of registered device types."""
    return list(_drivers.keys())
