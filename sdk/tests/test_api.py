# tests/test_api.py
from fastapi.testclient import TestClient
from opengpl.api import app

client = TestClient(app)

VALID_POLICY = """
opengpl: '0.1'
policy: test-api-policy
version: '1.0.0'
description: Test policy for API validation
status: ACTIVE
owner: test
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

INVALID_POLICY = "opengpl: '0.1'\npolicy: bad"  # missing required fields


def test_validate_valid_policy():
    response = client.post("/validate", json={"policy": VALID_POLICY, "version": "0.1"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["errors"] == []

def test_validate_invalid_policy():
    response = client.post("/validate", json={"policy": INVALID_POLICY, "version": "0.1"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert len(data["errors"]) > 0

def test_schema_versions():
    response = client.get("/schema-versions")
    assert response.status_code == 200
    assert "0.1" in response.json()["versions"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
