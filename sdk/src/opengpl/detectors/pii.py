# src/opengpl/detectors/pii.py
"""PII detection and sanitization.

Two backends:

- **Presidio** (NLP-based, higher recall) — used automatically when the
  optional extra is installed: ``pip install "opengpl-sdk[pii]"`` followed by
  ``python -m spacy download en_core_web_lg``.
- **Regex fallback** (default) — a small, dependency-free pattern set for
  common US-format identifiers (SSN, email, phone, credit card, IPv4). It is
  a heuristic, not a substitute for a dedicated PII service.
"""
import bisect
import re
from typing import NamedTuple

_ANALYZER = None  # lazy init; False means Presidio is unavailable


class PIIResult(NamedTuple):
    entity_type: str
    start: int
    end: int
    score: float


_REGEX_PATTERNS = [
    ("US_SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    # Bounded, and anchored by a lookbehind instead of \b, so a long run of
    # local-part characters with no "@" is scanned once, not once per offset.
    ("EMAIL_ADDRESS", re.compile(
        r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,255}\.[A-Za-z]{2,}\b")),
    ("CREDIT_CARD", re.compile(r"\b(?:\d[ -]?){13,16}\b")),
    ("PHONE_NUMBER", re.compile(r"(?:\+?1[ .-]?)?\(?\b\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}\b")),
    ("IP_ADDRESS", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
]


def _get_analyzer():
    """Return a Presidio AnalyzerEngine, or None if Presidio isn't usable."""
    global _ANALYZER
    if _ANALYZER is None:
        try:
            from presidio_analyzer import AnalyzerEngine

            _ANALYZER = AnalyzerEngine()
        except Exception:  # not installed, or spaCy model missing
            _ANALYZER = False
    return _ANALYZER or None


def backend() -> str:
    """Name of the active PII backend: ``"presidio"`` or ``"regex"``."""
    return "presidio" if _get_analyzer() else "regex"


def _detect_regex(text: str) -> list[PIIResult]:
    found: list[PIIResult] = []
    # Accepted spans never overlap, so keep them sorted and check only the
    # neighbours (a linear scan per match is quadratic on match-dense input).
    starts: list[int] = []
    ends: list[int] = []
    for entity, pattern in _REGEX_PATTERNS:
        for m in pattern.finditer(text):
            s, e = m.span()
            i = bisect.bisect_left(starts, s)
            if (i > 0 and ends[i - 1] > s) or (i < len(starts) and starts[i] < e):
                continue  # an earlier, more specific pattern already matched
            starts.insert(i, s)
            ends.insert(i, e)
            found.append(PIIResult(entity, s, e, 0.5))
    return found


def detect_pii(text: str) -> list[PIIResult]:
    """Returns list of PII entities found in text."""
    analyzer = _get_analyzer()
    if analyzer is None:
        return _detect_regex(text)
    results = analyzer.analyze(text=text, language="en")
    return [PIIResult(r.entity_type, r.start, r.end, r.score) for r in results]


def sanitize_pii(text: str) -> str:
    """Replace PII entities with [REDACTED-<TYPE>] placeholders."""
    results = sorted(detect_pii(text), key=lambda r: r.start, reverse=True)
    pieces: list[str] = []
    last_start = len(text)
    for r in results:
        if r.end > last_start:
            continue  # skip overlapping spans
        pieces.append(text[r.end:last_start])
        pieces.append(f"[REDACTED-{r.entity_type}]")
        last_start = r.start
    pieces.append(text[:last_start])
    return "".join(reversed(pieces))
