# src/opengpl/models.py
from dataclasses import dataclass, field


@dataclass
class EvaluationResult:
    passed: bool
    action: str  # ALLOW, LOG, REDACT, ALERT, BLOCK, ESCALATE, DENY
    reasons: list[str] = field(default_factory=list)
    evaluated: list[str] = field(default_factory=list)
    fired: list[str] = field(default_factory=list)

    @classmethod
    def allow(cls, *, evaluated: list[str] | None = None) -> "EvaluationResult":
        return cls(passed=True, action="ALLOW", evaluated=list(evaluated or []))

    @classmethod
    def block(
        cls,
        reasons: list[str],
        *,
        evaluated: list[str] | None = None,
        fired: list[str] | None = None,
    ) -> "EvaluationResult":
        return cls(
            passed=False,
            action="BLOCK",
            reasons=reasons,
            evaluated=list(evaluated or []),
            fired=list(fired or []),
        )
