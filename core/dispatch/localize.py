"""File localization: identify which project files are relevant for a given task.

Pre-dispatch step that maps a natural-language task description → list of file paths.
One cheap LLM call (via janitor provider pool). Result is injected into the dispatch
prompt so the worker already knows which files to look at.

Usage:
    from core.dispatch.localize import localize_files

    files = localize_files("Fix the auth bug in login", project_dir="/path/to/repo")
    # Returns ["core/auth/login.py", "tests/test_login.py", ...]

    # Or with the full enriched prompt:
    enriched = inject_file_context(prompt, project_dir="/path/to/repo")
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

# Files to always ignore — large generated artifacts, binaries, etc.
_ALWAYS_IGNORE = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build",
    ".janitor", "eval/traces", ".pytest_cache", ".mypy_cache", "*.pyc",
}

# Max file count to send in the localization prompt (avoids token overflow)
_MAX_FILES_IN_PROMPT = 300


def _git_files(project_dir: str) -> list[str]:
    """Return all tracked files in the repo, relative to project_dir."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, cwd=project_dir, timeout=10
        )
        if result.returncode == 0:
            return [f for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        pass
    # Fallback: walk the directory
    files = []
    for root, dirs, filenames in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in _ALWAYS_IGNORE]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(root, fn), project_dir)
            files.append(rel)
    return files[:_MAX_FILES_IN_PROMPT]


def _build_prompt(task_description: str, files: list[str]) -> str:
    file_list = "\n".join(files[:_MAX_FILES_IN_PROMPT])
    return f"""You are helping identify which files in a codebase are relevant to a task.

Task: {task_description}

Available files:
{file_list}

Respond with a JSON array of file paths (strings) that are most likely relevant to this task.
Include source files, test files, and config files that the task will touch or need to understand.
Limit to the 10 most relevant files. No explanation — JSON only.

Example: ["core/auth/login.py", "tests/test_auth.py", "config/auth.yaml"]"""


def localize_files(
    task_description: str,
    project_dir: Optional[str] = None,
    max_files: int = 10,
) -> list[str]:
    """Return a list of file paths relevant to the given task.

    Uses the janitor provider pool for one cheap LLM call.
    Returns an empty list (silently) on any error — callers should treat
    localization as best-effort and proceed without it if it fails.

    Args:
        task_description: Natural-language description of the task.
        project_dir: Repo root. Defaults to CWD.
        max_files: Maximum number of files to return.
    """
    root = project_dir or os.getcwd()
    files = _git_files(root)
    if not files:
        return []

    # Skip LLM call if too few files (repo is tiny, just return them all)
    if len(files) <= 15:
        return files[:max_files]

    try:
        import sys
        repo_root = Path(__file__).resolve().parent.parent.parent
        sys.path.insert(0, str(repo_root))
        from core.janitor.provider_pool import call_janitor

        prompt = _build_prompt(task_description, files)
        raw = call_janitor(prompt, max_tokens=512, timeout=20)

        # Parse JSON array from response
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        result = json.loads(raw.strip())
        if not isinstance(result, list):
            return []

        # Validate: only return files that actually exist in the repo
        valid = []
        for f in result:
            if isinstance(f, str) and Path(os.path.join(root, f)).exists():
                valid.append(f)
        return valid[:max_files]

    except Exception:
        return []


def inject_file_context(
    prompt: str,
    task_description: Optional[str] = None,
    project_dir: Optional[str] = None,
) -> str:
    """Inject a '## Relevant Files' section into the dispatch prompt.

    If localization fails or returns nothing, prompt is returned unchanged.

    Args:
        prompt: Original dispatch prompt.
        task_description: Description for localization (defaults to first 200 chars of prompt).
        project_dir: Repo root. Defaults to CWD.
    """
    desc = task_description or prompt[:200]
    files = localize_files(desc, project_dir=project_dir)
    if not files:
        return prompt

    file_lines = "\n".join(f"- `{f}`" for f in files)
    context_block = f"\n\n## Relevant Files\n\n{file_lines}\n"

    # Insert after the first heading if present, otherwise prepend
    lines = prompt.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("## ") and i > 0:
            return "\n".join(lines[:i]) + context_block + "\n".join(lines[i:])

    return prompt + context_block
