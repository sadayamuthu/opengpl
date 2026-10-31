#!/usr/bin/env python3
"""Regenerate the mapping tables in spec/docs/compliance-mapping.md from the SDK mapping data.

Each table lives between `<!-- BEGIN GENERATED:<framework> -->` and
`<!-- END GENERATED:<framework> -->`, where <framework> is an `audit.compliance`
value known to `opengpl.compliance.mapping.FRAMEWORK_FILES`.

Usage: python spec/scripts/gen_compliance_mapping.py [--check]
With --check, nothing is written and the exit code is 1 if the doc is out of date.
"""

from __future__ import annotations

import pathlib
import re
import sys

from opengpl.compliance.mapping import FRAMEWORK_FILES, MappingEntry, load_mappings
from opengpl.compliance.status import Status, stronger, value_status, value_statuses, weakest

DOC = pathlib.Path(__file__).resolve().parents[1] / "docs" / "compliance-mapping.md"

_BLOCK = re.compile(
    r"(<!-- BEGIN GENERATED:(?P<fw>[A-Za-z0-9-]+) -->\n)(?P<body>.*?)(<!-- END GENERATED:(?P=fw) -->)",
    re.S,
)

# Frameworks whose tables the doc must carry as generated blocks.
REQUIRED = ("NIST-AI-RMF", "FedRAMP-Moderate", "HIPAA", "EU-AI-Act", "SOC2")

HEADER = (
    "| Control | Policy field | Condition | Reference SDK status | Rationale |\n"
    "|---|---|---|---|---|\n"
)


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _condition(entry: MappingEntry) -> str:
    ((op, arg),) = entry.when.items()
    if op == "present":
        return "set"
    if op in ("true", "false"):
        return f"`{op}`"
    if op == "equals":
        return f"`{arg}`"
    if op == "in":
        return "one of " + ", ".join(f"`{v}`" for v in arg)
    if op == "any_of":
        return "includes any of " + ", ".join(f"`{v}`" for v in arg)
    raise ValueError(f"unknown condition op: {op}")


def _status(entry: MappingEntry) -> str:
    """Weakest status the row can carry, then any stronger statuses and the values that earn them."""
    ((op, arg),) = entry.when.items()
    f = entry.field
    if op == "equals":
        return value_status(f, str(arg)).value
    if op in ("in", "any_of"):
        candidates = {str(v): value_status(f, str(v)) for v in arg}
        base = weakest(candidates.values())
    else:
        base = value_status(f)
        candidates = value_statuses(f)
    parts = [base.value]
    for level in (Status.HEURISTIC, Status.ENFORCED):
        vals = [v for v, st in candidates.items() if st is level and stronger(st, base)]
        if vals:
            parts.append(f"{level.value} for " + ", ".join(f"`{v}`" for v in vals))
    return "; ".join(parts)


def render_table(framework: str) -> str:
    source = FRAMEWORK_FILES[framework]
    rows = [
        f"| `{e.control}` | `{e.field}` | {_condition(e)} | {_status(e)} | {_cell(e.rationale)} |\n"
        for e in load_mappings(framework)
    ]
    note = (
        f"<!-- Generated from sdk/src/opengpl/compliance/mappings/{source} "
        "by spec/scripts/gen_compliance_mapping.py. Do not edit by hand. -->\n"
    )
    return note + HEADER + "".join(rows)


def render_tables(doc_text: str) -> str:
    """Return doc_text with every generated block replaced by the current mapping table."""

    def sub(m: re.Match) -> str:
        fw = m.group("fw")
        if fw not in FRAMEWORK_FILES:
            raise ValueError(f"unknown framework in generated block: {fw}")
        return m.group(1) + render_table(fw) + m.group(4)

    return _BLOCK.sub(sub, doc_text)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    current = DOC.read_text(encoding="utf-8")
    found = {m.group("fw") for m in _BLOCK.finditer(current)}
    missing = [fw for fw in REQUIRED if fw not in found]
    if missing:
        print(f"{DOC} has no generated block for: {', '.join(missing)}", file=sys.stderr)
        return 1
    updated = render_tables(current)
    if check:
        if updated != current:
            print(
                f"{DOC} is out of date; run spec/scripts/gen_compliance_mapping.py", file=sys.stderr
            )
            return 1
        return 0
    if updated != current:
        DOC.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
