"""oneshot escalate — placeholder, implemented in T3."""
import click

@click.command()
@click.argument("task_id", required=True)
@click.option("--lane", required=True, help="Escalation lane (stronger than parent)")
def cli(task_id, lane):
    """Create an escalated follow-up task."""
    from oneshot_cli.tasks import escalate
    escalate(task_id, lane)
