# src/opengpl/audit/oscal.py
"""OSCAL 1.2.3 output: component definitions and assessment results."""
import uuid
from datetime import datetime, timezone

from opengpl.audit.ledger import _now
from opengpl.compliance.mapping import applicable_controls
from opengpl.compliance.nist import FRAMEWORK_TO_BASELINE, baseline

# --- OSCAL 1.2.3 component definition ---------------------------------------
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
        "title": f"{name} (OpenGPL policy evaluated by opengpl-sdk)",
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


# --- OSCAL 1.2.3 assessment results -----------------------------------------
class NothingToReport(ValueError):
    """No applied control is in the framework's baseline."""


def assessment_results(
    policy: dict, framework: str, decisions: list[dict], *, now: datetime | None = None
) -> dict:
    """Build OSCAL assessment results holding observations only (no findings)."""
    if framework not in FRAMEWORK_TO_BASELINE:
        raise UnsupportedFramework(framework)
    if framework not in (policy.get("audit") or {}).get("compliance", []):
        raise FrameworkNotDeclared(framework)

    name = policy.get("policy")
    version = str(policy.get("version"))
    base = baseline(FRAMEWORK_TO_BASELINE[framework])  # type: ignore[arg-type]
    applied = [a for a in applicable_controls(policy, framework) if a.control in base.controls]
    if not applied:
        raise NothingToReport(f"{name}: no applied control is in the {framework} baseline")

    kept = []
    seen: set[str] = set()
    for d in decisions:  # first occurrence of a decision id wins
        if (d.get("policy") == name and str(d.get("policy_version")) == version
                and d.get("gate") != "model" and str(d["id"]) not in seen):
            seen.add(str(d["id"]))
            kept.append(d)

    res_uuid = _uuid(f"res:{name}:{version}:{framework}")
    ar_uuid = _uuid(
        f"ar:{name}:{version}:{framework}:" + ",".join(sorted(str(d["id"]) for d in kept))
    )

    observations = []
    for d in kept:
        evaluated = d.get("evaluated") or []
        fired = d.get("fired") or []
        rule_fields = {r.split(":", 1)[0] for r in evaluated}
        bears = [
            a.control for a in applied
            if "audit.log_level" in a.fields or rule_fields & set(a.fields)
        ]
        props = [_prop("control-id", c) for c in bears]
        props += [
            _prop("gate", str(d["gate"])),
            _prop("decision-action", str(d["action"])),
            _prop("decision-id", str(d["id"])),
        ]
        observations.append({
            "uuid": _uuid("obs:" + str(d["id"])),
            "title": f"{d['gate']} gate: {d['action']}",
            "description": (
                f"Rules evaluated: {', '.join(evaluated) or 'none'}. "
                f"Rules fired: {', '.join(fired) or 'none'}."
            ),
            "methods": ["TEST"],
            "collected": d["timestamp"],
            "props": props,
            "relevant-evidence": [{
                "description": f"Decision record {d['id']}"
            }],
        })

    stamps = sorted(d["timestamp"] for d in kept)
    start, end = (stamps[0], stamps[-1]) if stamps else (oscal_now(now),) * 2

    result: dict = {
        "uuid": _uuid(f"result:{name}:{version}:{framework}"),
        "title": "OpenGPL runtime decision records",
        "description": (
            "Runtime decision records produced by opengpl-sdk, listed as observations. "
            "Each observation names the controls its evaluated rules map to. "
            "This is evidence for an assessor, not an assessment."
        ),
        "start": start,
        "end": end,
        "reviewed-controls": {"control-selections": [{
            "include-controls": [{"control-id": a.control} for a in applied]
        }]},
    }
    if observations:
        result["observations"] = observations

    return {"assessment-results": {
        "uuid": ar_uuid,
        "metadata": {
            "title": f"OpenGPL decision records for {name} {version} ({framework})",
            "last-modified": oscal_now(now),
            "version": version,
            "oscal-version": OSCAL_VERSION,
        },
        "import-ap": {"href": f"#{res_uuid}"},
        "results": [result],
        "back-matter": {"resources": [{
            "uuid": res_uuid,
            "title": "No assessment plan",
            "description": (
                "Generated by opengpl-sdk from runtime decision records. "
                "No assessment plan exists; these are decision records, not an assessment."
            ),
        }]},
    }}
