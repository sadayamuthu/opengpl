# src/opengpl/audit/ledger.py
"""JSONL decision log: one record per gate decision."""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import uuid
from datetime import UTC, datetime
from typing import Literal

from opengpl.detectors.pii import sanitize_pii
from opengpl.gates.output_gate import _BLOCK_PATTERNS
from opengpl.models import EvaluationResult

DECISION_SCHEMA = "opengpl.decision/1"
# Keys `opengpl audit` needs from every record.
REQUIRED_KEYS = ("id", "timestamp", "policy", "policy_version", "gate", "action", "evaluated")

# Applied after sanitize_pii so redaction does not depend on the PII backend
# (Presidio treats well-known test numbers such as 123-45-6789 as fake).
_REDACTIONS = (
    ("SSN", "[REDACTED-US_SSN]"),
    ("credit_card", "[REDACTED-CREDIT_CARD]"),
)


# Log-only credential shapes the gate regex misses: best-effort, common shapes
# only. Every quantifier is bounded and every unanchored token prefix has a
# lookbehind, so each pattern runs in linear time on adversarial input.
_CRED = "[REDACTED-CREDENTIAL]"
_LOG_CREDENTIAL_PATTERNS = (
    # PEM private key blocks; the body stops at the next "-----", so an
    # unterminated block is still redacted up to that point.
    (
        r"-----BEGIN [A-Z ]{0,40}PRIVATE KEY-----(?:[^-]|-(?!----)){0,16384}"
        r"(?:-----END [A-Z ]{0,40}PRIVATE KEY-----)?",
        _CRED,
    ),
    # JSON Web Tokens.
    (r"(?<![\w-])eyJ[\w-]{5,4096}\.[\w-]{5,4096}\.[\w-]{0,4096}", _CRED),
    # URL userinfo: keep the scheme and the host.
    (r"(?i)\b([a-z][a-z0-9+.-]{0,31}://)[^\s/@:]{1,256}:[^\s/@]{1,256}@", r"\1" + _CRED + "@"),
    # HTTP Basic and Bearer credentials: keep the header name.
    (
        r"(?i)\b(authorization\s{0,16}:\s{0,16})basic\s{1,16}[A-Za-z0-9+/]{1,4096}={0,2}",
        r"\1" + _CRED,
    ),
    (r"(?i)\bbearer\s{1,16}[^\s\",}]{1,4096}", _CRED),
    # Vendor token prefixes.
    (r"(?<![\w-])sk-[A-Za-z0-9_-]{16,256}", _CRED),
    (r"\bAKIA[0-9A-Z]{16}\b", _CRED),
    (r"(?<![\w-])gh[pousr]_[A-Za-z0-9]{20,255}", _CRED),
    (r"(?<![\w-])github_pat_[A-Za-z0-9_]{20,255}", _CRED),
    (r"(?<![\w-])xox[abp]-[A-Za-z0-9-]{10,255}", _CRED),
    # key: value / key=value / "key": "value". A quoted value is taken whole
    # (up to 4096 characters, or to the end of that run if the quote is never
    # closed), so no tail of a multi-word secret is left behind.
    (
        r"(?i)(?:api[_\s-]?key|password|passwd|passphrase|pwd|private[_-]?key|secret|token)"
        r"[\w-]{0,40}\"?\s{0,16}[:=]\s{0,16}(?:\"[^\"]{0,4096}\"?|[^\s\",}]{1,4096})",
        _CRED,
    ),
)


def redact_for_log(text: str) -> str:
    # Credentials first: the PII pass would otherwise split shapes such as
    # URL userinfo (user:pass@host looks like an e-mail address).
    for pat, repl in _LOG_CREDENTIAL_PATTERNS:
        text = re.sub(pat, repl, text)
    text = re.sub(_BLOCK_PATTERNS["credentials"], _CRED, text, flags=re.IGNORECASE)
    text = sanitize_pii(text)
    for key, token in _REDACTIONS:
        text = re.sub(_BLOCK_PATTERNS[key], token, text, flags=re.IGNORECASE)
    return text


def _now() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    dt = datetime.fromtimestamp(int(epoch), UTC) if epoch else datetime.now(UTC)
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
    ) -> dict | None:
        """Record one gate decision; return the record, or None if not recorded.

        Nothing is recorded when the policy sets ``audit.log_level: OFF``.
        Under FULL or DEBUG the record holds the text (redacted unless
        ``audit.pii_in_logs`` is true), but only when the record is kept (a
        file is open or ``max_records`` is not 0). If redaction raises, the
        text is omitted and ``text_redaction`` is set to ``"failed"``; raw text
        is never written as a fallback.
        """
        audit = policy.get("audit") or {}
        if audit.get("log_level") == "OFF":
            return None
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
            "text_sha256": None
            if text is None
            else hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
        kept = self._fh is not None or self.max_records != 0
        if kept and text is not None and audit.get("log_level") in ("FULL", "DEBUG"):
            if audit.get("pii_in_logs") is True:
                rec["text"] = text
            else:
                try:
                    rec["text"] = redact_for_log(text)
                except Exception:
                    rec["text_redaction"] = "failed"
        with self._lock:
            self.records.append(rec)
            if self.max_records is not None and len(self.records) > self.max_records:
                del self.records[: len(self.records) - self.max_records]
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
            missing = [k for k in REQUIRED_KEYS if k not in rec]
            if missing:
                raise ValueError(f"{path}:{lineno}: missing key(s) {', '.join(missing)}")
            out.append(rec)
    return out
