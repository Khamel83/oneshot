"""Click entry point for oneshot CLI."""
import click

from oneshot_cli import lanes_cmd, dispatch_cmd, status_cmd, collect_cmd, review_cmd, escalate_cmd, hello_cmd


@click.group()
def cli():
    """Oneshot delegation harness — dispatch bounded tasks to external workers."""
    pass


cli.add_command(lanes_cmd.cli, name="lanes")
cli.add_command(dispatch_cmd.cli, name="dispatch")
cli.add_command(status_cmd.cli, name="status")
cli.add_command(collect_cmd.cli, name="collect")
cli.add_command(review_cmd.cli, name="review")
cli.add_command(escalate_cmd.cli, name="escalate")
cli.add_command(hello_cmd.cli, name="hello")


@cli.group()
def worktree():
    """Manage git worktrees for dispatched tasks."""
    pass


from oneshot_cli.worktree import cli as worktree_cli  # noqa: E402
for name, cmd in worktree_cli.commands.items():
    worktree.add_command(cmd, name=name)


if __name__ == "__main__":
    cli()
