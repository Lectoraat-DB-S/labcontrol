"""External tool launcher commands."""

import shutil
import subprocess
import sys

import click

from ..output import success, warning, error


def _detach_kwargs():
    """Kwargs to launch a fully detached child across platforms."""
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        return {"creationflags": flags, "close_fds": True}
    return {"start_new_session": True}


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
    subprocess.Popen([exe], **_detach_kwargs())
