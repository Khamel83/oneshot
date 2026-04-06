"""Session recorder — append-only event log + SQLite index.

Records every significant turn in a Claude Code session:
- User requests (what was asked)
- Assistant actions (what was done)
- Files read/written
- Decisions made
- Tool calls (summary, not raw output)

Storage:
  {project}/.oneshot/
    events.jsonl        # Append-only raw events (one JSON line per turn)
    intelligence.db     # SQLite index for queries

Events are ~200-500 bytes each. A 100-turn session = ~30KB.
SQLite index is rebuilt on demand from JSONL (source of truth is the JSONL).
"""

import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _project_dir() -> Path:
    """Get current project root (directory with .git)."""
    cwd = Path(os.getcwd())
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists():
            return parent
    return cwd


def _oneshot_dir() -> Path:
    """Get/create .oneshot directory in project root."""
    d = _project_dir() / ".oneshot"
    d.mkdir(exist_ok=True)
    return d


EVENT_TYPES = [
    "user_request",    # What the user asked for
    "action_taken",    # What the assistant did (file edit, tool call, etc.)
    "file_read",       # A file was read
    "file_written",    # A file was created/edited
    "decision",        # A decision was made (routing, approach, etc.)
    "blocker",         # Something is blocked
    "discovery",       # Something was learned (bug found, pattern noticed)
    "commit",          # A git commit was made
    "session_start",   # Session began
    "session_end",     # Session ended
    "summary",         # A summary was generated (by janitor or user)
    "error",           # An error occurred
]


