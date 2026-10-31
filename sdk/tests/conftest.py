import pytest

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
input_controls:
  detect: [prompt_injection]
output_controls:
  block: [SSN]
audit:
  log_level: SUMMARY
  compliance: []
enforcement:
  engine: opengpl-sdk
  on_violation: BLOCK
  fallback: DENY
"""


@pytest.fixture
def engine_policy_file(tmp_path):
    f = tmp_path / "policy.gpl"
    f.write_text(MINIMAL_POLICY)
    return str(f)
