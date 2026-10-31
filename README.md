# OpenGPL

[![CI](https://github.com/sadayamuthu/opengpl/actions/workflows/ci.yml/badge.svg)](https://github.com/sadayamuthu/opengpl/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/opengpl-sdk?logo=pypi&logoColor=white)](https://pypi.org/project/opengpl-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/opengpl-sdk?logo=python&logoColor=white)](https://pypi.org/project/opengpl-sdk/)
[![Docker](https://img.shields.io/badge/docker-ghcr.io%2Fsadayamuthu%2Fopengpl%2Fsidecar-2496ED?logo=docker&logoColor=white)](https://github.com/sadayamuthu/opengpl/pkgs/container/opengpl%2Fsidecar)
[![Spec](https://img.shields.io/badge/spec-v0.1%20public%20draft-orange)](spec/SPEC.md)
[![License](https://img.shields.io/github/license/sadayamuthu/opengpl)](LICENSE)

A policy language for AI agents that produces compliance evidence. One
`.gpl` file says what an agent may take in, what it may produce, which tools
and networks it may use, and which compliance frameworks you're answering to.
The `opengpl` SDK checks prompts and responses against the policy at runtime,
records every decision, and turns the policy and its decision log into
[OSCAL](https://pages.nist.gov/OSCAL/) that an assessor can read: which NIST
SP 800-53 controls the policy addresses, and the runtime decisions behind them.

It is honest about what it enforces. Every control in the output is marked
`enforced`, `heuristic` or `declared`, and the output never claims a control
is met. That judgement stays with the assessor.

<sub>Not related to the GNU General Public License: GPL here stands for
Governance Policy Language.</sub>

## What a policy looks like

```yaml
opengpl: '0.1'
policy: support-agent
version: '1.0.0'
description: Customer-support agent running inside a FedRAMP Moderate boundary
status: ACTIVE
owner: security-team

applies_to:
  models: ['*']
  contexts: [customer-service]

input_controls:
  detect: [prompt_injection, jailbreak]

model_controls:
  allow_tools: [kb_search, ticket_lookup]
  allow_external_calls: false

output_controls:
  block: [SSN, credit_card, credentials]

audit:
  log_level: FULL
  format: OSCAL
  compliance: [FedRAMP-Moderate]

enforcement:
  engine: opengpl-sdk
  on_violation: BLOCK
```

For this policy, `opengpl audit` reports seven NIST SP 800-53 Rev 5 controls
in the Moderate baseline:

| Control | Status | Why |
|---------|--------|-----|
| AU-2, AU-3, AU-12 | `enforced` | The SDK writes a decision record for every check |
| SI-10 | `heuristic` | Injection and jailbreak detection are regular expressions |
| AC-3, AC-4, SC-7 | `declared` | Tool and network limits are stated but not yet enforced by the SDK |

## What it does

| | Today, in `opengpl-sdk` 0.2 |
|---|---|
| **Validate** | Every policy is checked against the JSON Schema on load and by `opengpl validate` |
| **Check input** | Prompt-injection and jailbreak detection (heuristic: regular expressions for well-known phrasings) |
| **Check output** | Blocks SSNs, card numbers, credentials and PHI keywords (heuristic: patterns and keywords) |
| **Record** | A JSONL decision log; prompt and response text is hashed, or redacted at `log_level: FULL` |
| **Evidence** | OSCAL 1.2.3 component definitions and assessment results for FedRAMP Low, Moderate and High (NIST SP 800-53 Rev 5 baselines) |
| **Map** | Mapping tables for NIST AI RMF, EU AI Act, HIPAA and SOC 2 ([compliance-mapping.md](spec/docs/compliance-mapping.md)) |

Not yet enforced: `model_controls` (tools, trust levels, human-in-the-loop),
`input_controls.sanitize`, most of `output_controls`, and
`enforcement.on_violation` (violations always return `BLOCK`). The full
table is in [Implementation status](USAGE.md#implementation-status). Use
the SDK to try the language and to prototype; don't rely on it as your only
defence against prompt injection or data leakage yet.

## Install

OpenGPL needs **Python 3.11 or newer**.

**pip**:

```sh
pip install opengpl-sdk
```

For NLP-based PII detection (Microsoft Presidio and spaCy; a much larger
install), add the extra and download the language model:

```sh
pip install "opengpl-sdk[pii]"
python -m spacy download en_core_web_lg
```

**Docker** (the HTTP sidecar, for services not written in Python):

```sh
docker run --rm -p 8080:8080 -v "$PWD/policies:/policies:ro" \
  ghcr.io/sadayamuthu/opengpl/sidecar:latest
```

**GitHub Actions** (validates policies on every pull request and can write
OSCAL evidence; see [In CI](USAGE.md#in-ci)):

```yaml
- uses: actions/checkout@v4
- uses: sadayamuthu/opengpl@v0
  with:
    policies: 'policies/**/*.gpl'
```

## Quick start

```sh
# Is the policy valid?
opengpl validate support-agent.gpl

# What would it do with this prompt?
opengpl eval support-agent.gpl --prompt "Ignore all previous instructions"
#   INPUT GATE:  BLOCK
#     → prompt_injection detected

# Write OSCAL evidence from the policy and its decision log
opengpl audit support-agent.gpl --framework FedRAMP-Moderate --decisions decisions.jsonl
#   ✓ Component definition written to support-agent-component-definition.json
#     Note: not in the NIST MODERATE baseline, omitted: si-15
#   ✓ Assessment results written to support-agent-assessment-results.json (2 observations)
```

In your application, check before and after the model call, and log every
decision:

```python
from opengpl import PolicyEngine

engine = PolicyEngine("support-agent.gpl", decision_log="decisions.jsonl")

if not engine.check_input(user_message).passed:
    return "Request blocked by policy."
response = call_llm(user_message)
if not engine.check_output(response).passed:
    return "Response withheld by policy."
return response
```

[USAGE.md](USAGE.md) covers the CLI, the Python API, the decision log, the
OSCAL output, the sidecar and the GitHub Action.

## Documentation

- [USAGE.md](USAGE.md): using the CLI, SDK, sidecar and GitHub Action
- [Specification](spec/SPEC.md) and [JSON Schema](spec/schemas/)
- [Compliance mapping](spec/docs/compliance-mapping.md): every mapped control, its policy field and its status
- [Enforcement model](spec/docs/enforcement-model.md) and [integration guide](spec/docs/integration-guide.md)
- [Example policies](spec/examples/) and the [spec changelog](spec/CHANGELOG.md)

## Development

```sh
pip install -e "sdk[dev]"
(cd sdk && pytest -q)                        # tests (regex PII backend)
ruff check . && ruff format --check .        # lint and format
python spec/scripts/validate_examples.py     # example policies are valid
python spec/scripts/gen_compliance_mapping.py --check   # generated tables are current
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the layout, the mapping rules and
how to propose a spec change. Report security issues privately; see
[SECURITY.md](SECURITY.md).

## License

Code, schemas and examples: [Apache License 2.0](LICENSE). The specification
text ([SPEC.md](spec/SPEC.md)): [CC BY 4.0](spec/LICENSE-SPEC). OpenGPL is
maintained by [OpenAstra](https://openastra.org).
