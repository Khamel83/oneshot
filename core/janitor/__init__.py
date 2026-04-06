"""OneShot Janitor — Background intelligence layer.

Free model processing for session recording, decision extraction,
memory hygiene, and project intelligence tasks.

All jobs route to openrouter/free via the janitor lane.
Cost: $0. Storage: append-only JSONL + SQLite index.
"""

from core.janitor.recorder import SessionRecorder
from core.janitor.worker import call_free, extract_structured

__all__ = ["SessionRecorder", "call_free", "extract_structured"]
