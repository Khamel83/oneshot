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


class TaskCategory(str, Enum):
    coding = "coding"
    research = "research"
    writing = "writing"
    review = "review"
    general = "general"


class TaskClass(str, Enum):
    plan = "plan"
    research = "research"
    search_sweep = "search_sweep"
    implement_small = "implement_small"
    implement_medium = "implement_medium"
    test_write = "test_write"
    review_diff = "review_diff"
    adversarial_review = "adversarial_review"
    doc_draft = "doc_draft"
    summarize_findings = "summarize_findings"
    # Janitor class — background maintenance, always routes to free lane
    janitor_summarize = "janitor_summarize"
    janitor_extract = "janitor_extract"
    janitor_hygiene = "janitor_hygiene"
    janitor_analyze = "janitor_analyze"


@dataclass
class Task:
    task_class: TaskClass
    description: str
    lane: Optional[str] = None
    max_task_size: TaskSize = TaskSize.medium
    requires_review: bool = True
    requires_search: bool = False
    risk_level: RiskLevel = RiskLevel.medium
    category: TaskCategory = TaskCategory.general


# Routing contract: task_class -> default lane
LANE_ASSIGNMENTS = {
    TaskClass.plan: "premium",
    TaskClass.research: "research",
    TaskClass.search_sweep: "research",
    TaskClass.implement_small: "cheap",
    TaskClass.implement_medium: "balanced",
    TaskClass.test_write: "cheap",
    TaskClass.review_diff: "premium",
    TaskClass.adversarial_review: "balanced",
    TaskClass.doc_draft: "cheap",
    TaskClass.summarize_findings: "cheap",
    # Janitor tasks always go to free lane
    TaskClass.janitor_summarize: "janitor",
    TaskClass.janitor_extract: "janitor",
    TaskClass.janitor_hygiene: "janitor",
    TaskClass.janitor_analyze: "janitor",
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


# Category assignment: task_class -> default category
CATEGORY_ASSIGNMENTS = {
    TaskClass.plan: TaskCategory.general,
    TaskClass.research: TaskCategory.research,
    TaskClass.search_sweep: TaskCategory.research,
    TaskClass.implement_small: TaskCategory.coding,
    TaskClass.implement_medium: TaskCategory.coding,
    TaskClass.test_write: TaskCategory.coding,
    TaskClass.review_diff: TaskCategory.review,
    TaskClass.adversarial_review: TaskCategory.review,
    TaskClass.doc_draft: TaskCategory.writing,
    TaskClass.summarize_findings: TaskCategory.writing,
    # Janitor tasks are always general
    TaskClass.janitor_summarize: TaskCategory.general,
    TaskClass.janitor_extract: TaskCategory.general,
    TaskClass.janitor_hygiene: TaskCategory.general,
    TaskClass.janitor_analyze: TaskCategory.general,
}

CODING_KEYWORDS = [
    "implement", "code", "fix", "refactor", "bug", "feature", "add function",
    "add method", "add class", "write test", "create test", "build", "api",
    "endpoint", "handler", "migrate", "schema", "query", "database",
    "error handling", "format", "deploy", "lint",
]

RESEARCH_KEYWORDS = [
    "research", "investigate", "explore", "search", "find", "look up",
    "discover", "understand", "learn about", "compare", "evaluate",
    "benchmark", "profile", "analyze", "discover",
]

WRITING_KEYWORDS = [
    "document", "write doc", "readme", "comment", "summarize", "draft",
    "write up", "explain", "describe", "notes", "synthesis",
    "write a", "update the", "release notes",
]

REVIEW_KEYWORDS = [
    "review", "audit", "inspect", "check", "verify", "validate",
    "quality", "challenge", "adversarial",
]

JANITOR_KEYWORDS = [
    "janitor", "summarize session", "extract decisions", "memory hygiene",
    "compact memory", "analyze traces", "dedup memory", "session digest",
    "file tracker", "stale detection", "dependency graph", "config drift",
]


def infer_category(description: str) -> TaskCategory:
    """Infer task category from description keywords.

    Priority: writing > review > coding > research > general.
    Writing and review are checked first because their intent verbs
    (document, summarize, review, audit) are strong signals that
    override incidental coding/research nouns (api, endpoint, profile).
    """
    desc_lower = description.lower()

    for kw in WRITING_KEYWORDS:
        if kw in desc_lower:
            return TaskCategory.writing

    for kw in REVIEW_KEYWORDS:
        if kw in desc_lower:
            return TaskCategory.review

    for kw in CODING_KEYWORDS:
        if kw in desc_lower:
            return TaskCategory.coding

    for kw in RESEARCH_KEYWORDS:
        if kw in desc_lower:
            return TaskCategory.research

    return TaskCategory.general
