"""Device discovery commands."""

import click

from ..output import device_table, warning


@click.command()
def devices():
    """Scan and show connected devices."""
    # Import hantek to trigger auto-registration
    from ..drivers import hantek  # noqa: F401
    from ..drivers.registry import discover_devices

    found = discover_devices()
    if not found:
        warning("No registered device types found")
        return
    device_table(found)
