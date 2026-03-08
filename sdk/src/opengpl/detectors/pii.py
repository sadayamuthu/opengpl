# src/opengpl/detectors/pii.py
from typing import NamedTuple
from presidio_analyzer import AnalyzerEngine

_ANALYZER = None  # lazy init


def _get_analyzer() -> AnalyzerEngine:
    global _ANALYZER
    if _ANALYZER is None:
        _ANALYZER = AnalyzerEngine()
    return _ANALYZER


class PIIResult(NamedTuple):
    entity_type: str
    start: int
    end: int
    score: float


def detect_pii(text: str) -> list[PIIResult]:
    """Returns list of PII entities found in text."""
    results = _get_analyzer().analyze(text=text, language="en")
    return [PIIResult(r.entity_type, r.start, r.end, r.score) for r in results]


def sanitize_pii(text: str) -> str:
    """Replace PII entities with [REDACTED-<TYPE>] placeholders."""
    results = sorted(detect_pii(text), key=lambda r: r.start, reverse=True)
    for r in results:
        text = text[:r.start] + f"[REDACTED-{r.entity_type}]" + text[r.end:]
    return text
