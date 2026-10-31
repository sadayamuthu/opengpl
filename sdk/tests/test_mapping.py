import pathlib

import pytest
import yaml

from opengpl.compliance.mapping import (
    FRAMEWORK_FILES,
    UnknownFramework,
    applicable_controls,
    get_field,
    load_mappings,
)
from opengpl.compliance.nist import catalog_ids
from opengpl.compliance.status import Status

EX = pathlib.Path(__file__).parents[2] / "spec" / "examples"
fedramp = yaml.safe_load((EX / "fedramp-moderate.gpl").read_text())


def ids(policy, fw="FedRAMP-Moderate"):
    return {c.control: c for c in applicable_controls(policy, fw)}


def test_every_mapped_control_exists_in_catalog():
    assert {e.control for e in load_mappings("FedRAMP-Moderate")} <= catalog_ids()


def test_control_appears_only_when_its_field_is_set():
    p = {"audit": {"log_level": "SUMMARY"}}
    assert "ac-3" not in ids(p) and "au-2" not in ids(p)
    p = {"audit": {"log_level": "FULL"}, "model_controls": {"allow_tools": ["search"]}}
    assert {"ac-3", "au-2"} <= ids(p).keys()


def test_status_is_weakest_contributing_value():
    assert ids(fedramp)["si-10"].status is Status.DECLARED  # context_stuffing has no detector
    p = {"input_controls": {"detect": ["prompt_injection", "jailbreak"]}}
    assert ids(p)["si-10"].status is Status.HEURISTIC


def test_evidence_names_field_and_value():
    assert ids(fedramp)["au-2"].evidence == ("audit.log_level=FULL",)
    assert ids(fedramp)["au-2"].status is Status.ENFORCED


def test_unknown_framework():
    with pytest.raises(UnknownFramework):
        load_mappings("PCI-DSS")


def test_sorted_numerically():
    ctl = [c.control for c in applicable_controls(fedramp, "FedRAMP-Moderate")]
    assert ctl == sorted(ctl, key=lambda c: (c.split("-")[0], [int(x) for x in c.split("-")[1].split(".")]))
    assert ctl.index("au-3") < ctl.index("au-11")


def test_framework_files_and_get_field():
    assert set(FRAMEWORK_FILES) == {"FedRAMP-Low", "FedRAMP-Moderate", "FedRAMP-High"}
    assert get_field({"a": {"b": 1}}, "a.b") == 1
    assert get_field({"a": {}}, "a.b") is None
    assert get_field({"a": 3}, "a.b") is None


def test_merged_control_collects_fields_and_weakest_status():
    p = {"model_controls": {"allow_tools": ["x"], "deny_tools": ["y"]}}
    c = ids(p)["ac-3"]
    assert c.fields == ("model_controls.allow_tools", "model_controls.deny_tools")
    assert c.status is Status.DECLARED
    assert len(c.statements) == 2


def test_scalar_and_boolean_conditions():
    assert "sc-7" in ids({"model_controls": {"allow_external_calls": False}})
    assert "sc-7" not in ids({"model_controls": {"allow_external_calls": True}})
    assert "au-2" not in ids({"audit": {}})


def test_unset_or_empty_list_is_absent():
    assert "ac-3" not in ids({"model_controls": {"allow_tools": []}})


def test_au9_not_mapped():
    assert "au-9" not in {e.control for e in load_mappings("FedRAMP-High")}


def test_every_entry_has_rationale():
    for e in load_mappings("FedRAMP-Low"):
        assert e.rationale and e.statement


def test_list_evidence_is_one_item_per_value():
    p = {"input_controls": {"detect": ["jailbreak", "toxicity"]}}
    assert ids(p)["si-10"].evidence == ("input_controls.detect=jailbreak",)
