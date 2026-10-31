#!/usr/bin/env python3
"""Regenerate src/opengpl/compliance/data/nist_sp800_53r5.json from NIST oscal-content.

Standard library only. Pinned to TAG; change it deliberately and re-run.
"""
import json
import urllib.request
from pathlib import Path

TAG = "v1.6.0"
PREFIX = (
    f"https://raw.githubusercontent.com/usnistgov/oscal-content/{TAG}"
    "/nist.gov/SP800-53/rev5/json/"
)
CATALOG = "NIST_SP-800-53_rev5_catalog.json"
LEVELS = ("LOW", "MODERATE", "HIGH")
OUT = Path(__file__).resolve().parent.parent / "src/opengpl/compliance/data/nist_sp800_53r5.json"


def fetch(name: str) -> dict:
    with urllib.request.urlopen(PREFIX + name, timeout=60) as r:
        return json.load(r)


def collect(controls, out):
    for c in controls:
        out.add(c["id"].lower())
        collect(c.get("controls", []), out)


def main() -> None:
    cat = fetch(CATALOG)["catalog"]
    ids: set[str] = set()
    for g in cat.get("groups", []):
        collect(g.get("controls", []), ids)
    baselines = {}
    for level in LEVELS:
        name = f"NIST_SP-800-53_rev5_{level}-baseline_profile.json"
        prof = fetch(name)["profile"]
        ctrls = {
            i.lower()
            for imp in prof.get("imports", [])
            for inc in imp.get("include-controls", [])
            for i in inc.get("with-ids", [])
        }
        baselines[level] = {"href": PREFIX + name, "controls": sorted(ctrls)}
    data = {
        "source_tag": TAG,
        "catalog_href": PREFIX + CATALOG,
        "catalog_ids": sorted(ids),
        "baselines": baselines,
    }
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"wrote {OUT}: {len(ids)} ids; " + ", ".join(f"{k}={len(v['controls'])}" for k, v in baselines.items()))


if __name__ == "__main__":
    main()
