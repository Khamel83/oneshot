"""Repo-first memory helpers for OneShot and customer repos."""

from __future__ import annotations

import re
import sqlite3
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


STABLE_DIR = Path("docs") / "agents"
OP_DIR = Path(".oneshot")
OP_SUBDIRS = (
    "sessions",
    "checkpoints",
    "conflicts",
    "provenance",
    "abstractions",
    "index",
)
POLICY_MODES = {"portable", "isolated", "sensitive", "private"}
REVIEW_GATES = {"normal", "high-risk-quorum"}


def global_index_root() -> Path:
    env = os.environ.get("ONESHOT_MEMORY_INDEX_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".local" / "state" / "oneshot" / "memory-index").resolve()


def global_index_db() -> Path:
    return global_index_root() / "memory.db"


def repo_root(path: str | Path | None = None) -> Path:
    return Path(path or Path.cwd()).resolve()


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_day() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "entry"


def _write_if_missing(path: Path, content: str, force: bool = False) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return True


def _append(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + content)


def scaffold(
    repo: str | Path | None = None, mode: str = "isolated", force: bool = False
) -> dict:
    if mode not in POLICY_MODES:
        raise ValueError(
            f"Invalid mode '{mode}'. Expected one of: {', '.join(sorted(POLICY_MODES))}"
        )

    root = repo_root(repo)
    stable = root / STABLE_DIR
    op = root / OP_DIR
    stable.mkdir(parents=True, exist_ok=True)
    op.mkdir(parents=True, exist_ok=True)
    for subdir in OP_SUBDIRS:
        (op / subdir).mkdir(parents=True, exist_ok=True)

    created = []
    templates = {
        stable / "MEMORY_POLICY.md": _policy_template(mode),
        stable
        / "DECISIONS.md": "# Decisions\n\nDurable decisions and supersessions.\n",
        stable
        / "BLOCKERS.md": "# Blockers\n\nActive blockers and resolved lessons worth preserving.\n",
        stable
        / "RUNBOOKS.md": "# Runbooks\n\nImportant commands and operational procedures.\n",
        stable
        / "CONTEXT.md": "# Context\n\nStable architecture or domain summary for this repo.\n",
        op / ".gitignore": _gitignore_template(),
    }
    for path, content in templates.items():
        if _write_if_missing(path, content, force=force):
            created.append(path)

    return {"repo_root": root, "created": created}


def _policy_template(mode: str) -> str:
    return (
        "# Memory Policy\n\n"
        f"- mode: {mode}\n"
        "- owner: repo\n"
        "- commit_stable_memory: true\n"
        f"- allow_cross_repo_abstractions: {'true' if mode != 'private' else 'false'}\n"
        "- allow_raw_cross_repo_retrieval: false\n"
        "- secrets_policy: never-store\n"
        "- summary_cadence: checkpoint-and-session-end\n"
        f"- review_gate: {'high-risk-quorum' if mode in {'sensitive', 'private'} else 'normal'}\n"
    )


def _gitignore_template() -> str:
    return "sessions/\ncheckpoints/\nindex/\nconflicts/\nprovenance/\n"


def create_provenance(
    repo: str | Path | None,
    title: str,
    source_tool: str,
    source_session: str,
    source_type: str,
    confidence: str,
    notes: str = "",
) -> tuple[str, Path]:
    root = repo_root(repo)
    prov_dir = root / OP_DIR / "provenance"
    prov_dir.mkdir(parents=True, exist_ok=True)
    entry_id = f"{_now_day()}-{_slugify(title)}"
    path = prov_dir / f"{entry_id}.md"
    path.write_text(
        "# Provenance\n"
        f"- id: {entry_id}\n"
        f"- created_at: {_now_iso()}\n"
        f"- repo: {root.name}\n"
        f"- source_tool: {source_tool}\n"
        f"- source_session: {source_session}\n"
        f"- source_type: {source_type}\n"
        f"- confidence: {confidence}\n"
        f"- notes: {notes or 'none'}\n"
    )
    return entry_id, path


def promote_decision(
    repo: str | Path | None,
    title: str,
    summary: str,
    rationale: str,
    status: str = "active",
    source_tool: str = "manual",
    source_session: str = "local-session",
    source_type: str = "manual-promotion",
    confidence: str = "medium",
    notes: str = "",
    supersedes: str = "",
) -> dict:
    root = repo_root(repo)
    _, prov_path = create_provenance(
        root, title, source_tool, source_session, source_type, confidence, notes
    )
    content = (
        f"## {_now_day()} - {title}\n"
        f"- status: {status}\n"
        f"- source: {source_tool}\n"
        f"- provenance: {prov_path.relative_to(root)}\n"
        f"- summary: {summary}\n"
        f"- rationale: {rationale}\n"
        f"- supersedes: {supersedes or 'none'}\n\n"
    )
    target = root / STABLE_DIR / "DECISIONS.md"
    _append(target, content)
    return {"target": target, "provenance": prov_path}


def promote_blocker(
    repo: str | Path | None,
    title: str,
    blocker: str,
    resolution: str = "",
    status: str = "active",
    source_tool: str = "manual",
    source_session: str = "local-session",
    source_type: str = "manual-promotion",
    confidence: str = "medium",
    notes: str = "",
    follow_up: str = "",
) -> dict:
    root = repo_root(repo)
    _, prov_path = create_provenance(
        root, title, source_tool, source_session, source_type, confidence, notes
    )
    content = (
        f"## {_now_day()} - {title}\n"
        f"- status: {status}\n"
        f"- source: {source_tool}\n"
        f"- provenance: {prov_path.relative_to(root)}\n"
        f"- blocker: {blocker}\n"
        f"- resolution: {resolution or 'pending'}\n"
        f"- follow_up: {follow_up or 'none'}\n\n"
    )
    target = root / STABLE_DIR / "BLOCKERS.md"
    _append(target, content)
    return {"target": target, "provenance": prov_path}


def promote_runbook(
    repo: str | Path | None,
    title: str,
    when_to_use: str,
    procedure: str,
    notes_text: str = "",
    source_tool: str = "manual",
    source_session: str = "local-session",
    source_type: str = "manual-promotion",
    confidence: str = "medium",
    notes: str = "",
) -> dict:
    root = repo_root(repo)
    _, prov_path = create_provenance(
        root, title, source_tool, source_session, source_type, confidence, notes
    )
    content = (
        f"## Runbook: {title}\n"
        "- status: active\n"
        f"- source: {source_tool}\n"
        f"- provenance: {prov_path.relative_to(root)}\n\n"
        "### When to use\n"
        f"{when_to_use}\n\n"
        "### Command / procedure\n"
        "```bash\n"
        f"{procedure.rstrip()}\n"
        "```\n\n"
        "### Notes\n"
        f"{notes_text or 'none'}\n\n"
    )
    target = root / STABLE_DIR / "RUNBOOKS.md"
    _append(target, content)
    return {"target": target, "provenance": prov_path}


def capture_session_summary(
    repo: str | Path | None,
    title: str,
    summary: str,
    source_tool: str = "manual",
    source_session: str = "local-session",
    confidence: str = "medium",
    notes: str = "",
) -> dict:
    root = repo_root(repo)
    entry_id, prov_path = create_provenance(
        root, title, source_tool, source_session, "session", confidence, notes
    )
    target = root / OP_DIR / "sessions" / f"{entry_id}.md"
    target.write_text(
        f"# Session Summary: {title}\n\n"
        f"- source: {source_tool}\n"
        f"- provenance: {prov_path.relative_to(root)}\n\n"
        f"{summary.rstrip()}\n"
    )
    return {"target": target, "provenance": prov_path}


def create_abstraction(
    repo: str | Path | None,
    title: str,
    lesson: str,
    category: str,
    trust: str,
    sensitivity: str,
    removed_details: str = "",
    promotes_from: str = "",
) -> dict:
    root = repo_root(repo)
    abstraction_dir = root / OP_DIR / "abstractions"
    abstraction_dir.mkdir(parents=True, exist_ok=True)
    entry_id = f"{_now_day()}-{_slugify(title)}"
    target = abstraction_dir / f"{entry_id}.md"
    target.write_text(
        "# Abstraction\n"
        f"- title: {title}\n"
        f"- id: {entry_id}\n"
        f"- source_repo: {root.name}\n"
        f"- trust: {trust}\n"
        f"- sensitivity: {sensitivity}\n"
        f"- category: {category}\n"
        f"- promotes_from: {promotes_from or 'none'}\n\n"
        "## Lesson\n"
        f"{lesson.rstrip()}\n\n"
        "## Non-portable details removed\n"
        f"{removed_details or 'none'}\n"
    )
    return {"target": target}


@dataclass
class SearchResult:
    source: str
    title: str
    body: str
    score: int
    priority: int
    conflicted: bool = False
    superseded: bool = False


def retrieve_same_repo(
    repo: str | Path | None, query: str, limit: int = 10
) -> list[SearchResult]:
    root = repo_root(repo)
    terms = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if t]
    files = [
        (root / STABLE_DIR / "DECISIONS.md", 0),
        (root / STABLE_DIR / "BLOCKERS.md", 1),
        (root / STABLE_DIR / "RUNBOOKS.md", 2),
        (root / STABLE_DIR / "CONTEXT.md", 3),
    ]

    results: list[SearchResult] = []
    for path, priority in files:
        results.extend(_search_path(path, terms, priority))

    op_base = root / OP_DIR
    for subdir, priority in (
        ("conflicts", 4),
        ("sessions", 5),
        ("checkpoints", 6),
        ("abstractions", 7),
    ):
        directory = op_base / subdir
        if directory.exists():
            for path in sorted(directory.glob("*.md")):
                results.extend(
                    _search_path(path, terms, priority, treat_whole_file=True)
                )

    results.sort(key=lambda r: (r.priority, r.superseded, -r.score, r.source, r.title))
    return [r for r in results if r.score > 0][:limit]


