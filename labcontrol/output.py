"""Rich console output helpers."""

from rich.console import Console
from rich.table import Table

console = Console()


def success(msg: str) -> None:
    console.print(f"[green]{msg}[/green]")


def warning(msg: str) -> None:
    console.print(f"[yellow]{msg}[/yellow]")


def error(msg: str) -> None:
    console.print(f"[red]{msg}[/red]")


def device_table(devices: list[dict]) -> None:
    """Print a table of discovered devices."""
    table = Table(title="Devices")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Status")
    for dev in devices:
        status = dev["status"]
        style = "green" if status == "connected" else "red"
        table.add_row(dev["type"], dev["name"], f"[{style}]{status}[/{style}]")
    console.print(table)


def preset_table(presets: list[dict]) -> None:
    """Print a table of available presets."""
    table = Table(title="Presets")
    table.add_column("Name", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Description", style="dim")
    for p in presets:
        table.add_row(p["name"], p["title"], p["description"])
    console.print(table)


def preset_results(results: dict) -> None:
    """Print results of applying a preset."""
    table = Table(title="Configuration Applied")
    table.add_column("Setting", style="cyan")
    table.add_column("Result", style="green")
    for key, value in results.items():
        table.add_row(key, str(value))
    console.print(table)


def status_display(status: dict) -> None:
    """Print device status."""
    if not status.get("connected"):
        error("Scope not connected")
        return
    table = Table(title="Scope Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    for key, value in status.items():
        if key == "connected":
            continue
        if isinstance(value, dict):
            for subkey, subval in value.items():
                table.add_row(f"{key}.{subkey}", str(subval))
        else:
            table.add_row(key, str(value))
    console.print(table)
