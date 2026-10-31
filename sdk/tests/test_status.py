from opengpl.compliance.status import Status, weakest, value_status
from opengpl.gates.output_gate import _BLOCK_PATTERNS


def test_weakest_orders_declared_lowest():
    assert weakest([Status.ENFORCED, Status.HEURISTIC]) is Status.HEURISTIC
    assert weakest([Status.ENFORCED, Status.DECLARED]) is Status.DECLARED
    assert weakest([]) is Status.DECLARED


def test_detectors_are_heuristic_and_unknown_values_declared():
    assert value_status("input_controls.detect", "prompt_injection") is Status.HEURISTIC
    assert value_status("input_controls.detect", "jailbreak") is Status.HEURISTIC
    assert value_status("input_controls.detect", "context_stuffing") is Status.DECLARED
    assert value_status("model_controls.allow_tools") is Status.DECLARED
    assert value_status("audit.log_level") is Status.ENFORCED
    assert value_status("audit.pii_in_logs") is Status.HEURISTIC


def test_output_block_registry_matches_gate_patterns():
    for key in _BLOCK_PATTERNS:
        assert value_status("output_controls.block", key) is Status.HEURISTIC
    assert value_status("output_controls.block", "financial") is Status.DECLARED
