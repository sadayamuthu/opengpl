# tests/test_loader.py
import pytest
from opengpl.loader import load, validate_schema
from opengpl.models import EvaluationResult

MINIMAL_POLICY = """
opengpl: '0.1'
policy: test-policy
version: '1.0.0'
description: Test policy
status: ACTIVE
owner: test-team
applies_to:
  models: ['gpt-4o']
  contexts: [test]
audit:
  log_level: SUMMARY
  compliance: []
enforcement:
  engine: opengpl-sdk
  on_violation: BLOCK
  fallback: DENY
"""

def test_load_valid_policy(tmp_path):
    f = tmp_path / "policy.gpl"
    f.write_text(MINIMAL_POLICY)
    policy = load(str(f))
    assert policy["policy"] == "test-policy"
    assert policy["opengpl"] == "0.1"

def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load("/nonexistent/policy.gpl")

def test_load_invalid_schema(tmp_path):
    f = tmp_path / "bad.gpl"
    f.write_text("opengpl: '0.1'\npolicy: bad")  # missing required fields
    with pytest.raises(ValueError, match="schema"):
        load(str(f))
