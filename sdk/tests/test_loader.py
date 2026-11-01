# tests/test_loader.py
import pytest

from opengpl.loader import _get_schema, load

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


_TWO = (
    MINIMAL_POLICY.replace("policy: test-policy", "policy: alpha")
    + "---\n"
    + MINIMAL_POLICY.replace("policy: test-policy", "policy: beta")
)


def test_load_all_multi_document(tmp_path):
    from opengpl.loader import load_all

    f = tmp_path / "multi.gpl"
    f.write_text(_TWO)
    assert [d["policy"] for d in load_all(str(f))] == ["alpha", "beta"]


def test_load_rejects_multi_document_with_clear_error(tmp_path):
    f = tmp_path / "multi.gpl"
    f.write_text(_TWO)
    with pytest.raises(ValueError, match="contains 2 policies"):
        load(str(f))


def test_load_invalid_yaml_is_value_error(tmp_path):
    f = tmp_path / "bad.gpl"
    f.write_text("opengpl: '0.1'\n  bad: [indent")
    with pytest.raises(ValueError, match="Invalid YAML"):
        load(str(f))


def test_schema_version_rejects_path_traversal():
    with pytest.raises(ValueError, match="Invalid OpenGPL schema version"):
        _get_schema("../../etc/passwd")
