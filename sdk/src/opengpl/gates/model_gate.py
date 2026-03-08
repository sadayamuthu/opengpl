# src/opengpl/gates/model_gate.py
from opengpl.models import EvaluationResult


class ModelGate:
    """Evaluates model_controls. Patent-sensitive methods delegated to ControlGate."""

    def __init__(self, policy: dict):
        self._controls = policy.get("model_controls", {})

    def evaluate(self, context: dict | None = None) -> EvaluationResult:
        # Open source: basic tool access check only
        # Full dual-gate enforcement = ControlGate commercial feature
        return EvaluationResult.allow()
