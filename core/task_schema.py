"""OneShot Router - Task classification and lane-based routing."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaskSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class TaskClass(str, Enum):
    plan = "plan"
    research = "research"
    search_sweep = "search_sweep"
    implement_small = "implement_small"
    implement_medium = "implement_medium"
    test_write = "test_write"
    review_diff = "review_diff"
    doc_draft = "doc_draft"
    summarize_findings = "summarize_findings"


@dataclass
class Task:
    task_class: TaskClass
    description: str
    lane: Optional[str] = None
    max_task_size: TaskSize = TaskSize.medium
    requires_review: bool = True
    requires_search: bool = False


# Routing contract: task_class -> default lane
LANE_ASSIGNMENTS = {
    TaskClass.plan: "premium",
    TaskClass.research: "research",
    TaskClass.search_sweep: "research",
    TaskClass.implement_small: "cheap",
    TaskClass.implement_medium: "balanced",
    TaskClass.test_write: "cheap",
    TaskClass.review_diff: "premium",
    TaskClass.doc_draft: "cheap",
    TaskClass.summarize_findings: "cheap",
}
