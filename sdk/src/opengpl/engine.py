# src/opengpl/engine.py
from opengpl import loader
from opengpl.gates.input_gate import InputGate
from opengpl.gates.model_gate import ModelGate
from opengpl.gates.output_gate import OutputGate
from opengpl.models import EvaluationResult


class PolicyEngine:
    """Main entry point for OpenGPL policy enforcement."""

    def __init__(self, policy_path: str):
        self.policy = loader.load(policy_path)
        self._input_gate = InputGate(self.policy)
        self._model_gate = ModelGate(self.policy)
        self._output_gate = OutputGate(self.policy)

    def check_input(self, text: str, context: str | None = None) -> EvaluationResult:
        """Evaluate input text against input_controls."""
        return self._input_gate.evaluate(text, context)

    def check_model(self, context: dict | None = None) -> EvaluationResult:
        """Evaluate model controls."""
        return self._model_gate.evaluate(context)

    def check_output(self, text: str) -> EvaluationResult:
        """Evaluate output text against output_controls."""
        return self._output_gate.evaluate(text)
