"""External tool launcher commands."""

import shutil
import subprocess

import click

from ..output import success, warning, error


@click.command()
def openhantek():
    """Launch OpenHantek (disconnects scope first if connected)."""
    from ..drivers.registry import _instances

    # Release USB device so OpenHantek can claim it
    if "scope" in _instances:
        warning("Disconnecting scope so OpenHantek can access the device...")
        try:
            _instances["scope"].disconnect()
        except Exception:
            pass
        del _instances["scope"]

    exe = shutil.which("OpenHantek") or shutil.which("openhantek")
    if not exe:
        error("OpenHantek not found in PATH")
        return
    success(f"Starting OpenHantek ({exe})")
    subprocess.Popen([exe], start_new_session=True)
