"""ASCII banner for labcontrol CLI."""

BANNER = r"""
[bold cyan]
  ╦  ╔═╗╔╗ ╔═╗╔═╗╔╗╔╔╦╗╦═╗╔═╗╦
  ║  ╠═╣╠╩╗║  ║ ║║║║ ║ ╠╦╝║ ║║
  ╩═╝╩ ╩╚═╝╚═╝╚═╝╝╚╝ ╩ ╩╚═╚═╝╩═╝[/bold cyan]
[dim]  ──────────────────────────────────
   CLI instrument configuration tool
  ──────────────────────────────────[/dim]
"""


def print_banner():
    """Print the labcontrol banner using rich."""
    from rich.console import Console
    Console().print(BANNER)
