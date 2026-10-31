"""Validate OSCAL documents against the vendored OSCAL 1.2.3 JSON schemas."""
from __future__ import annotations

import json
import pathlib
from functools import lru_cache
from typing import Literal

from jsonschema import Draft7Validator

_DIR = pathlib.Path(__file__).parent / "data" / "oscal" / "v1.2.3"
_FILES = {
    "component": "oscal_component_schema.json",
    "assessment-results": "oscal_assessment-results_schema.json",
}


@lru_cache(maxsize=None)
def _validator(model: str) -> Draft7Validator:
    text = (_DIR / _FILES[model]).read_text(encoding="utf-8")
    # Python's `re` cannot compile \p{..}; substitute equivalents.
    text = text.replace("\\\\p{L}", "[^\\\\W\\\\d_]").replace("\\\\p{N}", "\\\\d")
    return Draft7Validator(json.loads(text))


def validate(doc: dict, model: Literal["component", "assessment-results"]) -> list[str]:
    errs = sorted(_validator(model).iter_errors(doc), key=lambda e: list(e.absolute_path))
    return [f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errs]
