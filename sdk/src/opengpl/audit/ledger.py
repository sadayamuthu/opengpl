# src/opengpl/audit/ledger.py
"""JSONL decision log: one record per gate decision."""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from typing import Literal

from opengpl.detectors.pii import sanitize_pii
from opengpl.gates.output_gate import _BLOCK_PATTERNS
from opengpl.models import EvaluationResult

DECISION_SCHEMA = "opengpl.decision/1"

# Applied after sanitize_pii so redaction does not depend on the PII backend
# (Presidio treats well-known test numbers such as 123-45-6789 as fake).
_REDACTIONS = (
    ("SSN", "[REDACTED-US_SSN]"),
    ("credit_card", "[REDACTED-CREDIT_CARD]"),
    ("credentials", "[REDACTED-CREDENTIAL]"),
)


# Log-only credential shapes the gate regex misses (JSON keys, *_token, Bearer).
_LOG_CREDENTIAL_PATTERNS = (
    r"(?i)\b\w*(?:api[_\s-]?key|password|passwd|secret|token)\w*\"?\s*[:=]\s*\"?[^\s\",}]+",
    r"(?i)\bbearer\s+[^\s\",}]+",
)


def redact_for_log(text: str) -> str:
    text = sanitize_pii(text)
    for key, token in _REDACTIONS:
        text = re.sub(_BLOCK_PATTERNS[key], token, text, flags=re.IGNORECASE)
    for pat in _LOG_CREDENTIAL_PATTERNS:
        text = re.sub(pat, "[REDACTED-CREDENTIAL]", text)
    return text


def _now() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    dt = datetime.fromtimestamp(int(epoch), timezone.utc) if epoch else datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class DecisionLog:
    """Append-only decision log.

    `records` is a recent-window convenience (last `max_records`); the JSONL
    file is the record of truth.
    """

    def __init__(self, path: str | os.PathLike | None = None, *, max_records: int | None = 10_000):
        self.max_records = max_records
        self.records: list[dict] = []
        self._lock = threading.Lock()
        self._fh = open(path, "a", encoding="utf-8") if path is not None else None

    def record(
        self,
        *,
        policy: dict,
        gate: Literal["input", "output", "model"],
        result: EvaluationResult,
        text: str | None,
    ) -> dict:
        audit = policy.get("audit") or {}
        rec = {
            "schema": DECISION_SCHEMA,
            "id": str(uuid.uuid4()),
            "timestamp": _now(),
            "policy": policy.get("policy"),
            "policy_version": policy.get("version"),
            "gate": gate,
            "passed": result.passed,
            "action": result.action,
            "reasons": list(result.reasons),
            "evaluated": list(result.evaluated),
            "fired": list(result.fired),
            "text_sha256": None if text is None else hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
        if text is not None and audit.get("log_level") in ("FULL", "DEBUG"):
            rec["text"] = text if audit.get("pii_in_logs") is True else redact_for_log(text)
        with self._lock:
            self.records.append(rec)
            if self.max_records is not None and len(self.records) > self.max_records:
                del self.records[:len(self.records) - self.max_records]
            if self._fh is not None:
                self._fh.write(json.dumps(rec) + "\n")
                self._fh.flush()
        return rec


def read_decisions(path: str | os.PathLike) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                raise ValueError(f"{path}:{lineno}: invalid JSON") from None
            if not isinstance(rec, dict) or rec.get("schema") != DECISION_SCHEMA:
                raise ValueError(f"{path}:{lineno}: not an opengpl decision record")
            out.append(rec)
    return out
