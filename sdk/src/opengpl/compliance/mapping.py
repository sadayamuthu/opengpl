"""Policy-field to control mapping. A control is reported only if a policy field implements it."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from typing import Any

import yaml

from opengpl.compliance.status import Status, value_status, weakest

FRAMEWORK_FILES: dict[str, str] = {
    "FedRAMP-Low": "sp800-53r5.yaml",
    "FedRAMP-Moderate": "sp800-53r5.yaml",
    "FedRAMP-High": "sp800-53r5.yaml",
}


class UnknownFramework(ValueError):
    pass


@dataclass(frozen=True)
class MappingEntry:
    framework: str
    control: str
    field: str
    when: dict
    statement: str
    rationale: str


@dataclass(frozen=True)
class AppliedControl:
    control: str
    status: Status
    fields: tuple[str, ...]
    evidence: tuple[str, ...]
    statements: tuple[str, ...]


def _norm_when(when: dict) -> dict:
    # YAML 1.1 reads an unquoted `true:`/`false:` key as a boolean; accept both spellings.
    return {("true" if k is True else "false" if k is False else k): v for k, v in when.items()}


@lru_cache(maxsize=None)
def _load(filename: str) -> tuple[MappingEntry, ...]:
    text = (files("opengpl.compliance") / "mappings" / filename).read_text(encoding="utf-8")
    doc = yaml.safe_load(text)
    return tuple(
        MappingEntry(
            framework=doc["framework"],
            control=e["control"],
            field=e["field"],
            when=_norm_when(e["when"]),
            statement=e["statement"],
            rationale=e["rationale"],
        )
        for e in doc["entries"]
    )


def load_mappings(framework: str) -> list[MappingEntry]:
    try:
        filename = FRAMEWORK_FILES[framework]
    except KeyError:
        raise UnknownFramework(framework) from None
    return list(_load(filename))


def get_field(policy: dict, dotted: str) -> Any:
    cur: Any = policy
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _fmt(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ", ".join(_fmt(v) for v in value)
    return str(value)


def _evaluate(entry: MappingEntry, value: Any) -> tuple[Status, str] | None:
    """Return (status, rendered value) if the condition holds, else None."""
    if value is None:
        return None
    (op, arg), = entry.when.items()
    f = entry.field
    if op == "present":
        if value == [] or value == "" or value == {}:
            return None
        if isinstance(value, list):
            return weakest(value_status(f, str(v)) for v in value), _fmt(value)
        return value_status(f, _fmt(value)), _fmt(value)
    if op in ("true", "false"):
        if value is not (op == "true"):
            return None
        return value_status(f), _fmt(value)
    if op == "equals":
        if value != arg:
            return None
        return value_status(f, _fmt(value)), _fmt(value)
    if op == "in":
        if isinstance(value, (list, dict)) or value not in arg:
            return None
        return value_status(f, _fmt(value)), _fmt(value)
    if op == "any_of":
        if not isinstance(value, list):
            return None
        hits = [v for v in value if v in arg]
        if not hits:
            return None
        return weakest(value_status(f, v) for v in hits), _fmt(hits)
    raise ValueError(f"unknown condition op: {op}")


def _evidence(field: str, rendered: str) -> list[str]:
    return [f"{field}={item}" for item in rendered.split(", ")]


def _sort_key(control: str) -> tuple[str, tuple[int, ...]]:
    family, _, num = control.partition("-")
    return family, tuple(int(x) for x in num.split("."))


def applicable_controls(policy: dict, framework: str) -> list[AppliedControl]:
    grouped: dict[str, list[tuple[Status, MappingEntry, str]]] = {}
    for entry in load_mappings(framework):
        res = _evaluate(entry, get_field(policy, entry.field))
        if res is not None:
            grouped.setdefault(entry.control, []).append((res[0], entry, res[1]))
    out = []
    for control in sorted(grouped, key=_sort_key):
        hits = grouped[control]
        out.append(
            AppliedControl(
                control=control,
                status=weakest(s for s, _, _ in hits),
                fields=tuple(e.field for _, e, _ in hits),
                evidence=tuple(ev for _, e, v in hits for ev in _evidence(e.field, v)),
                statements=tuple(e.statement.replace("{value}", v) for _, e, v in hits),
            )
        )
    return out
