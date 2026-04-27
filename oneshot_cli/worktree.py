"""Git worktree management for oneshot tasks."""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKTREE_PARENT = REPO_ROOT.parent / "oneshot-worktrees"


def worktree_path(task_id: str) -> Path:
    return WORKTREE_PARENT / task_id


def branch_name(task_id: str) -> str:
    return f"worker/{task_id}"


def create(task_id: str) -> Path:
    """Create a worktree at ../oneshot-worktrees/<task_id> on branch worker/<task_id>."""
    wp = worktree_path(task_id)
    if wp.exists():
        raise FileExistsError(f"Worktree already exists: {wp}")
    wp.parent.mkdir(parents=True, exist_ok=True)

    br = branch_name(task_id)
    subprocess.run(
        ["git", "worktree", "add", str(wp), "-b", br, "HEAD"],
        check=True, cwd=REPO_ROOT,
    )
    return wp


def remove(task_id: str) -> None:
    """Remove worktree and delete its branch."""
    wp = worktree_path(task_id)
    br = branch_name(task_id)

    subprocess.run(["git", "worktree", "remove", "-f", str(wp)], check=True, cwd=REPO_ROOT)
    subprocess.run(["git", "branch", "-D", br], check=True, cwd=REPO_ROOT)


def list_worktrees() -> list[dict]:
    """Return list of oneshot worktrees."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True, text=True, check=True, cwd=REPO_ROOT,
    )
    wts = []
    current = {}
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                wts.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            ref = line.split(" ", 1)[1]
            current["branch"] = ref.replace("refs/heads/", "")
        elif line == "":
            if current:
                wts.append(current)
                current = {}
    if current:
        wts.append(current)

    return [w for w in wts if "oneshot-worktrees" in w.get("path", "")]


import click


@click.group()
def cli():
    """Manage git worktrees for dispatched tasks."""
    pass


@cli.command("create")
@click.argument("task_id")
def create_cmd(task_id):
    wp = create(task_id)
    click.echo(f"Created worktree: {wp}")


@cli.command("remove")
@click.argument("task_id")
def remove_cmd(task_id):
    remove(task_id)
    click.echo(f"Removed worktree for {task_id}")


@cli.command("list")
def list_cmd():
    wts = list_worktrees()
    if not wts:
        click.echo("No oneshot worktrees.")
        return
    click.echo(f"{'PATH':<60} {'BRANCH':<40}")
    for w in wts:
        click.echo(f"{w['path']:<60} {w.get('branch', '?'):<40}")
