"""Pinned NIST SP 800-53 Rev 5 reference data (usnistgov/oscal-content v1.6.0)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from typing import Literal

FRAMEWORK_TO_BASELINE: dict[str, str] = {
    "FedRAMP-Low": "LOW",
    "FedRAMP-Moderate": "MODERATE",
    "FedRAMP-High": "HIGH",
}


@dataclass(frozen=True)
class Baseline:
    level: str
    href: str
    controls: frozenset[str]


@lru_cache(maxsize=1)
def _data() -> dict:
    text = (files("opengpl.compliance") / "data" / "nist_sp800_53r5.json").read_text(
        encoding="utf-8"
    )
    return json.loads(text)


def catalog_ids() -> frozenset[str]:
    return frozenset(_data()["catalog_ids"])


def baseline(level: Literal["LOW", "MODERATE", "HIGH"]) -> Baseline:
    b = _data()["baselines"][level]
    return Baseline(level=level, href=b["href"], controls=frozenset(b["controls"]))
