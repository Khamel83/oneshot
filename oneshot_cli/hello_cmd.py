"""oneshot hello — greet the user."""
from __future__ import annotations

import click


@click.command("hello")
def cli():
    """Print a greeting from oneshot."""
    click.echo("Hello from oneshot!")
