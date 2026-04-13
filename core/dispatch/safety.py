"""Git safety helpers: stash-before-dispatch and rollback-on-failure.

Usage:
    from core.dispatch.safety import stash_before, rollback, is_high_risk

    # Before a high-risk dispatch:
    stash_ref = stash_before(project_dir)

    # ... run dispatch + verification ...

    # If tests failed, rollback:
    if not passed:
        rollback(project_dir, stash_ref)

Design:
- Stash only if there are staged/unstaged changes (clean trees are a no-op).
- Rollback = git stash pop (restores exactly what was stashed).
- All operations are best-effort: failures are returned as None/False, never raised.
- Stash message is always "dispatch-safety-{timestamp}" for easy identification.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional


def _git(args: list[str], cwd: str) -> tuple[int, str, str]:
    """Run a git command. Returns (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, cwd=cwd, timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def has_changes(project_dir: str) -> bool:
    """Return True if there are any staged or unstaged changes."""
    rc, out, _ = _git(["status", "--porcelain"], project_dir)
    if rc != 0:
        return False
    return bool(out.strip())


def stash_before(project_dir: str, label: str = "") -> Optional[str]:
    """Create a git stash before dispatch. Returns stash ref or None.

    Returns None if:
    - The working tree is clean (nothing to stash)
    - The stash command failed

    Args:
        project_dir: Path to git repository root.
        label: Optional label suffix for the stash message.
    """
    if not has_changes(project_dir):
        return None

    ts = int(time.time())
    msg = f"dispatch-safety-{ts}" + (f"-{label}" if label else "")
    rc, out, err = _git(["stash", "push", "-m", msg], project_dir)
    if rc != 0:
        return None

    # Verify the stash was created (git stash push returns "No local changes to save"
    # if nothing was stashed — has_changes() should have caught that, but be safe)
    if "No local changes" in out or "No local changes" in err:
        return None

    # Get the stash ref (stash@{0} is always the most recent)
    rc2, sha, _ = _git(["rev-parse", "stash@{0}"], project_dir)
    if rc2 == 0 and sha:
        return sha  # Return the SHA so we can find it even if other stashes pile up
    return "stash@{0}"


def rollback(project_dir: str, stash_ref: Optional[str]) -> bool:
    """Pop the stash to undo dispatch changes. Returns True on success.

    Args:
        project_dir: Path to git repository root.
        stash_ref: The stash ref or SHA returned by stash_before().
                   If None, does nothing and returns False.
    """
    if stash_ref is None:
        return False

    # Try by SHA first (survives other stash operations in between)
    if len(stash_ref) == 40 or (len(stash_ref) > 7 and not stash_ref.startswith("stash@")):
        # It's a SHA — find which stash@ it corresponds to
        rc, list_out, _ = _git(["stash", "list", "--format=%H %gd"], project_dir)
        if rc == 0:
            for line in list_out.splitlines():
                parts = line.split()
                if parts and parts[0].startswith(stash_ref[:7]):
                    # Found the stash by SHA prefix — pop it by index
                    stash_index = parts[1] if len(parts) > 1 else "stash@{0}"
                    rc2, _, _ = _git(["stash", "pop", stash_index], project_dir)
                    return rc2 == 0

    # Fall back to stash@{0}
    rc, _, _ = _git(["stash", "pop", stash_ref if stash_ref.startswith("stash@") else "stash@{0}"], project_dir)
    return rc == 0


def run_verification(
    commands: list[str],
    project_dir: str,
    timeout: int = 120,
) -> tuple[bool, str]:
    """Run verification commands. Returns (all_passed, combined_output).

    Stops on first failure. Output is trimmed to 2000 chars for trace embedding.

    Args:
        commands: Shell commands to run (each run via bash -c).
        project_dir: Working directory for the commands.
        timeout: Per-command timeout in seconds.
    """
    if not commands:
        return True, ""

    combined = []
    for cmd in commands:
        try:
            result = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True, text=True,
                cwd=project_dir, timeout=timeout
            )
            out = (result.stdout + result.stderr).strip()
            combined.append(f"$ {cmd}\n{out}")
            if result.returncode != 0:
                return False, "\n\n".join(combined)[-2000:]
        except subprocess.TimeoutExpired:
            combined.append(f"$ {cmd}\nTIMEOUT after {timeout}s")
            return False, "\n\n".join(combined)[-2000:]
        except Exception as e:
            combined.append(f"$ {cmd}\nERROR: {e}")
            return False, "\n\n".join(combined)[-2000:]

    return True, "\n\n".join(combined)[-2000:]


def is_high_risk(task_class: str) -> bool:
    """Return True for task classes that warrant a git stash before dispatch.

    High-risk = classes that write to source files, not just read/document.
    """
    HIGH_RISK = {
        "implement_small", "implement_medium", "implement_large",
        "refactor", "bug_fix", "migrate", "upgrade",
    }
    return task_class in HIGH_RISK
