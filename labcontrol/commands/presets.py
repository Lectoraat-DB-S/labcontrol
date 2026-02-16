"""Preset management commands."""

import click
from rich.syntax import Syntax

from ..output import console, preset_table, preset_results, success, error
from ..preset import list_presets, load_preset


@click.command("list")
def list_cmd():
    """Show available presets."""
    presets = list_presets()
    if not presets:
        error("No presets found")
        return
    preset_table(presets)


@click.command()
@click.argument("name")
def show(name: str):
    """Show preset details."""
    try:
        preset = load_preset(name)
    except FileNotFoundError as e:
        error(str(e))
        return

    console.print(f"[bold]{preset.name}[/bold]")
    if preset.description:
        console.print(f"[dim]{preset.description}[/dim]")
    console.print()

    for dev_type, dev_cfg in preset.devices.items():
        console.print(f"[cyan]{dev_type}:[/cyan]")
        if dev_cfg.channels:
            for ch_num, ch in dev_cfg.channels.items():
                console.print(f"  CH{ch_num}: {ch.vdiv} V/div, {ch.coupling}, probe {ch.probe}x")
        if dev_cfg.timebase is not None:
            console.print(f"  Timebase: {dev_cfg.timebase}s/div")
        if dev_cfg.trigger:
            console.print(f"  Trigger: {dev_cfg.trigger.source} {dev_cfg.trigger.mode} @ {dev_cfg.trigger.level}V")


@click.command()
@click.argument("name")
def load(name: str):
    """Load a preset and apply it to connected devices."""
    try:
        preset = load_preset(name)
    except FileNotFoundError as e:
        error(str(e))
        return

    # Import hantek to trigger auto-registration
    from ..drivers import hantek  # noqa: F401
    from ..drivers.registry import get_device

    all_results = {}
    for dev_type, dev_cfg in preset.devices.items():
        driver = get_device(dev_type)
        if not driver:
            error(f"Device '{dev_type}' not found or failed to connect")
            continue
        config = dev_cfg.model_dump()
        results = driver.apply_config(config)
        all_results.update(results)

    if all_results:
        preset_results(all_results)
        success(f"Preset '{preset.name}' loaded successfully")
    else:
        error("No settings were applied")
