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
        evaluated = []
        fired = []

        for name, detect, reason in (
            ("prompt_injection", injection.detect_injection, "prompt_injection detected"),
            ("jailbreak", jailbreak.detect_jailbreak, "jailbreak attempt detected"),
        ):
            if name not in detections:
                continue
            rule_id = f"input_controls.detect:{name}"
            evaluated.append(rule_id)
            if detect(text):
                fired.append(rule_id)
                reasons.append(reason)

        if reasons:
            return EvaluationResult.block(reasons, evaluated=evaluated, fired=fired)
        return EvaluationResult.allow(evaluated=evaluated)
