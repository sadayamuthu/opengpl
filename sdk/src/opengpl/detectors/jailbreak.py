# src/opengpl/detectors/jailbreak.py
import re

_JAILBREAK_PATTERNS = [
    r"pretend\s+you\s+(are|have)\s+(no\s+restrictions|DAN|unrestricted)",
    r"you\s+are\s+DAN",
    r"do\s+anything\s+now",
    r"(bypass|ignore|forget)\s+(your\s+)?(safety|restrictions|guidelines|rules)",
    r"act\s+as\s+(if\s+you\s+(have\s+no|are\s+without)|an?\s+unrestricted)",
    r"jailbreak",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _JAILBREAK_PATTERNS]


def detect_jailbreak(text: str) -> bool:
    """Returns True if a jailbreak attempt is detected."""
    return any(p.search(text) for p in _COMPILED)
