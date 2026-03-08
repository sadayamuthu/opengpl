# src/opengpl/audit/ledger.py
import json
from datetime import datetime, timezone
from opengpl.models import EvaluationResult


class AuditLedger:
    def __init__(self):
        self.events: list[dict] = []

    def record(self, event_type: str, result: EvaluationResult, policy_name: str) -> None:
        self.events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "policy": policy_name,
            "passed": result.passed,
            "action": result.action,
            "reasons": result.reasons,
        })

    def to_json(self) -> str:
        return json.dumps(self.events, indent=2)
