<div align="center">

<!-- <img src="https://openastra.org/assets/opengpl-logo.svg" alt="OpenGPL" width="120" /> -->

# OpenGPL

## Generative Policy Language

The open policy language for generative AI systems

[![Version](https://img.shields.io/badge/version-v0.1--draft-blue?style=flat-square)](https://github.com/sadayamuthu/opengpl/releases)
[![Status](https://img.shields.io/badge/status-Public%20Draft-orange?style=flat-square)](https://github.com/sadayamuthu/opengpl/blob/main/SPEC.md)
[![License: CC BY 4.0](https://img.shields.io/badge/Spec%20License-CC%20BY%204.0-green?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)
[![License: Apache 2.0](https://img.shields.io/badge/Code%20License-Apache%202.0-green?style=flat-square)](https://opensource.org/licenses/Apache-2.0)
[![OpenAstra](https://img.shields.io/badge/Governed%20by-OpenAstra%20Standards-1B4F8A?style=flat-square)](https://openastra.org)
[![Discussions](https://img.shields.io/badge/Discuss-GitHub%20Discussions-purple?style=flat-square)](https://github.com/sadayamuthu/opengpl/discussions)

---

[Specification](./SPEC.md) · [Schema](./schema/) · [Examples](./examples/) · [Changelog](./CHANGELOG.md) · [Contributing](./CONTRIBUTING.md) · [openastra.org](https://openastra.org) · [opengpl.org](https://opengpl.org)

</div>

---

## What is OpenGPL?

OpenGPL (Generative Policy Language) is an open, declarative policy language purpose-built for generative AI systems. It defines **how AI agents behave**, what resources they can access, what they can produce, and how they demonstrate compliance — at runtime and at rest.

```yaml
opengpl: '0.1'
policy: customer-service-agent
version: '1.0.0'
description: Governs the customer-facing AI support agent

applies_to:
  models: ['gpt-4o', 'claude-3-5-sonnet']
  contexts: [customer-service]

input_controls:
  detect: [prompt_injection, jailbreak]
  sanitize: [pii, credentials]

output_controls:
  block: [SSN, PHI, credit_card]
  require: [source_attribution]

audit:
  log_level: FULL
  format: OSCAL
  compliance: [FedRAMP-Moderate, SOC2]

enforcement:
  engine: opengpl-runtime
  on_violation: BLOCK
```

---

## Why OpenGPL?

Existing policy languages — OPA/Rego, AWS Cedar, HashiCorp Sentinel — were built for **deterministic systems**. Generative AI breaks every assumption they were built on:

| Challenge | Deterministic Systems | Generative AI Systems |
|---|---|---|
| Output predictability | Binary, fully known | Probabilistic, context-dependent |
| Policy evaluation | Pattern matching | Semantic reasoning required |
| Compliance evidence | Static logs | Dynamic, session-based artifacts |
| Trust model | User → Resource | Agent → Model → Tool → Output |
| Threat model | Known attack patterns | Novel, adaptive (prompt injection, jailbreaks) |

**OpenGPL is built for the generative world.**

---

## Core Features

- **🔒 Four-plane policy control** — Input, Model, Output, and Audit planes in a single document
- **🤖 LLM-native** — Trust levels, hallucination thresholds, and tool access as first-class primitives
- **📋 Compliance-first** — Native mapping to FedRAMP, NIST AI RMF, HIPAA, and EU AI Act
- **📄 OSCAL output** — Policies auto-generate compliance evidence artifacts
- **🧩 Composable** — Inherit and extend base policies; wildcard agent matching
- **🔓 Open standard** — Governed by OpenAstra, licensed CC BY 4.0; no vendor lock-in
- **⚙️ Framework-agnostic** — Works with any LLM provider or agent framework

---

## Quick Start

### 1. Install the OpenGPL runtime

```bash
pip install opengpl-runtime
```

### 2. Write a policy

```yaml
# my-policy.gpl
opengpl: '0.1'
policy: my-agent
version: '1.0.0'
description: My first OpenGPL policy
status: ACTIVE
owner: security-team

applies_to:
  models: ['*']
  contexts: [general]

audit:
  log_level: SUMMARY
  compliance: [SOC2]

enforcement:
  engine: opengpl-runtime
  on_violation: LOG
```

### 3. Apply the policy

```python
from opengpl import PolicyEngine

engine = PolicyEngine("my-policy.gpl")

# Evaluate before LLM call
result = engine.check_input(user_message)
if not result.passed:
    return "Request blocked by policy."

# Evaluate after LLM response (optional)
output = engine.check_output(llm_response)
return llm_response if output.passed else "Response blocked by policy."
```

---

## Repository Structure

```text
opengpl/
├── SPEC.md                    # Full OpenGPL v0.1 specification
├── README.md                  # This file
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # How to contribute
├── LICENSE-SPEC               # CC BY 4.0 (specification)
├── LICENSE-CODE               # Apache 2.0 (reference code)
├── schema/
│   ├── opengpl-v0.1.json      # JSON Schema for validation
│   └── opengpl-v0.1.yaml      # YAML Schema reference
├── examples/
│   ├── minimal.gpl            # Minimal valid policy
│   ├── healthcare-hipaa.gpl   # Healthcare / HIPAA example
│   ├── fedramp-moderate.gpl   # FedRAMP Moderate example
│   ├── multi-agent.gpl        # Multi-agent trust hierarchy
│   └── dev-sandbox.gpl        # Development sandbox policy
└── docs/
    ├── compliance-mapping.md  # Framework mapping reference
    ├── enforcement-model.md   # How enforcement works
    └── integration-guide.md   # LangChain, AutoGen, direct API
```

---

## Compliance Frameworks Supported

| Framework | Coverage |
|---|---|
| NIST AI Risk Management Framework | Full control mapping |
| FedRAMP Low / Moderate / High | Full control mapping + OSCAL output |
| HIPAA Technical Safeguards | Full coverage |
| EU AI Act (High-Risk) | Articles 10, 11, 13, 14, 15 |
| SOC 2 (Trust Service Criteria) | Full coverage |
| ISO/IEC 42001 | Partial |
| India DPDPA | Partial |

---

## Using the Schema

The OpenGPL JSON Schema is published at:

```text
https://opengpl.org/schemas/v0.1/opengpl.schema.json
```

> **Note:** This URL is live once the `v0.1.0` release is published via the release workflow.
> Until then, use the raw GitHub URL:
> `https://raw.githubusercontent.com/sadayamuthu/opengpl/main/schema/opengpl-v0.1.json`

### Editor Support (VS Code)

Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) and add this comment to the top of any policy file:

```yaml
# yaml-language-server: $schema=https://opengpl.org/schemas/v0.1/opengpl.schema.json
opengpl: '0.1'
policy: my-agent-policy
version: '1.0.0'
```

You will get auto-complete and inline validation errors as you type — no install needed.

### CI Validation (Python)

```bash
pip install jsonschema pyyaml
python3 -c "
import yaml, jsonschema, urllib.request, json
schema = json.loads(urllib.request.urlopen('https://opengpl.org/schemas/v0.1/opengpl.schema.json').read())
jsonschema.validate(yaml.safe_load(open('my-policy.gpl')), schema)
print('Policy valid')
"
```

Replace `my-policy.gpl` with the path to your policy file.

---

## Contributing

OpenGPL is an open standard maintained by **OpenAstra** at [openastra.org](https://openastra.org).

- 📖 Read the [full specification](./SPEC.md)
- 💬 Join [GitHub Discussions](https://github.com/sadayamuthu/opengpl/discussions)
- 🐛 File issues for spec clarifications or bugs
- 📝 Submit pull requests for examples, schema fixes, or doc improvements
- 🗳️ Participate in [GitHub Discussions](https://openastra.org/opengpl)

All specification changes require a **30-day public comment period**.  
See [CONTRIBUTING.md](./CONTRIBUTING.md) for full governance details.

---

## License

- **Specification** ([SPEC.md](./SPEC.md)): [Creative Commons CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Reference code, schemas, examples**: [Apache License 2.0](https://opensource.org/licenses/Apache-2.0)

---

<div align="center">

**OpenGPL is an [OpenAstra](https://openastra.org) initiative**  

[opengpl](https://opengpl.org/opengpl) · [openastra](https://openastra.org)

</div>
