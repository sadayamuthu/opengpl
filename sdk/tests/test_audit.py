# tests/test_audit.py
import json
from opengpl.audit.ledger import AuditLedger
from opengpl.audit.oscal import generate_oscal_stub
from opengpl.models import EvaluationResult


def test_ledger_records_event():
    ledger = AuditLedger()
    result = EvaluationResult(passed=True, action="ALLOW")
    ledger.record(event_type="input_check", result=result, policy_name="test")
    assert len(ledger.events) == 1
    assert ledger.events[0]["action"] == "ALLOW"

def test_ledger_export_json():
    ledger = AuditLedger()
    ledger.record("input_check", EvaluationResult(passed=False, action="BLOCK", reasons=["injection"]), "test")
    exported = json.loads(ledger.to_json())
    assert exported[0]["passed"] is False

def test_oscal_stub_structure():
    stub = generate_oscal_stub(policy_name="test-policy", framework="FedRAMP-Moderate")
    assert stub["oscal-version"] == "1.0.4"
    assert stub["metadata"]["title"] == "test-policy"
    assert "NOTE" in stub["metadata"]
