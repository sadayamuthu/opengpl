from opengpl.compliance.nist import FRAMEWORK_TO_BASELINE, baseline, catalog_ids


def test_catalog_contains_controls_and_enhancements():
    ids = catalog_ids()
    assert {"ac-3", "au-2", "si-10", "ac-6.1"} <= ids
    assert len(ids) > 1000


def test_moderate_baseline_pinned():
    m = baseline("MODERATE")
    assert "v1.6.0" in m.href and m.href.endswith("MODERATE-baseline_profile.json")
    assert len(m.controls) == 287
    assert "au-2" in m.controls and "si-15" not in m.controls


def test_baselines_nest():
    assert baseline("LOW").controls <= baseline("MODERATE").controls <= baseline("HIGH").controls


def test_framework_map():
    assert FRAMEWORK_TO_BASELINE["FedRAMP-High"] == "HIGH"