def _search_path(
    path: Path, terms: Iterable[str], priority: int, treat_whole_file: bool = False
) -> list[SearchResult]:
    if not path.exists():
        return []
    text = path.read_text()
    if treat_whole_file:
        sections = [(_extract_metadata(text).get("title", path.stem), text)]
    else:
        sections = _split_sections(text)
    results = []
    for title, body in sections:
        haystack = f"{title}\n{body}".lower()
        score = sum(haystack.count(term) for term in terms) if terms else 1
        conflicted = path.parts[-2] == "conflicts" or "- status: conflicted" in haystack
        superseded = "- status: superseded" in haystack
        if score > 0:
            results.append(
                SearchResult(
                    source=str(path),
                    title=title,
                    body=_snippet(body, terms),
                    score=score,
                    priority=priority,
                    conflicted=conflicted,
                    superseded=superseded,
                )
            )
    return results


def _split_sections(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_title = "document"
    current_body: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if current_body:
                sections.append((current_title, current_body))
            current_title = line[3:].strip()
            current_body = []
        else:
            current_body.append(line)
    if current_body or not sections:
        sections.append((current_title, current_body))
    return [(title, "\n".join(body).strip()) for title, body in sections]


def _snippet(body: str, terms: Iterable[str], max_chars: int = 240) -> str:
    text = re.sub(r"\s+", " ", body).strip()
    if len(text) <= max_chars:
        return text
    lowered = text.lower()
    positions = [
        lowered.find(term) for term in terms if term and lowered.find(term) >= 0
    ]
    if positions:
        start = max(0, min(positions) - 60)
        end = min(len(text), start + max_chars)
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        return prefix + text[start:end].strip() + suffix
    return text[: max_chars - 3].rstrip() + "..."


def load_policy(repo: str | Path | None) -> dict:
    root = repo_root(repo)
    policy_path = root / STABLE_DIR / "MEMORY_POLICY.md"
    if not policy_path.exists():
        return {
            "mode": "isolated",
            "owner": "repo",
            "commit_stable_memory": "true",
            "allow_cross_repo_abstractions": "true",
            "allow_raw_cross_repo_retrieval": "false",
            "secrets_policy": "never-store",
            "summary_cadence": "checkpoint-and-session-end",
            "review_gate": "normal",
        }
    data: dict[str, str] = {}
    for line in policy_path.read_text().splitlines():
        match = re.match(r"^-\s+([a-z_]+):\s+(.*)$", line.strip())
        if match:
            data[match.group(1)] = match.group(2).strip()
    return data


def _connect_index() -> sqlite3.Connection:
    db_path = global_index_db()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            repo_root TEXT NOT NULL,
            repo_name TEXT NOT NULL,
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            sensitivity TEXT NOT NULL,
            source_path TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_kind ON documents(kind)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_documents_repo ON documents(repo_root)"
    )
    return conn


