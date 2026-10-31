# src/opengpl/engine.py
import os

from opengpl import loader
from opengpl.audit.ledger import DecisionLog
from opengpl.gates.input_gate import InputGate
from opengpl.gates.model_gate import ModelGate
from opengpl.gates.output_gate import OutputGate
from opengpl.models import EvaluationResult


class PolicyEngine:
    """Main entry point for OpenGPL policy enforcement."""

    def __init__(
        self, policy_path: str, decision_log: str | os.PathLike | DecisionLog | None = None
    ):
        self.policy = loader.load(policy_path)
        self._input_gate = InputGate(self.policy)
        self._model_gate = ModelGate(self.policy)
        self._output_gate = OutputGate(self.policy)
        self.decisions = (
            decision_log if isinstance(decision_log, DecisionLog) else DecisionLog(decision_log)
        )

    def check_input(self, text: str, context: str | None = None) -> EvaluationResult:
        """Evaluate input text against input_controls."""
        result = self._input_gate.evaluate(text, context)
        self.decisions.record(policy=self.policy, gate="input", result=result, text=text)
        return result

    def check_model(self, context: dict | None = None) -> EvaluationResult:
        """Evaluate model controls."""
        result = self._model_gate.evaluate(context)
        self.decisions.record(policy=self.policy, gate="model", result=result, text=None)
        return result

    def check_output(self, text: str) -> EvaluationResult:
        """Evaluate output text against output_controls."""
        result = self._output_gate.evaluate(text)
        self.decisions.record(policy=self.policy, gate="output", result=result, text=text)
        return result
