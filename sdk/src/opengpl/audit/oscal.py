# src/opengpl/audit/oscal.py
"""
Basic OSCAL stub for open source runtime.
Full OSCAL assembly (component definitions, assessment results, POA&M)
is a ControlGate commercial feature.
"""

def generate_oscal_stub(policy_name: str, framework: str) -> dict:
    """
    Returns a minimal OSCAL System Security Plan stub.
    Full OSCAL artifact assembly requires ControlGate.
    """
    return {
        "oscal-version": "1.0.4",
        "metadata": {
            "title": policy_name,
            "framework": framework,
            "NOTE": (
                "This is a basic stub. Full OSCAL assembly with component "
                "definitions, assessment results, and POA&M requires ControlGate. "
                "See https://openastra.ai/controlgate"
            ),
        },
    }


# --- OSCAL 1.2.3 component definition ---------------------------------------
import uuid
from datetime import datetime, timezone

from opengpl.audit.ledger import _now
from opengpl.compliance.mapping import applicable_controls
from opengpl.compliance.nist import FRAMEWORK_TO_BASELINE, baseline

OSCAL_VERSION = "1.2.3"
NS = "https://opengpl.org/ns/oscal"
UUID_NS = uuid.uuid5(uuid.NAMESPACE_URL, NS)

_STATUS_REMARKS = (
    "implementation-status values: "
    "enforced = the SDK blocks or alters behavior based on this field; "
    "heuristic = the SDK acts on this field using best-effort pattern matching that can miss cases; "
    "declared = the policy states this value but the SDK does not act on it."
)


class UnsupportedFramework(ValueError):
    """The framework has no NIST baseline mapping."""


class FrameworkNotDeclared(ValueError):
    """The framework is not listed in the policy's audit.compliance."""


def oscal_now(now: datetime | None = None) -> str:
    """UTC timestamp YYYY-MM-DDTHH:MM:SSZ; SOURCE_DATE_EPOCH overrides the clock."""
    if now is None:
        return _now()
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uuid(key: str) -> str:
    return str(uuid.uuid5(UUID_NS, key))


def _prop(name: str, value: str) -> dict:
    return {"name": name, "ns": NS, "value": value}


def component_definition(
    policy: dict, framework: str, *, now: datetime | None = None
) -> tuple[dict, list[str]]:
    """Build an OSCAL component definition; returns (document, omitted_controls)."""
    import opengpl

    if framework not in FRAMEWORK_TO_BASELINE:
        raise UnsupportedFramework(framework)
    if framework not in (policy.get("audit") or {}).get("compliance", []):
        raise FrameworkNotDeclared(framework)

    name = policy.get("policy")
    version = str(policy.get("version"))
    base = baseline(FRAMEWORK_TO_BASELINE[framework])  # type: ignore[arg-type]
    applied = applicable_controls(policy, framework)
    in_base = [a for a in applied if a.control in base.controls]
    omitted = [a.control for a in applied if a.control not in base.controls]

    props = [_prop("policy-name", str(name)), _prop("policy-version", version)]
    if policy.get("opengpl"):
        props.append(_prop("opengpl-version", str(policy["opengpl"])))
    props.append(_prop("sdk-version", opengpl.__version__))

    component: dict = {
        "uuid": _uuid(f"comp:{name}:{version}:{framework}"),
        "type": "software",
        "title": f"{name} (OpenGPL policy enforced by opengpl-sdk)",
        "description": (policy.get("description") or "").strip() or f"OpenGPL policy {name}",
        "props": props,
    }
    if in_base:
        # OSCAL 1.2.3 control-implementation has no remarks field; define statuses on the component.
        component["remarks"] = _STATUS_REMARKS
        reqs = []
        for a in in_base:
            rprops = [_prop("implementation-status", a.status.value)]
            rprops += [_prop("policy-field", e) for e in a.evidence]
            reqs.append({
                "uuid": _uuid(f"ir:{name}:{version}:{a.control}"),
                "control-id": a.control,
                "description": " ".join(a.statements),
                "props": rprops,
            })
        component["control-implementations"] = [{
            "uuid": _uuid(f"ci:{name}:{version}:{framework}"),
            "source": base.href,
            "description": (
                f"Controls from the NIST SP 800-53 Rev 5 {base.level} baseline addressed by "
                "fields set in this OpenGPL policy. This lists policy fields mapped to controls; "
                "it is not an assessment."
            ),
            "implemented-requirements": reqs,
        }]

    doc = {"component-definition": {
        "uuid": _uuid(f"cd:{name}:{version}:{framework}"),
        "metadata": {
            "title": f"OpenGPL policy {name} {version} ({framework})",
            "last-modified": oscal_now(now),
            "version": version,
            "oscal-version": OSCAL_VERSION,
        },
        "components": [component],
    }}
    return doc, omitted