def index_repo_memory(repo: str | Path | None) -> dict:
    root = repo_root(repo)
    policy = load_policy(root)
    conn = _connect_index()
    with conn:
        conn.execute("DELETE FROM documents WHERE repo_root = ?", (str(root),))
        count = 0
        count += _index_markdown_file(
            conn,
            root,
            root / STABLE_DIR / "DECISIONS.md",
            "decision",
            policy.get("mode", "isolated"),
        )
        count += _index_markdown_file(
            conn,
            root,
            root / STABLE_DIR / "BLOCKERS.md",
            "blocker",
            policy.get("mode", "isolated"),
        )
        count += _index_markdown_file(
            conn,
            root,
            root / STABLE_DIR / "RUNBOOKS.md",
            "runbook",
            policy.get("mode", "isolated"),
        )
        count += _index_markdown_file(
            conn,
            root,
            root / STABLE_DIR / "CONTEXT.md",
            "context",
            policy.get("mode", "isolated"),
            treat_whole_file=True,
        )
        abstractions_dir = root / OP_DIR / "abstractions"
        if abstractions_dir.exists():
            for abstraction in sorted(abstractions_dir.glob("*.md")):
                count += _index_markdown_file(
                    conn,
                    root,
                    abstraction,
                    "abstraction",
                    _extract_metadata(abstraction.read_text()).get(
                        "sensitivity", policy.get("mode", "isolated")
                    ),
                    treat_whole_file=True,
                )
    conn.close()
    return {"repo_root": root, "indexed": count, "db": global_index_db()}


