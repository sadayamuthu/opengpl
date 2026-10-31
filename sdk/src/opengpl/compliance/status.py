# src/opengpl/compliance/status.py
"""What the SDK really enforces: enforced, heuristic or declared."""
from collections.abc import Iterable
from enum import Enum

from opengpl.gates.output_gate import _BLOCK_PATTERNS


class Status(str, Enum):
    DECLARED = "declared"
    HEURISTIC = "heuristic"
    ENFORCED = "enforced"


_ORDER = {Status.DECLARED: 0, Status.HEURISTIC: 1, Status.ENFORCED: 2}

_REGISTRY: dict[tuple[str, str | None], Status] = {
    ("input_controls.detect", "prompt_injection"): Status.HEURISTIC,
    ("input_controls.detect", "jailbreak"): Status.HEURISTIC,
    ("audit.pii_in_logs", None): Status.HEURISTIC,
    ("audit.log_level", None): Status.ENFORCED,
    ("audit.format", "OSCAL"): Status.ENFORCED,
}
for _key in _BLOCK_PATTERNS:
    _REGISTRY[("output_controls.block", _key)] = Status.HEURISTIC


def weakest(statuses: Iterable[Status]) -> Status:
    """Return the weakest status; an empty input is DECLARED."""
    return min(statuses, key=_ORDER.__getitem__, default=Status.DECLARED)


def value_status(field: str, value: str | None = None) -> Status:
    """Look up (field, value), then (field, None), then DECLARED."""
    return _REGISTRY.get((field, value)) or _REGISTRY.get((field, None), Status.DECLARED)
