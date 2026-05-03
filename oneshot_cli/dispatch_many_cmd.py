"""oneshot dispatch-many command — parallel fan-out dispatch."""

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import click


@click.command()
@click.option("--lane", required=True, help="Lane name (e.g. routine_coder)")
@click.option(
    "--task-file",
    "task_files",
    multiple=True,
    required=True,
    type=click.Path(exists=True),
    help="Path to a task markdown file. Repeat for each parallel task.",
)
@click.option("--allow-dirty", is_flag=True, help="Skip dirty-tree check")
def cli(lane, task_files, allow_dirty):
    """Dispatch multiple tasks in parallel. Each gets its own worktree and worker.

    Example:
        ./bin/oneshot dispatch-many --lane routine_coder \\
            --task-file /tmp/fix-a.md \\
            --task-file /tmp/fix-b.md \\
            --task-file /tmp/fix-c.md
    """
    from oneshot_cli.tasks import dispatch

    if len(task_files) == 1:
        click.echo("Tip: for a single task, use `dispatch` instead of `dispatch-many`")

    click.echo(f"Dispatching {len(task_files)} tasks in parallel on lane '{lane}'...")

    results = {}

    def run_one(tf):
        task_id = dispatch(lane, task_file=tf, allow_dirty=allow_dirty)
        return tf, task_id

    with ThreadPoolExecutor(max_workers=len(task_files)) as executor:
        futures = {executor.submit(run_one, tf): tf for tf in task_files}
        for future in as_completed(futures):
            tf = futures[future]
            try:
                _, task_id = future.result()
                results[tf] = task_id
            except Exception as e:
                click.echo(f"  ERROR dispatching {tf}: {e}", err=True)
                results[tf] = None

    click.echo("\nAll tasks dispatched:")
    failed = 0
    for tf, task_id in results.items():
        if task_id:
            click.echo(f"  {task_id}  ← {tf}")
            click.echo(f"    collect: ./bin/oneshot collect {task_id}")
        else:
            click.echo(f"  FAILED  ← {tf}")
            failed += 1

    if failed:
        sys.exit(1)