def _index_markdown_file(
    conn: sqlite3.Connection,
    root: Path,
    path: Path,
    kind: str,
    sensitivity: str,
    treat_whole_file: bool = False,
) -> int:
    if not path.exists():
        return 0
    text = path.read_text()
    if treat_whole_file:
        sections = [(_extract_metadata(text).get("title", path.stem), text)]
    else:
        sections = _split_sections(text)
    count = 0
    for title, body in sections:
        doc_id = f"{root}:{path}:{title}"
        conn.execute(
            """
            INSERT OR REPLACE INTO documents (id, repo_root, repo_name, kind, title, body, sensitivity, source_path, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                str(root),
                root.name,
                kind,
                title,
                body,
                sensitivity,
                str(path.relative_to(root)),
                _now_iso(),
            ),
        )
        count += 1
    return count


def search_cross_repo_abstractions(
    query: str, current_repo: str | Path | None = None, limit: int = 10
) -> dict:
    current = str(repo_root(current_repo)) if current_repo else None
    terms = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if t]
    try:
        conn = _connect_index()
    except Exception as exc:  # pragma: no cover - exercised via CLI behavior
        return {"status": "degraded", "reason": str(exc), "results": []}

    try:
        rows = conn.execute(
            "SELECT repo_root, repo_name, title, body, sensitivity, source_path FROM documents WHERE kind = 'abstraction'"
        ).fetchall()
    finally:
        conn.close()

    results = []
    for repo_root_value, repo_name, title, body, sensitivity, source_path in rows:
        if current and repo_root_value == current:
            continue
        if sensitivity in {"private", "sensitive"}:
            continue
        haystack = f"{title}\n{body}".lower()
        score = sum(haystack.count(term) for term in terms) if terms else 1
        if score > 0:
            results.append(
                {
                    "repo_name": repo_name,
                    "title": title,
                    "source_path": source_path,
                    "sensitivity": sensitivity,
                    "score": score,
                    "snippet": _snippet(body, terms),
                }
            )
    results.sort(key=lambda item: (-item["score"], item["repo_name"], item["title"]))
    return {"status": "ok", "results": results[:limit]}


def _extract_metadata(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^-\s+([a-z_]+):\s+(.*)$", line.strip())
        if match:
            data[match.group(1)] = match.group(2).strip()
    return data