class SessionRecorder:
    """Append-only session event recorder."""

    def __init__(self, project_dir: Optional[str] = None):
        self._dir = Path(project_dir) / ".oneshot" if project_dir else _oneshot_dir()
        self._dir.mkdir(exist_ok=True)
        self._events_path = self._dir / "events.jsonl"
        self._db_path = self._dir / "intelligence.db"
        self._session_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        self._turn_count = 0

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def events_path(self) -> Path:
        return self._events_path

    def record(
        self,
        event_type: str,
        content: str,
        metadata: Optional[dict] = None,
        files: Optional[list[str]] = None,
    ) -> dict:
        """Record an event to the append-only JSONL log.

        Args:
            event_type: One of EVENT_TYPES.
            content: Human-readable description of what happened.
            metadata: Optional structured data (tool name, exit code, etc.).
            files: Optional list of file paths involved.

        Returns:
            The event dict that was written.
        """
        self._turn_count += 1
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session": self._session_id,
            "turn": self._turn_count,
            "type": event_type,
            "content": content,
            "meta": metadata or {},
            "files": files or [],
        }
        with open(self._events_path, "a") as f:
            f.write(json.dumps(event, separators=(",", ":")) + "\n")
        return event

    def record_user_request(self, what: str):
        """Record what the user asked for."""
        return self.record("user_request", what)

    def record_action(self, what: str, tool: str = "", files: list[str] | None = None):
        """Record an action taken by the assistant."""
        return self.record("action_taken", what, metadata={"tool": tool}, files=files)

    def record_file_read(self, path: str):
        """Record a file being read."""
        return self.record("file_read", f"Read {path}", files=[path])

    def record_file_written(self, path: str, action: str = "edited"):
        """Record a file being written/edited."""
        return self.record("file_written", f"{action} {path}", files=[path])

    def record_decision(self, decision: str, alternatives: list[str] | None = None):
        """Record a decision that was made."""
        return self.record(
            "decision", decision,
            metadata={"alternatives": alternatives or []}
        )

    def record_blocker(self, what: str, reason: str = ""):
        """Record something that's blocked."""
        return self.record("blocker", what, metadata={"reason": reason})

    def record_discovery(self, what: str):
        """Record something learned."""
        return self.record("discovery", what)

    def record_commit(self, message: str, files: list[str] | None = None):
        """Record a git commit."""
        return self.record("commit", message, files=files)

    def record_error(self, what: str, context: str = ""):
        """Record an error."""
        return self.record("error", what, metadata={"context": context})

    def record_summary(self, summary: str, source: str = "janitor"):
        """Record a summary generated by the janitor or user."""
        return self.record("summary", summary, metadata={"source": source})

    def get_recent_events(self, n: int = 20) -> list[dict]:
        """Get the last N events from the JSONL log."""
        if not self._events_path.exists():
            return []
        events = []
        with open(self._events_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return events[-n:]

    def get_events_by_type(self, event_type: str, limit: int = 50) -> list[dict]:
        """Get events of a specific type."""
        return [
            e for e in self.get_recent_events(limit * 5)
            if e.get("type") == event_type
        ][:limit]

    def get_events_by_session(self, session_id: str) -> list[dict]:
        """Get all events from a specific session."""
        if not self._events_path.exists():
            return []
        events = []
        with open(self._events_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        e = json.loads(line)
                        if e.get("session") == session_id:
                            events.append(e)
                    except json.JSONDecodeError:
                        continue
        return events

    def get_decisions(self) -> list[dict]:
        """Get all recorded decisions."""
        return self.get_events_by_type("decision")

    def get_blockers(self) -> list[dict]:
        """Get all recorded blockers."""
        return self.get_events_by_type("blocker")

    def get_files_touched(self) -> dict[str, list[str]]:
        """Get all files touched, grouped by action type."""
        result: dict[str, list[str]] = {"read": [], "written": [], "committed": []}
        for event in self.get_recent_events(200):
            t = event.get("type")
            for f in event.get("files", []):
                if t == "file_read" and f not in result["read"]:
                    result["read"].append(f)
                elif t == "file_written" and f not in result["written"]:
                    result["written"].append(f)
                elif t == "commit" and f not in result["committed"]:
                    result["committed"].append(f)
        return result

    def session_summary_text(self) -> str:
        """Generate a plain-text summary of the current session for LLM consumption."""
        events = self.get_events_by_session(self._session_id)
        if not events:
            return "No events recorded this session."

        lines = [f"Session {self._session_id} — {len(events)} events"]
        lines.append("")

        decisions = [e for e in events if e["type"] == "decision"]
        if decisions:
            lines.append("DECISIONS:")
            for d in decisions:
                lines.append(f"  - {d['content']}")
            lines.append("")

        blockers = [e for e in events if e["type"] == "blocker"]
        if blockers:
            lines.append("BLOCKERS:")
            for b in blockers:
                lines.append(f"  - {b['content']}")
            lines.append("")

        files_touched = set()
        for e in events:
            for f in e.get("files", []):
                files_touched.add(f)
        if files_touched:
            lines.append("FILES TOUCHED:")
            for f in sorted(files_touched):
                lines.append(f"  - {f}")
            lines.append("")

        user_requests = [e for e in events if e["type"] == "user_request"]
        if user_requests:
            lines.append("USER REQUESTS:")
            for r in user_requests:
                lines.append(f"  [{r['turn']}] {r['content'][:100]}")
            lines.append("")

        return "\n".join(lines)

    # --- SQLite index (rebuilt on demand from JSONL) ---

    def _get_db(self) -> sqlite3.Connection:
        """Get or create the SQLite database with the events table."""
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                session TEXT NOT NULL,
                turn INTEGER NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                meta TEXT DEFAULT '{}',
                files TEXT DEFAULT '[]'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts)")
        conn.commit()
        return conn

    def rebuild_index(self):
        """Rebuild the SQLite index from the JSONL source of truth."""
        conn = self._get_db()
        conn.execute("DELETE FROM events")

        if not self._events_path.exists():
            conn.close()
            return

        count = 0
        with open(self._events_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    conn.execute(
                        "INSERT INTO events (ts, session, turn, type, content, meta, files) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            e["ts"],
                            e["session"],
                            e["turn"],
                            e["type"],
                            e["content"],
                            json.dumps(e.get("meta", {})),
                            json.dumps(e.get("files", [])),
                        )
                    )
                    count += 1
                except (json.JSONDecodeError, KeyError):
                    continue

        conn.commit()
        conn.close()
        return count

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        """Run a read-only query against the SQLite index.

        Caller is responsible for rebuilding index if stale.
        """
        conn = self._get_db()
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def stats(self) -> dict:
        """Get basic stats about the event log."""
        if not self._events_path.exists():
            return {"total_events": 0, "sessions": 0, "file_size_bytes": 0}

        total = 0
        sessions = set()
        with open(self._events_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    total += 1
                    sessions.add(e.get("session", ""))
                except json.JSONDecodeError:
                    continue

        return {
            "total_events": total,
            "sessions": len(sessions),
            "file_size_bytes": self._events_path.stat().st_size,
        }
