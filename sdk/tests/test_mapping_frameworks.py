import importlib.resources as r
import json
import re

import pytest

from opengpl.compliance.mapping import FRAMEWORK_FILES, applicable_controls, load_mappings

NEW = ("NIST-AI-RMF", "EU-AI-Act", "HIPAA", "SOC2")


def test_ai_rmf_ids_are_real_subcategories():
    valid = set(json.loads((r.files("opengpl.compliance") / "data" / "nist_ai_rmf_subcategories.json").read_text()))
    assert {e.control for e in load_mappings("NIST-AI-RMF")} <= valid
    assert "GOVERN 1.1" in valid


def test_ai_rmf_subcategory_list_shape():
    valid = json.loads((r.files("opengpl.compliance") / "data" / "nist_ai_rmf_subcategories.json").read_text())
    assert len(valid) == len(set(valid)) == 72  # NIST AI 100-1 Tables 1-4: 19 + 18 + 22 + 13
    assert all(re.fullmatch(r"(GOVERN|MAP|MEASURE|MANAGE) \d\.\d{1,2}", s) for s in valid)


def test_eu_ai_act_ids_are_articles_9_to_15():
    for e in load_mappings("EU-AI-Act"):
        m = re.fullmatch(r"art-(\d+)(\.\d+)?", e.control)
        assert m and 9 <= int(m.group(1)) <= 15
    assert not any(e.control.startswith(("art-10", "art-11")) for e in load_mappings("EU-AI-Act"))


def test_hipaa_and_soc2_id_formats():
    assert all(re.fullmatch(r"164\.3\d\d\([a-z]\)(\(\d+\))?", e.control) for e in load_mappings("HIPAA"))
    assert all(re.fullmatch(r"CC\d\.\d", e.control) for e in load_mappings("SOC2"))


@pytest.mark.parametrize("fw", NEW)
def test_new_frameworks_registered_and_nonempty(fw):
    assert fw in FRAMEWORK_FILES
    assert load_mappings(fw)


@pytest.mark.parametrize("fw", NEW)
def test_applicable_controls_runs_and_is_field_gated(fw):
    full = {
        "input_controls": {"detect": ["prompt_injection", "jailbreak"], "require_user_auth": True},
        "model_controls": {"allow_external_calls": False, "require_human_in_loop": ["x"],
                           "allow_tools": ["search"], "deny_tools": ["shell"]},
        "output_controls": {"block": ["PHI", "SSN"], "hallucination_threshold": 0.1,
                            "require": ["disclaimer"]},
        "audit": {"log_level": "FULL", "alert_on_violation": True, "retention_days": 365},
    }
    got = applicable_controls(full, fw)
    assert got
    assert applicable_controls({}, fw) == []
    # Every applied control comes from a mapping entry whose field is set.
    fields = {e.field for e in load_mappings(fw)}
    assert all(set(c.fields) <= fields for c in got)


def test_sort_key_orders_all_id_shapes_naturally():
    from opengpl.compliance.mapping import _sort_key
    assert sorted(["ac-11", "ac-3"], key=_sort_key) == ["ac-3", "ac-11"]
    assert sorted(["MEASURE 2.13", "MEASURE 2.4"], key=_sort_key) == ["MEASURE 2.4", "MEASURE 2.13"]
    assert sorted(["art-15.5", "art-12.1", "art-15"], key=_sort_key) == ["art-12.1", "art-15", "art-15.5"]
    assert sorted(["164.312(d)", "164.312(a)(1)", "164.312(b)"], key=_sort_key) == ["164.312(a)(1)", "164.312(b)", "164.312(d)"]
    assert sorted(["CC7.2", "CC6.7", "CC6.1"], key=_sort_key) == ["CC6.1", "CC6.7", "CC7.2"]
