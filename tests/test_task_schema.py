"""Tests for core/task_schema.py — task classification and risk inference."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.task_schema import (
    CATEGORY_ASSIGNMENTS,
    HIGH_RISK_KEYWORDS,
    LANE_ASSIGNMENTS,
    LOW_RISK_KEYWORDS,
    RISK_AUTONOMY,
    CODING_KEYWORDS,
    RESEARCH_KEYWORDS,
    WRITING_KEYWORDS,
    REVIEW_KEYWORDS,
    JANITOR_KEYWORDS,
    RiskLevel,
    Task,
    TaskCategory,
    TaskClass,
    TaskSize,
    infer_category,
    infer_risk,
)


# ── Enum completeness ──

class TestEnums:
    def test_task_class_values(self):
        expected = {
            "plan", "research", "search_sweep", "implement_small",
            "implement_medium", "test_write", "review_diff",
            "adversarial_review", "doc_draft", "summarize_findings",
            "janitor_summarize", "janitor_extract", "janitor_hygiene",
            "janitor_analyze",
        }
        assert {tc.value for tc in TaskClass} == expected

    def test_task_category_values(self):
        assert {c.value for c in TaskCategory} == {"coding", "research", "writing", "review", "general"}

    def test_risk_level_values(self):
        assert {r.value for r in RiskLevel} == {"low", "medium", "high"}


# ── Lane assignments ──

class TestLaneAssignments:
    def test_all_task_classes_have_lane(self):
        for tc in TaskClass:
            assert tc in LANE_ASSIGNMENTS, f"{tc} missing from LANE_ASSIGNMENTS"

    def test_coding_tasks_on_non_janitor_lanes(self):
        for tc in [TaskClass.implement_small, TaskClass.implement_medium, TaskClass.test_write]:
            assert LANE_ASSIGNMENTS[tc] != "janitor"

    def test_janitor_tasks_always_on_janitor_lane(self):
        for tc in [TaskClass.janitor_summarize, TaskClass.janitor_extract,
                    TaskClass.janitor_hygiene, TaskClass.janitor_analyze]:
            assert LANE_ASSIGNMENTS[tc] == "janitor"

    def test_plan_on_premium(self):
        assert LANE_ASSIGNMENTS[TaskClass.plan] == "premium"

    def test_research_on_research(self):
        assert LANE_ASSIGNMENTS[TaskClass.research] == "research"


# ── Category assignments ──

class TestCategoryAssignments:
    def test_all_task_classes_have_category(self):
        for tc in TaskClass:
            assert tc in CATEGORY_ASSIGNMENTS, f"{tc} missing from CATEGORY_ASSIGNMENTS"

    def test_janitor_categories_are_general(self):
        for tc in [TaskClass.janitor_summarize, TaskClass.janitor_extract,
                    TaskClass.janitor_hygiene, TaskClass.janitor_analyze]:
            assert CATEGORY_ASSIGNMENTS[tc] == TaskCategory.general


# ── infer_category ──

class TestInferCategory:
    def test_coding_keywords(self):
        for kw in ["implement", "fix", "refactor", "bug", "feature", "api", "endpoint"]:
            assert infer_category(f"{kw} the handler") == TaskCategory.coding

    def test_research_keywords(self):
        for kw in ["research", "investigate", "explore", "search"]:
            assert infer_category(f"{kw} Supabase RLS") == TaskCategory.research

    def test_writing_keywords(self):
        for kw in ["document", "readme", "summarize", "draft", "notes"]:
            assert infer_category(f"{kw} the API endpoints") == TaskCategory.writing

    def test_review_keywords(self):
        for kw in ["review", "audit", "inspect", "validate"]:
            assert infer_category(f"{kw} this pull request") == TaskCategory.review

    def test_general_fallback(self):
        assert infer_category("hello world") == TaskCategory.general
        assert infer_category("do something") == TaskCategory.general
        # "update the" matches WRITING_KEYWORDS["update the"] — that's correct behavior
        # "modify some code" matches CODING_KEYWORDS["code"] — correct behavior
        # A truly general description that hits no keywords is hard to find
        assert infer_category("have a conversation") == TaskCategory.general

    def test_writing_overrides_coding(self):
        # "document the API" — writing intent overrides coding noun
        assert infer_category("document the API endpoints") == TaskCategory.writing

    def test_review_overrides_research(self):
        assert infer_category("review the research findings") == TaskCategory.review

    def test_specific_task_descriptions(self):
        assert infer_category("implement the auth handler") == TaskCategory.coding
        assert infer_category("fix the bug in login.py") == TaskCategory.coding
        assert infer_category("research Supabase RLS patterns") == TaskCategory.research
        assert infer_category("summarize the meeting notes") == TaskCategory.writing
        assert infer_category("review this pull request") == TaskCategory.review
        assert infer_category("audit the security config") == TaskCategory.review


# ── infer_risk ──

class TestInferRisk:
    def test_high_risk_keywords(self):
        for kw in HIGH_RISK_KEYWORDS:
            assert infer_risk(f"update {kw} settings") == RiskLevel.high

    def test_low_risk_keywords(self):
        for kw in LOW_RISK_KEYWORDS:
            assert infer_risk(f"add {kw} to the module") == RiskLevel.low

    def test_medium_risk_default(self):
        assert infer_risk("update the thing") == RiskLevel.medium
        assert infer_risk("modify some code") == RiskLevel.medium

    def test_high_risk_in_files(self):
        assert infer_risk("fix the bug", ["auth.py", "login.py"]) == RiskLevel.high

    def test_risk_from_files_only(self):
        assert infer_risk("update something", ["test_auth.py"]) == RiskLevel.high

    def test_high_risk_takes_priority_over_low(self):
        # "auth" (high) should win over "refactor" (low)
        assert infer_risk("refactor auth module") == RiskLevel.high


# ── Risk autonomy ──

class TestRiskAutonomy:
    def test_all_risk_levels_have_autonomy(self):
        for rl in RiskLevel:
            assert rl in RISK_AUTONOMY, f"{rl} missing from RISK_AUTONOMY"

    def test_low_risk_no_approval(self):
        assert RISK_AUTONOMY[RiskLevel.low]["requires_approval"] is False
        assert RISK_AUTONOMY[RiskLevel.low]["auto_edit"] is True

    def test_high_risk_requires_approval(self):
        assert RISK_AUTONOMY[RiskLevel.high]["requires_approval"] is True
        assert RISK_AUTONOMY[RiskLevel.high]["auto_edit"] is False
        assert RISK_AUTONOMY[RiskLevel.high]["synchronous_only"] is True

    def test_medium_risk_needs_approval(self):
        assert RISK_AUTONOMY[RiskLevel.medium]["requires_approval"] is True


# ── Keyword coverage ──

class TestKeywordLists:
    def test_no_duplicates_in_keyword_lists(self):
        for name, kws in [("CODING", CODING_KEYWORDS), ("RESEARCH", RESEARCH_KEYWORDS),
                           ("WRITING", WRITING_KEYWORDS), ("REVIEW", REVIEW_KEYWORDS),
                           ("JANITOR", JANITOR_KEYWORDS)]:
            assert len(kws) == len(set(kws)), f"{name}_KEYWORDS has duplicates"
