"""Labcontrol CLI entry point."""

import click

from .commands.devices import devices
from .commands.presets import list_cmd, show, load
from .commands.scope import scope
from .commands.tools import openhantek


@click.group(invoke_without_command=True)
@click.version_option(package_name="labcontrol")
@click.pass_context
def cli(ctx):
    """Labcontrol - CLI instrument configuration tool."""
    if ctx.invoked_subcommand is None:
        from .banner import print_banner
        print_banner()
        click.echo(ctx.get_help())


cli.add_command(devices)
cli.add_command(list_cmd, name="list")
cli.add_command(show)
cli.add_command(load)
cli.add_command(scope)
cli.add_command(openhantek)
