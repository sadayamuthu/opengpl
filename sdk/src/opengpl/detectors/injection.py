# src/opengpl/detectors/injection.py
import re

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(your\s+)?(previous\s+)?instructions",
    r"you\s+are\s+now\s+in\s+(developer|jailbreak|dan)\s+mode",
    r"reveal\s+(the\s+)?(system\s+prompt|instructions)",
    r"print\s+(your\s+)?(system\s+prompt|prompt\s+above)",
    r"repeat\s+(the\s+)?(words|text)\s+above",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def detect_injection(text: str) -> bool:
    """Returns True if prompt injection is detected."""
    return any(p.search(text) for p in _COMPILED)
