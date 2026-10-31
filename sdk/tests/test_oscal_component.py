import json, pathlib, pytest, yaml
from datetime import datetime, timezone
from opengpl.audit.oscal import component_definition, UnsupportedFramework, FrameworkNotDeclared
from tests.oscal_schema import validate

EX = pathlib.Path(__file__).parents[2] / "spec" / "examples"
NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)
fedramp = yaml.safe_load((EX / "fedramp-moderate.gpl").read_text())

def irs(doc):
    return {i["control-id"]: i for i in doc["component-definition"]["components"][0]["control-implementations"][0]["implemented-requirements"]}

def prop(ir, name):
    return [p["value"] for p in ir.get("props", []) if p["name"] == name]

def test_fedramp_example_is_schema_valid():
    doc, omitted = component_definition(fedramp, "FedRAMP-Moderate", now=NOW)
    assert validate(doc, "component") == []
    assert "si-15" in omitted

def test_status_and_evidence_props():
    doc, _ = component_definition(fedramp, "FedRAMP-Moderate", now=NOW)
    assert prop(irs(doc)["si-10"], "implementation-status") == ["declared"]
    assert prop(irs(doc)["au-2"], "policy-field") == ["audit.log_level=FULL"]

def test_deterministic():
    a, _ = component_definition(fedramp, "FedRAMP-Moderate", now=NOW)
    b, _ = component_definition(fedramp, "FedRAMP-Moderate", now=NOW)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)

def test_no_mapped_controls_still_valid():
    p = {"policy": "bare-agent", "version": "1.0.0", "description": "d", "audit": {"log_level": "SUMMARY", "compliance": ["FedRAMP-Moderate"]}}
    doc, _ = component_definition(p, "FedRAMP-Moderate", now=NOW)
    assert validate(doc, "component") == []
    assert "control-implementations" not in doc["component-definition"]["components"][0]

def test_framework_errors():
    with pytest.raises(UnsupportedFramework):
        component_definition(fedramp, "NIST-AI-RMF", now=NOW)
    with pytest.raises(FrameworkNotDeclared):
        component_definition(fedramp, "FedRAMP-High", now=NOW)

def test_no_assessment_language():
    doc, _ = component_definition(fedramp, "FedRAMP-Moderate", now=NOW)
    text = json.dumps(doc).lower()
    assert "satisfied" not in text and "compliant" not in text and "controlgate" not in text
