# tests/test_audit.py
from opengpl.audit.ledger import DecisionLog, read_decisions
from opengpl.models import EvaluationResult


def test_decision_log_records_event():
    log = DecisionLog()
    rec = log.record(policy={"policy": "test", "version": "1"}, gate="input",
                     result=EvaluationResult(passed=True, action="ALLOW"), text=None)
    assert log.records == [rec]
    assert rec["action"] == "ALLOW"

def test_decision_log_roundtrip(tmp_path):
    log = DecisionLog(tmp_path / "d.jsonl")
    log.record(policy={"policy": "test", "version": "1"}, gate="output",
               result=EvaluationResult(passed=False, action="BLOCK", reasons=["injection"]), text="x")
    recs = read_decisions(tmp_path / "d.jsonl")
    assert recs[0]["passed"] is False and recs[0]["reasons"] == ["injection"]
