# src/opengpl/models.py
from dataclasses import dataclass, field


@dataclass
class EvaluationResult:
    passed: bool
    action: str  # ALLOW, LOG, REDACT, ALERT, BLOCK, ESCALATE, DENY
    reasons: list[str] = field(default_factory=list)

    @classmethod
    def allow(cls) -> "EvaluationResult":
        return cls(passed=True, action="ALLOW")

    @classmethod
    def block(cls, reasons: list[str]) -> "EvaluationResult":
        return cls(passed=False, action="BLOCK", reasons=reasons)
