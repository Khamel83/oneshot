"""oneshot review — placeholder, implemented in T3."""
import click

@click.command()
@click.argument("task_id", required=True)
def cli(task_id):
    """Print review bundle paths for a collected task."""
    from oneshot_cli.tasks import review
    review(task_id)
