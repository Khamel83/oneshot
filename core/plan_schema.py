"""OneShot Plan Schema — Machine-readable plans alongside ROADMAP.md."""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from core.task_schema import RiskLevel


class StepAction(str, Enum):
    explore = "explore"
    add_tests = "add_tests"
    implement = "implement"
    refactor = "refactor"
    verify = "verify"
    document = "document"
    configure = "configure"


class VerifyType(str, Enum):
    test = "test"
    lint = "lint"
    typecheck = "typecheck"
    acceptance = "acceptance"
    diff_review = "diff_review"


@dataclass
class PlanStep:
    id: str
    action: StepAction
    description: str
    files: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class VerifyStep:
    verify_type: VerifyType
    command: str
    description: str = ""


@dataclass
class Plan:
    objective: str
    assumptions: list[str] = field(default_factory=list)
    steps: list[PlanStep] = field(default_factory=list)
    verification: list[VerifyStep] = field(default_factory=list)
    rollback: str = ""
    risk_level: RiskLevel = RiskLevel.medium
    notes: str = ""

    def to_dict(self) -> dict:
        """Serialize to dict for JSON output."""
        import dataclasses
        result = dataclasses.asdict(self)
        # Convert enums to strings
        for step in result["steps"]:
            step["action"] = step["action"].value
        for v in result["verification"]:
            v["verify_type"] = v["verify_type"].value
        result["risk_level"] = result["risk_level"].value
        return result

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=indent)
