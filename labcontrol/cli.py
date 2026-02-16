"""Labcontrol CLI entry point."""

import click

from .commands.devices import devices
from .commands.presets import list_cmd, show, load
from .commands.scope import scope
from .commands.tools import openhantek


@click.group()
@click.version_option(package_name="labcontrol")
def cli():
    """Labcontrol - CLI instrument configuration tool."""
    pass


cli.add_command(devices)
cli.add_command(list_cmd, name="list")
cli.add_command(show)
cli.add_command(load)
cli.add_command(scope)
cli.add_command(openhantek)
