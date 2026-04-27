"""Tests for core/router/lane_policy.py — routing resolution."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.router.lane_policy import (
    get_category_preference,
    get_fallback_lane,
    get_reviewer,
    get_search_backend,
    get_worker_pool,
    load_lanes,
    reorder_by_preference,
    resolve,
)


# ── load_lanes ──

class TestLoadLanes:
    def test_loads_valid_yaml(self):
        lanes = load_lanes()
        assert "lanes" in lanes
        assert "premium" in lanes["lanes"]
        assert "balanced" in lanes["lanes"]
        assert "cheap" in lanes["lanes"]
        assert "research" in lanes["lanes"]

    def test_lanes_have_required_fields(self):
        lanes = load_lanes()
        for name in ["premium", "balanced", "cheap", "research"]:
            lane = lanes["lanes"][name]
            assert "worker_pool" in lane, f"{name} missing worker_pool"
            assert "category_preference" in lane, f"{name} missing category_preference"


# ── get_worker_pool ──

class TestGetWorkerPool:
    def test_cheap_has_workers(self):
        workers = get_worker_pool("cheap")
        assert len(workers) > 0

    def test_unknown_lane_returns_empty(self):
        workers = get_worker_pool("nonexistent")
        assert workers == []


# ── get_reviewer ──

class TestGetReviewer:
    def test_all_lanes_have_reviewer(self):
        for lane in ["premium", "balanced", "cheap", "research"]:
            reviewer = get_reviewer(lane)
            assert reviewer and len(reviewer) > 0


# ── get_fallback_lane ──

class TestGetFallbackLane:
    def test_cheap_has_fallback(self):
        fallback = get_fallback_lane("cheap")
        assert fallback is not None


# ── get_search_backend ──

class TestGetSearchBackend:
    def test_research_lane_has_search_backend(self):
        search = get_search_backend("research")
        assert search == "argus"


# ── reorder_by_preference ──

class TestReorderByPreference:
    def test_reorders_correctly(self):
        workers = ["b", "c", "a"]
        pref = ["a", "c"]
        result = reorder_by_preference(workers, pref)
        assert result == ["a", "c", "b"]

    def test_preserves_unavailable_workers(self):
        workers = ["x", "y", "z"]
        pref = ["a", "b"]
        result = reorder_by_preference(workers, pref)
        assert result == ["x", "y", "z"]

    def test_empty_preference(self):
        workers = ["a", "b"]
        result = reorder_by_preference(workers, [])
        assert result == ["a", "b"]


# ── resolve ──

class TestResolve:
    def test_implement_small_routes_to_cheap(self):
        r = resolve("implement_small", category="coding")
        assert r["lane"] == "cheap"
        assert r["category"] == "coding"

    def test_research_routes_to_research_lane(self):
        r = resolve("research", category="research")
        assert r["lane"] == "research"
        assert r["search_backend"] == "argus"

    def test_plan_routes_to_premium(self):
        r = resolve("plan")
        assert r["lane"] == "premium"
        assert r["workers"][0] == "claude_code"

    def test_category_inferred_when_not_provided(self):
        r = resolve("implement_small")
        assert r["category"] == "coding"

        r = resolve("review_diff")
        assert r["category"] == "review"

        r = resolve("doc_draft")
        assert r["category"] == "writing"

        r = resolve("research")
        assert r["category"] == "research"

    def test_category_preference_reorders_workers(self):
        r = resolve("implement_small", category="coding")
        assert r["workers"]  # non-empty
        assert "codex" in r["workers"]

    def test_risk_defaults_to_medium(self):
        r = resolve("implement_small")
        assert r["risk"]["level"] == "medium"
        assert r["risk"]["requires_approval"] is True

    def test_risk_level_can_be_set(self):
        r = resolve("implement_small", risk_level="high")
        assert r["risk"]["level"] == "high"
        assert r["risk"]["synchronous_only"] is True

    def test_janitor_routes_to_janitor_lane(self):
        r = resolve("janitor_hygiene")
        assert r["lane"] == "janitor"

    def test_has_reviewer(self):
        r = resolve("implement_small")
        assert "review_with" in r
        assert r["review_with"]

    def test_has_fallback(self):
        r = resolve("implement_small")
        assert "fallback_lane" in r

    def test_all_task_classes_resolve(self):
        from core.task_schema import TaskClass
        for tc in TaskClass:
            r = resolve(tc.value)
            assert r["lane"]
            assert isinstance(r["workers"], list)
