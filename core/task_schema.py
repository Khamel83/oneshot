"""OneShot Router - Task classification and lane-based routing."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaskSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


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
    risk_level: RiskLevel = RiskLevel.medium


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

# Risk-based autonomy rules
RISK_AUTONOMY = {
    RiskLevel.low: {
        "auto_edit": True,
        "auto_verify": True,
        "auto_commit": False,
        "requires_approval": False,
    },
    RiskLevel.medium: {
        "auto_edit": False,
        "auto_verify": True,
        "auto_commit": False,
        "requires_approval": True,
    },
    RiskLevel.high: {
        "auto_edit": False,
        "auto_verify": True,
        "auto_commit": False,
        "requires_approval": True,
        "synchronous_only": True,
    },
}

HIGH_RISK_KEYWORDS = [
    "auth", "billing", "migration", "security", "password",
    "token", "secret", "credential", "production", "deploy",
]

LOW_RISK_KEYWORDS = [
    "refactor", "rename", "test", "lint", "doc", "format", "comment",
]


def infer_risk(description: str, files: list[str] = None) -> RiskLevel:
    """Classify task risk based on keywords in description and file paths."""
    desc_lower = description.lower()
    all_text = desc_lower
    if files:
        all_text += " " + " ".join(f.lower() for f in files)

    for kw in HIGH_RISK_KEYWORDS:
        if kw in all_text:
            return RiskLevel.high

    for kw in LOW_RISK_KEYWORDS:
        if kw in all_text:
            return RiskLevel.low

    return RiskLevel.medium
