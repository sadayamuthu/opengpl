# Using OpenGPL

- [Implementation status](#implementation-status)
- [The CLI](#the-cli)
- [The Python SDK](#the-python-sdk)
- [The decision log](#the-decision-log)
- [OSCAL output](#oscal-output)
- [The sidecar](#the-sidecar)
- [In CI](#in-ci)
- [Editor support](#editor-support)
- [Compliance frameworks](#compliance-frameworks)
- [Repository layout](#repository-layout)

## Implementation status

OpenGPL is a public draft. The [specification](spec/SPEC.md) describes what a
conforming runtime does; the reference SDK, `opengpl-sdk` 0.2, implements part
of it.

| Policy block | Reference SDK today |
|---|---|
| Schema validation (all blocks) | ✅ Enforced: `opengpl validate`, and on every `PolicyEngine` load |
| `input_controls.detect`: `prompt_injection`, `jailbreak` | ⚠️ Heuristic: a small set of regular expressions for well-known phrasings; easy to evade |
| Other `input_controls.detect` values | ⏳ Parsed, not acted on |
| `input_controls.sanitize` | ⏳ Parsed, not applied. PII helpers are in `opengpl.detectors.pii` (regex by default; Presidio with the `[pii]` extra) |
| `output_controls.block`: `SSN`, `PHI`, `credit_card`, `credentials` | ⚠️ Heuristic: patterns and keywords |
| Other `output_controls` (`redact`, `require`, `hallucination_threshold`, topics) | ⏳ Parsed, not enforced |
| `model_controls` (tools, trust levels, human-in-the-loop) | ⏳ Parsed, not enforced; the model gate always allows |
| `enforcement.on_violation` | ⏳ Violations always return `BLOCK` |
| `audit.log_level` | ✅ Decides what the decision log records; `OFF` records nothing |
| `audit.pii_in_logs` | ⚠️ Heuristic redaction of logged text unless set to `true` |
| `audit.format: OSCAL` | ✅ `opengpl audit` writes OSCAL 1.2.3 |

Contributions to any ⏳ row are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

## The CLI

Installing `opengpl-sdk` adds the `opengpl` command.

```sh
opengpl validate POLICY.gpl
opengpl eval POLICY.gpl --prompt TEXT [--context NAME]
opengpl audit POLICY.gpl --framework FRAMEWORK [--output PATH]
              [--decisions LOG.jsonl] [--results-output PATH]
```

**`validate`** checks a policy file against the JSON Schema. A file may hold
several policies separated by `---`; each one is checked.

**`eval`** runs a prompt through the input gate and a placeholder through the
output gate, and prints what each gate decided. It is a dry run: nothing is
written.

**`audit`** writes an OSCAL component definition for the policy and, with
`--decisions`, OSCAL assessment results from a decision log. See
[OSCAL output](#oscal-output). The default output paths are
`<policy>-component-definition.json` and `<policy>-assessment-results.json`.

| Exit code | Meaning |
|-----------|---------|
| 0 | Success. For `eval`, also when a gate blocks |
| 1 | A file is missing or unreadable, the policy is invalid, or a decision log line is malformed (the message names `path:line`) |
| 2 | `audit` only: the framework has no OSCAL baseline, the policy doesn't list it in `audit.compliance`, or `--decisions` was given but no mapped control is in the baseline |

## The Python SDK

```python
from opengpl import PolicyEngine

engine = PolicyEngine("support-agent.gpl", decision_log="decisions.jsonl")

result = engine.check_input(prompt, context="customer-service")
result.passed    # False when a check fired
result.action    # "ALLOW" or "BLOCK"
result.reasons   # e.g. ["prompt_injection detected"]
result.evaluated # rules checked, e.g. ["input_controls.detect:prompt_injection", ...]
result.fired     # the subset that matched

engine.check_output(response)
engine.check_model()   # always ALLOW today; recorded but excluded from OSCAL results
```

`PolicyEngine` takes one policy per file; use `opengpl.loader.load_all()` for
files with several. The full API reference is in
[sdk/README.md](sdk/README.md); framework patterns (LangChain, AutoGen,
CrewAI) are in the [integration guide](spec/docs/integration-guide.md).

## The decision log

Pass `decision_log=` (a path, or a `opengpl.audit.ledger.DecisionLog`) to
`PolicyEngine` and every check appends one JSON line:

```json
{"schema": "opengpl.decision/1", "id": "6f0c…", "timestamp": "2026-11-01T09:30:00Z",
 "policy": "support-agent", "policy_version": "1.0.0", "gate": "input",
 "passed": false, "action": "BLOCK", "reasons": ["prompt_injection detected"],
 "evaluated": ["input_controls.detect:prompt_injection", "input_controls.detect:jailbreak"],
 "fired": ["input_controls.detect:prompt_injection"], "text_sha256": "9b1d…"}
```

What happens to the prompt or response text depends on the policy:

| `audit.log_level` | Recorded |
|---|---|
| `OFF` | Nothing: no record is written or kept |
| `SUMMARY`, `STANDARD` | The record with a SHA-256 hash of the text, never the text |
| `FULL`, `DEBUG` | The record plus the text, redacted unless `audit.pii_in_logs: true` |

Redaction replaces PII (with the regex backend: email addresses, US SSNs,
card numbers, phone numbers, IP addresses; more with the Presidio extra) and
common credential shapes (best-effort: API-key and token assignments, bearer
and basic auth headers, JWTs, PEM private keys, URL passwords, and AWS,
GitHub, Slack and `sk-` keys) with placeholders such as `[REDACTED-US_SSN]`.
If redaction itself fails, the text is left out and the record says
`"text_redaction": "failed"`; raw text is never written as a fallback.

The JSONL file is the record. `DecisionLog` also keeps the last 10,000
records in memory (`engine.decisions.records`); set `max_records=0` to keep
none. Writes are safe across threads in one process, not across processes, so
give each worker process its own log file.

## OSCAL output

`opengpl audit` writes [OSCAL](https://pages.nist.gov/OSCAL/) 1.2.3 JSON for
the FedRAMP Low, Moderate and High frameworks. FedRAMP no longer publishes its
OSCAL baselines, so the controls are drawn from NIST's SP 800-53 Rev 5 Low,
Moderate and High baselines (`usnistgov/oscal-content` v1.6.0); FedRAMP's
baselines are built on these. A control OpenGPL maps but the baseline
doesn't include (such as SI-15 for Moderate) is left out, with a note.

A control appears only when the policy sets a field that implements it, and
each one carries an `implementation-status`:

| Status | Meaning |
|---|---|
| `enforced` | The SDK blocks or alters behaviour based on this field |
| `heuristic` | The SDK acts on this field using best-effort pattern matching that can miss cases |
| `declared` | The policy states this value but the SDK does not act on it |

When several fields implement one control, it takes the weakest of their
statuses. The output never says a control is satisfied, and contains no
findings: that judgement belongs to the assessor.

- **Component definition**: one component for the policy, and one
  implemented requirement per control, naming the policy fields and values
  behind it.
- **Assessment results**: one observation per input or output decision from
  the log (model-gate decisions are left out), linked to the controls it bears
  on. Observations cite the decision's `id`; no prompt or response text and no
  text hash appear in OSCAL output, so it can be shared.

Output is deterministic: UUIDs are derived from the policy and the decisions,
and `SOURCE_DATE_EPOCH` fixes the timestamps.

The other frameworks (NIST AI RMF, EU AI Act, HIPAA, SOC 2) have no official
OSCAL catalog, so they are covered by the
[mapping tables](spec/docs/compliance-mapping.md) only.

## The sidecar

The sidecar serves the SDK over HTTP, for services not written in Python.
Your application calls it before and after each model call; it is not a
proxy.

```sh
docker run --rm -p 8080:8080 \
  -v "$PWD/policies:/policies:ro" \
  -v "$PWD/logs:/logs" -e OPENGPL_DECISION_LOG=/logs/decisions.jsonl \
  ghcr.io/sadayamuthu/opengpl/sidecar:latest
```

| Method and path | Body | Returns |
|---|---|---|
| `GET /health` | | `{"status": "ok"}` |
| `POST /input/check` | `{"policy": "support-agent.gpl", "prompt": "…", "context": "…"}` | `{"passed", "action", "reasons"}` |
| `POST /output/check` | `{"policy": "support-agent.gpl", "text": "…"}` | `{"passed", "action", "reasons"}` |

| Environment variable | Default | Meaning |
|---|---|---|
| `OPENGPL_POLICY_DIR` | `/policies` | Directory policies are read from; `policy` must be a file name inside it |
| `OPENGPL_DECISION_LOG` | unset | JSONL decision log path; unset means nothing is written |

The sidecar has no authentication and no request-size limit. Run it on a
private network or behind a proxy that provides both. More in
[sidecar/README.md](sidecar/README.md).

## In CI

The GitHub Action validates policy files on every pull request and,
optionally, writes OSCAL evidence. It installs `opengpl-sdk` from PyPI and
writes a report to the job summary.

```yaml
on: pull_request

jobs:
  policy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - id: opengpl
        uses: sadayamuthu/opengpl@v0
        with:
          policies: 'policies/**/*.gpl'
          audit-policy: policies/support-agent.gpl
          framework: FedRAMP-Moderate
      - uses: actions/upload-artifact@v4
        with:
          name: oscal-evidence
          path: opengpl-oscal/
```

| Input | Default | Meaning |
|---|---|---|
| `policies` | `**/*.gpl` | Space- or newline-separated glob patterns of files to validate |
| `audit-policy` | | One policy to write OSCAL output for; empty means validate only |
| `framework` | `FedRAMP-Moderate` | `FedRAMP-Low`, `FedRAMP-Moderate` or `FedRAMP-High` |
| `decisions` | | A JSONL decision log; when set, assessment results are written too |
| `output-dir` | `opengpl-oscal` | Where the OSCAL files go |
| `version` | `latest` | The `opengpl-sdk` version to install |
| `python-version` | `3.11` | Python to run it with |

Outputs: `component-definition` and `assessment-results`, the paths written.
The step fails when any policy is invalid or the audit fails.

## Editor support

The JSON Schema is published at `https://opengpl.org/schema/v0.1/schema.json`.
With the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)
for VS Code, add this line to the top of a policy file for completion and
inline errors:

```yaml
# yaml-language-server: $schema=https://opengpl.org/schema/v0.1/schema.json
```

## Compliance frameworks

| Framework | Covered by |
|---|---|
| FedRAMP Low, Moderate, High (NIST SP 800-53 Rev 5) | OSCAL output and mapping table (AC, AU, IA, SC and SI families) |
| NIST AI Risk Management Framework | Mapping table (GOVERN, MAP, MEASURE and MANAGE subcategories) |
| EU AI Act (high-risk systems) | Mapping table (Articles 12 to 15) |
| HIPAA Technical Safeguards | Mapping table (§164.312(b) and (d)) |
| SOC 2 (Trust Services Criteria) | Mapping table (CC6 and CC7) |
| ISO/IEC 42001, India DPDPA | Partial, planned for spec v0.2 |

A mapping shows which controls a policy can provide evidence for. It is not a
certification. Every row, its policy field, its status and its rationale are
in [compliance-mapping.md](spec/docs/compliance-mapping.md).

## Repository layout

```text
spec/      the specification, JSON Schema, example policies and reference docs
sdk/       the Python package opengpl-sdk: the PolicyEngine, the CLI and the
           compliance mappings (sdk/src/opengpl/compliance/mappings/*.yaml)
sidecar/   the HTTP sidecar image
action.yml the GitHub Action
```
