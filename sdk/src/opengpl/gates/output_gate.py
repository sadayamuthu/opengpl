# src/opengpl/gates/output_gate.py
import re
from opengpl.models import EvaluationResult

# Simple keyword patterns for blocked data types
_BLOCK_PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "PHI": r"\b(diagnosis|prescription|medical record|patient)\b",
    "credit_card": r"\b(?:\d{4}[\s-]?){3}\d{4}\b",
    "credentials": r"\b(api[_\s]?key|password|secret|token)\s*[:=]\s*\S+",
}


class OutputGate:
    def __init__(self, policy: dict):
        self._controls = policy.get("output_controls", {})
        self._on_violation = policy.get("enforcement", {}).get("on_violation", "BLOCK")

    def evaluate(self, text: str) -> EvaluationResult:
        blocked_types = self._controls.get("block", [])
        reasons = []

        for dtype in blocked_types:
            pattern = _BLOCK_PATTERNS.get(dtype)
            if pattern and re.search(pattern, text, re.IGNORECASE):
                reasons.append(f"blocked data type detected: {dtype}")

        if reasons:
            return EvaluationResult.block(reasons)
        return EvaluationResult.allow()
