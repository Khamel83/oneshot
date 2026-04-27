"""oneshot collect — placeholder, implemented in T3."""
import click

@click.command()
@click.argument("task_id", required=True)
def cli(task_id):
    """Collect worker results (diff, test log) from a worktree."""
    from oneshot_cli.tasks import collect
    collect(task_id)
