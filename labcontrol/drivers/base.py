"""Base device driver protocol."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class DeviceDriver(Protocol):
    """Protocol that all device drivers must implement."""

    device_type: str
    device_name: str

    def connect(self) -> bool:
        """Connect to the device. Returns True on success."""
        ...

    def disconnect(self) -> None:
        """Disconnect from the device."""
        ...

    def get_status(self) -> dict:
        """Return current device configuration as a dict."""
        ...

    def apply_config(self, config: dict) -> dict:
        """Apply configuration dict. Returns results with status per setting."""
        ...
