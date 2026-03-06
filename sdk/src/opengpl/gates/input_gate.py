# src/opengpl/gates/input_gate.py
from opengpl.models import EvaluationResult
from opengpl.detectors import injection, jailbreak, pii


class InputGate:
    def __init__(self, policy: dict):
        self._controls = policy.get("input_controls", {})
        self._on_violation = policy.get("enforcement", {}).get("on_violation", "BLOCK")

    def evaluate(self, text: str, context: str | None = None) -> EvaluationResult:
        detections = self._controls.get("detect", [])
        reasons = []

        if "prompt_injection" in detections and injection.detect_injection(text):
            reasons.append("prompt_injection detected")

        if "jailbreak" in detections and jailbreak.detect_jailbreak(text):
            reasons.append("jailbreak attempt detected")

        if reasons:
            return EvaluationResult.block(reasons)
        return EvaluationResult.allow()
