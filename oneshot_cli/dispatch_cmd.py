"""oneshot dispatch command."""

import click


@click.command()
@click.option("--lane", required=True, help="Lane name (e.g. routine_coder)")
@click.option("--task", default=None, help="Task description (inline)")
@click.option(
    "--task-file",
    default=None,
    type=click.Path(exists=True),
    help="Path to task markdown",
)
@click.option(
    "--runner", default=None, help="Runner template name (default: auto from provider)"
)
@click.option("--allow-dirty", is_flag=True, help="Skip dirty-tree check")
def cli(lane, task, task_file, runner, allow_dirty):
    """Dispatch a bounded task to an external worker and execute it in a worktree."""
    from oneshot_cli.tasks import dispatch

    dispatch(
        lane,
        task_text=task,
        task_file=task_file,
        runner=runner,
        allow_dirty=allow_dirty,
    )
