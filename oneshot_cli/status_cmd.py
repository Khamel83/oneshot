"""oneshot status — placeholder, implemented in T3."""
import click

@click.command()
@click.argument("task_id", required=False)
def cli(task_id):
    """Show status of dispatched tasks."""
    from oneshot_cli.tasks import status
    status(task_id)
