# OpenGPL v0.1 Specification

Governance Policy Language — Full Technical Specification

---

| Field | Value |
|---|---|
| **Title** | OpenGPL — Governance Policy Language Specification |
| **Version** | 0.1 |
| **Status** | PUBLIC DRAFT — Community Review Open |
| **Published** | March 2025 |
| **Governed by** | OpenAstra |
| **Spec License** | Creative Commons CC BY 4.0 |
| **Code License** | Apache License 2.0 |
| **Feedback** | [GitHub Discussions](https://github.com/sadayamuthu/opengpl/discussions) |
| **Website** | [opengpl.org](https://opengpl.org) · [openastra.org/opengpl](https://openastra.org/opengpl) |

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Design Principles](#3-design-principles)
4. [Core Concepts](#4-core-concepts)
5. [Policy Schema Reference](#5-policy-schema-reference)
6. [Syntax Specification](#6-syntax-specification)
7. [Enforcement Model](#7-enforcement-model)
8. [Compliance Mapping](#8-compliance-mapping)
9. [Integration Reference](#9-integration-reference)
10. [Versioning & Governance](#10-versioning--governance)
11. [Appendices](#11-appendices)

---

## 1. Abstract

OpenGPL (Governance Policy Language) is an open, declarative policy language purpose-built for generative AI systems and dynamic systems. It defines how AI agents behave, what resources they can access, what they can produce, and how they demonstrate compliance — at runtime and at rest.

Existing policy frameworks such as OPA/Rego, AWS Cedar, and HashiCorp Sentinel were designed for deterministic systems where inputs and outputs are fully known. Generative AI introduces stochastic outputs, contextual reasoning, multi-agent trust hierarchies, and probabilistic risk — none of which existing policy languages address natively.

OpenGPL fills this gap. It provides a structured, human-readable, machine-enforceable policy format for LLM-powered systems, with native support for compliance frameworks including NIST AI RMF, FedRAMP, HIPAA, and the EU AI Act.

This document defines the OpenGPL v0.1 specification, including syntax, schema, enforcement model, and compliance mapping. It is published as a public draft for community review under the OpenAstra.

---

## 2. Introduction

### 2.1 Background

The rapid deployment of large language models (LLMs) and generative AI agents into enterprise and government environments has outpaced the development of policy and governance tooling designed for these systems.

In deterministic systems, a policy evaluation is binary — a request either matches a rule or it does not. In generative AI and dynamic systems, outputs are probabilistic, context-dependent, and semantically rich. A policy that says "block requests containing PII" must now evaluate whether a model's natural language response *inadvertently* reveals PII — a fundamentally different problem.

### 2.2 The Gap OpenGPL Fills

| Framework | Built For | LLM Support | Compliance Output |
|---|---|---|---|
| OPA / Rego | Kubernetes, APIs | None | Custom |
| AWS Cedar | App authorization | None | None |
| HashiCorp Sentinel | IaC / Terraform | None | None |
| NeMo Guardrails | LLM runtime rails | Partial | None |
| **OpenGPL v0.1** | **Generative AI and dynamic systems** | **Native** | **OSCAL / FedRAMP** |

> **Note:** In August 2025, Apple hired the maintainers of OPA with plans to sunset enterprise OPA offerings — further validating the need for a purpose-built AI policy language with neutral governance.

### 2.3 Scope

OpenGPL v0.1 covers:

- Policy syntax and schema for governing LLM input, model behavior, tool access, and output
- Runtime enforcement model via OpenGPL-compatible runtimes (for example the `opengpl-sdk` reference implementation)
- Compliance output mapping to NIST AI RMF, FedRAMP Moderate, HIPAA, and EU AI Act
- Integration patterns for LangChain, AutoGen, CrewAI, and direct API usage
- Versioning and governance model for the OpenGPL standard

### 2.4 Out of Scope (v0.1)

- Training-time policy enforcement *(planned: v0.2)*
- Multi-modal content policy — image, audio, video *(planned: v0.3)*
- Fine-grained attribution and provenance tracking *(planned: v0.3)*

---

## 3. Design Principles

OpenGPL is designed around six core principles:

### P1 — Generative-Native

Policies must reason about probabilistic, contextual outputs — not just binary input matching. OpenGPL natively models confidence thresholds, semantic risk categories, and output variance as first-class policy primitives.

### P2 — Declarative and Human-Readable

Policy authors should not need to be programmers. OpenGPL uses YAML-based syntax designed to be readable by compliance officers, GRC teams, legal counsel, and security engineers alike. Policies serve as both machine-executable artifacts and human-readable governance documents.

### P3 — Framework-Agnostic

OpenGPL policies are portable across LLM providers (OpenAI, Anthropic, Google, Mistral, open-source), agent frameworks (LangChain, AutoGen, CrewAI), and deployment environments (cloud, on-premise, air-gapped). No vendor lock-in.

### P4 — Compliance-First

Every OpenGPL policy generates structured audit evidence in OSCAL-compatible format. Policies can be directly mapped to NIST AI RMF controls, FedRAMP boundaries, HIPAA safeguards, and EU AI Act obligations — reducing compliance documentation burden from weeks to minutes.

### P5 — Open Standard

OpenGPL is governed as an open standard under the OpenAstra at [openastra.org](https://openastra.org). The specification, schema, and reference implementation are published under open licenses. Commercial implementations are permitted without royalty under a FRAND commitment.

### P6 — Composable

Policies are modular and composable. A base policy can be extended, overridden, or inherited by environment-specific or agent-specific policies. Organizations maintain a canonical policy library and apply contextual variations without duplication.

---

## 4. Core Concepts

### 4.1 Policy

A **Policy** is the fundamental unit of OpenGPL. It is a structured YAML document that defines the governance rules for a specific AI agent, model, or use case.

> **Definition:** An OpenGPL Policy is a versioned, machine-enforceable governance artifact that describes the permitted inputs, model behaviors, tool access, and outputs for a defined AI system context.

### 4.2 Control Blocks

A policy is composed of four control blocks, each governing a distinct phase of the LLM interaction lifecycle:

| Block | Governs | Example Controls |
|---|---|---|
| `input_controls` | Incoming prompts and context | Injection detection, PII sanitization, token limits |
| `model_controls` | Model behavior and capabilities | Tool access, trust level, human-in-loop triggers |
| `output_controls` | Generated responses | PII blocking, hallucination limits, tone enforcement |
| `audit` | Evidence generation | Log level, OSCAL output, compliance framework mapping |

### 4.3 Enforcement Engine

OpenGPL policies are executed by **OpenGPL-compatible runtimes**, such as the reference `opengpl-sdk` Python package or other enforcement engines that implement the OpenGPL runtime interface. A runtime acts as a Policy Enforcement Point (PEP) that intercepts LLM requests and responses, evaluates them against applicable policies, and takes the configured enforcement action.

Multiple runtimes may exist; OpenGPL deliberately does not mandate a single implementation.

### 4.4 Trust Levels

Every agent and interaction context in OpenGPL carries a **Trust Level** that controls default policy permissiveness:

| Level | Name | Description | Default Stance |
|---|---|---|---|
| `0` | `UNTRUSTED` | External, unauthenticated agents | Deny-by-default |
| `1` | `LOW` | Authenticated external agents | Minimal permissions |
| `2` | `MEDIUM` | Internal agents with standard access | Standard controls |
| `3` | `HIGH` | Privileged internal agents | Elevated permissions |
| `4` | `SYSTEM` | System-level agents with full authority | Operator-defined |

### 4.5 Compliance Framework

A `compliance` declaration in an OpenGPL policy maps controls to regulatory or standards frameworks. This mapping drives automatic generation of OSCAL compliance evidence artifacts (Component Definitions, System Security Plans, and Assessment Results).

### 4.6 Policy Inheritance

OpenGPL supports single-level policy inheritance via the `extends` field. A child policy inherits all parent controls and may override specific fields. This enables a canonical organizational baseline policy extended with use-case-specific rules without duplication.

---

## 5. Policy Schema Reference

### 5.1 Top-Level Structure

| Field | Type | Required | Description |
|---|---|---|---|
| `opengpl` | string | **Yes** | OpenGPL spec version (e.g., `'0.1'`) |
| `policy` | string | **Yes** | Unique policy identifier (slug format) |
| `version` | string | **Yes** | Semantic version of this policy (e.g., `'1.0.0'`) |
| `description` | string | **Yes** | Human-readable description |
| `status` | enum | **Yes** | `DRAFT` \| `REVIEW` \| `ACTIVE` \| `DEPRECATED` |
| `owner` | string | **Yes** | Team or individual responsible for this policy |
| `applies_to` | object | **Yes** | Scope of application |
| `input_controls` | object | No | Controls governing incoming prompts |
| `model_controls` | object | No | Controls governing model behavior |
| `output_controls` | object | No | Controls governing generated outputs |
| `audit` | object | **Yes** | Audit and compliance configuration |
| `enforcement` | object | **Yes** | Enforcement engine and violation handling |
| `extends` | string | No | Parent policy identifier (for inheritance) |
| `metadata` | object | No | Tags, labels, and organizational metadata |

---

### 5.2 `applies_to` Schema

| Field | Type | Description |
|---|---|---|
| `models` | string[] | LLM model identifiers; wildcard `*` supported |
| `agents` | string[] | Named agent identifiers or wildcard patterns |
| `contexts` | string[] | Deployment context labels |
| `environments` | string[] | `development` \| `staging` \| `production` |
| `effective_from` | date | ISO 8601 date this policy becomes active |
| `effective_until` | date | ISO 8601 date this policy expires |

---

### 5.3 `input_controls` Schema

| Field | Type | Default | Description |
|---|---|---|---|
| `detect` | string[] | `[]` | Threat categories: `prompt_injection`, `jailbreak`, `context_stuffing`, `role_confusion`, `data_exfiltration`, `adversarial_elicitation` |
| `sanitize` | string[] | `[]` | Data categories: `pii`, `credentials`, `internal_system_refs`, `ip_addresses` |
| `max_context_tokens` | integer | unlimited | Maximum token count for input context window |
| `max_prompt_tokens` | integer | unlimited | Maximum token count for the prompt itself |
| `allow_system_override` | boolean | `false` | Whether system prompts can override user-level controls |
| `require_user_auth` | boolean | `false` | Whether verified user identity is required |
| `language_filter` | string[] | `[]` | Permitted natural languages (ISO 639-1 codes) |

---

### 5.4 `model_controls` Schema

| Field | Type | Default | Description |
|---|---|---|---|
| `allow_tools` | string[] | `[]` | Explicitly permitted tool/function names |
| `deny_tools` | string[] | `[]` | Explicitly denied tool/function names |
| `trust_level` | enum | `MEDIUM` | `UNTRUSTED` \| `LOW` \| `MEDIUM` \| `HIGH` \| `SYSTEM` |
| `require_human_in_loop` | string[] | `[]` | Conditions requiring human approval |
| `max_tool_calls` | integer | unlimited | Maximum tool invocations per session |
| `allow_code_execution` | boolean | `false` | Whether the model may execute generated code |
| `allow_external_calls` | boolean | `false` | Whether the model may call external APIs or URLs |
| `temperature_ceiling` | float | provider default | Maximum sampling temperature (0.0–2.0) |
| `model_routing` | object | none | Rules for routing to specific model versions |

---

### 5.5 `output_controls` Schema

| Field | Type | Default | Description |
|---|---|---|---|
| `block` | string[] | `[]` | Data categories to block: `SSN`, `PHI`, `credit_card`, `credentials`, `PII` |
| `redact` | string[] | `[]` | Data categories to replace with `[REDACTED]` |
| `require` | string[] | `[]` | Required output attributes: `source_attribution`, `confidence_score`, `disclaimer` |
| `deny_topics` | string[] | `[]` | Semantic topic categories the model must not address |
| `max_response_tokens` | integer | unlimited | Maximum token count for generated response |
| `hallucination_threshold` | float | none | Maximum acceptable hallucination risk score (0.0–1.0) |
| `tone_enforcement` | string | none | `professional` \| `neutral` \| `formal` \| `supportive` |
| `deny_formats` | string[] | `[]` | Output formats to deny: `executable_code`, `shell_commands`, `sql_injection_patterns` |

---

### 5.6 `audit` Schema

| Field | Type | Default | Description |
|---|---|---|---|
| `log_level` | enum | `SUMMARY` | `OFF` \| `SUMMARY` \| `STANDARD` \| `FULL` \| `DEBUG` |
| `format` | enum | `JSON` | `JSON` \| `OSCAL` \| `SIEM` \| `CEF` |
| `retention_days` | integer | `90` | Log retention period in days |
| `compliance` | string[] | `[]` | See [Compliance Framework Identifiers](#appendix-c--compliance-framework-identifiers) |
| `pii_in_logs` | boolean | `false` | Whether PII may appear in audit logs |
| `evidence_export` | boolean | `false` | Auto-export OSCAL artifacts on policy evaluation |
| `alert_on_violation` | boolean | `true` | Send alerts when policy violations are detected |
| `alert_channels` | string[] | `[]` | `email` \| `slack` \| `pagerduty` \| `siem` |

---

### 5.7 `enforcement` Schema

| Field | Type | Default | Description |
|---|---|---|---|
| `engine` | string | `opengpl-sdk` | Enforcement engine identifier (e.g., `opengpl-sdk`) |
| `on_violation` | enum | `LOG` | Action on policy violation (see [Violation Actions](#72-violation-actions)) |
| `on_detection` | enum | `ALERT` | Action on threat detection |
| `fallback` | enum | `DENY` | Action when enforcement engine is unavailable |

---

## 6. Syntax Specification

### 6.1 Minimal Valid Policy

```yaml
opengpl: '0.1'
policy: my-ai-agent
version: '1.0.0'
description: Baseline policy for a general-purpose agent
status: ACTIVE
owner: security-team

applies_to:
  models: ['*']
  contexts: [general]

audit:
  log_level: SUMMARY
  compliance: [SOC2]

enforcement:
  engine: opengpl-sdk
  on_violation: LOG
```

---

### 6.2 Full Example — Healthcare Customer Service Agent

```yaml
opengpl: '0.1'
policy: healthcare-customer-service
version: '2.1.0'
description: >
  Governs the patient-facing customer service AI agent for
  an outpatient healthcare portal. Enforces HIPAA safeguards
  and restricts clinical advice.
status: ACTIVE
owner: healthcare-compliance-team
extends: org-baseline-policy

applies_to:
  models:
    - gpt-4o
    - claude-3-5-sonnet
  agents:
    - patient-portal-bot
  contexts:
    - appointment-booking
    - billing-inquiry
    - general-health-info
  environments: [production]
  effective_from: '2025-01-01'

input_controls:
  detect:
    - prompt_injection
    - jailbreak
    - role_confusion
  sanitize:
    - pii
    - credentials
  max_context_tokens: 8000
  max_prompt_tokens: 2000
  require_user_auth: true

model_controls:
  allow_tools:
    - appointment_search
    - billing_lookup
    - faq_retrieval
  deny_tools:
    - code_execution
    - file_write
    - external_api
    - email_send
  trust_level: LOW
  require_human_in_loop:
    - medication_question
    - diagnostic_inquiry
    - billing_dispute_above_500
  allow_code_execution: false
  allow_external_calls: false
  max_tool_calls: 10

output_controls:
  block:
    - SSN
    - PHI
    - credit_card
    - date_of_birth
  redact:
    - phone_number
    - email_address
  deny_topics:
    - clinical_diagnosis
    - medication_prescription
    - surgical_advice
  require:
    - source_attribution
    - disclaimer_not_medical_advice
  max_response_tokens: 800
  tone_enforcement: supportive
  hallucination_threshold: 0.15

audit:
  log_level: FULL
  format: OSCAL
  retention_days: 2555  # 7 years per HIPAA
  compliance:
    - HIPAA
    - SOC2
    - NIST-AI-RMF
  pii_in_logs: false
  evidence_export: true
  alert_on_violation: true
  alert_channels: [pagerduty, siem]

enforcement:
  engine: opengpl-sdk
  on_violation: BLOCK
  on_detection: ALERT
  fallback: DENY

metadata:
  tags: [healthcare, hipaa, patient-facing]
  review_cycle: quarterly
  last_reviewed: '2025-01-15'
  approved_by: CISO
```

---

### 6.3 Policy Inheritance Example

```yaml
opengpl: '0.1'
policy: dev-sandbox-agent
version: '1.0.0'
description: Developer sandbox — relaxed controls for internal testing
status: ACTIVE
owner: engineering-team
extends: org-baseline-policy  # Inherits all parent controls

applies_to:
  environments: [development]
  agents: [dev-*]  # Wildcard: all agents prefixed with 'dev-'

# Override only what differs from the parent
model_controls:
  trust_level: HIGH
  allow_code_execution: true  # Permitted in dev sandbox
  max_tool_calls: 50

audit:
  log_level: DEBUG
  alert_on_violation: false  # No alerts in dev

enforcement:
  on_violation: LOG  # Log only — don't block in dev
```

---

### 6.4 Validation Rules

An OpenGPL policy document is valid if and only if:

1. The `opengpl` field matches a published OpenGPL specification version
2. The `policy` field is a non-empty string in slug format (lowercase letters, numbers, hyphens)
3. The `version` field follows semantic versioning (`MAJOR.MINOR.PATCH`)
4. `applies_to.models` and `applies_to.contexts` arrays are non-empty
5. The `audit` and `enforcement` blocks are present and contain required fields
6. If `extends` is specified, the parent policy must exist and be accessible
7. All enum fields contain values from the defined enumeration sets
8. Date fields use ISO 8601 format (`YYYY-MM-DD`)
9. `hallucination_threshold` must be between `0.0` and `1.0` if specified
10. `temperature_ceiling` must be between `0.0` and `2.0` if specified

---

## 7. Enforcement Model

### 7.1 Enforcement Architecture

OpenGPL enforcement follows the Policy Decision Point / Policy Enforcement Point (PDP/PEP) model, adapted for generative AI:

```text
  User / Agent Request
         │
         ▼
  ┌─────────────────┐
  │  PEP: Input     │  ← runtime intercepts request
  │  Gate           │  ← input_controls evaluated
  └────────┬────────┘
           │ ALLOW
           ▼
  ┌─────────────────┐
  │  PDP: OpenGPL   │  ← model_controls validated
  │  Engine         │  ← trust level determined
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  LLM Provider   │  ← model generates response
  │  (any model)    │  ← tool calls evaluated per-call
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  PEP: Output    │  ← output_controls evaluated
  │  Gate           │  ← redaction applied
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  Audit Ledger   │  ← OSCAL evidence generated
  │                 │  ← compliance artifacts assembled
  └────────┬────────┘
           │
           ▼
  Final Response / Violation Action
```

---

### 7.2 Violation Actions

| Action | Behavior | Typical Use Case |
|---|---|---|
| `ALLOW` | Pass through with no modification | Monitoring mode, low-risk contexts |
| `LOG` | Pass through and write to audit log | Development, testing, observability |
| `REDACT` | Pass through with sensitive data replaced by `[REDACTED]` | PII protection, output sanitization |
| `ALERT` | Pass through and trigger configured alert channels | Suspicious activity, anomaly detection |
| `BLOCK` | Return policy violation error; request not processed | Production enforcement, high-risk contexts |
| `ESCALATE` | Pause and route to human reviewer queue | Financial decisions, medical queries, legal content |
| `DENY` | Hard denial with audit log; no fallback | Absolute prohibitions, critical violations |

> **Rule:** `DENY` always overrides all other actions, regardless of policy specificity or inheritance.

---

### 7.3 Evaluation Order

When a policy is evaluated, controls are applied in the following sequence:

1. Policy applicability check (`applies_to` scope validation)
2. Trust level determination
3. `input_controls` evaluation (left to right within block)
4. `model_controls` validation (pre-dispatch)
5. Tool call evaluation (per-call, during execution)
6. `output_controls` evaluation (post-generation)
7. Audit record generation
8. Violation action execution

---

### 7.4 Conflict Resolution

When multiple policies apply to the same agent or context:

- More specific policies take precedence over less specific policies
- Child policies override parent policy fields (inheritance model)
- When two sibling policies conflict, the **stricter** (more restrictive) control applies
- `DENY` always overrides all other actions regardless of policy specificity

---

## 8. Compliance Mapping

### 8.1 NIST AI Risk Management Framework

| NIST AI RMF Function | OpenGPL Block | Key Controls |
|---|---|---|
| **GOVERN** | Policy metadata, `audit` | `owner`, `review_cycle`, `compliance` declaration |
| **MAP** | `applies_to`, `metadata` | Context mapping, risk classification, model inventory |
| **MEASURE** | `audit`, `output_controls` | `log_level`, `hallucination_threshold`, `evidence_export` |
| **MANAGE** | `enforcement`, `model_controls` | `on_violation`, `trust_level`, `require_human_in_loop` |

---

### 8.2 FedRAMP Moderate Baseline

| Control Family | OpenGPL Mapping | Coverage |
|---|---|---|
| AC — Access Control | `model_controls.trust_level`, `require_user_auth` | AC-2, AC-3, AC-6 |
| AU — Audit & Accountability | `audit` block (all fields) | AU-2, AU-3, AU-9, AU-12 |
| CM — Configuration Management | Policy `version`, `status`, `extends` | CM-2, CM-6, CM-9 |
| IA — Identification & Auth | OpenID.ai integration, `require_user_auth` | IA-2, IA-3, IA-5 |
| SI — System Integrity | `input_controls.detect`, `output_controls.block` | SI-3, SI-10 |
| SC — System & Comm. Protection | `model_controls.allow_external_calls` | SC-7, SC-8 |

---

### 8.3 HIPAA Technical Safeguards

| Safeguard | 45 CFR Reference | OpenGPL Control |
|---|---|---|
| Access Control | 164.312(a)(1) | `trust_level`, `require_user_auth`, `allow_tools` |
| Audit Controls | 164.312(b) | `log_level: FULL`, `retention_days: 2555` |
| Integrity | 164.312(c)(1) | `output_controls.block: [PHI]`, `hallucination_threshold` |
| Transmission Security | 164.312(e)(1) | `allow_external_calls: false` |

---

### 8.4 EU AI Act (High-Risk Systems)

| Article | Requirement | OpenGPL Coverage |
|---|---|---|
| Article 10 | Data governance | `input_controls.sanitize` |
| Article 11 | Technical documentation | Policy document serves as technical documentation |
| Article 13 | Transparency & information | `output_controls.require: [disclaimer, source_attribution]` |
| Article 14 | Human oversight | `model_controls.require_human_in_loop` |
| Article 15 | Accuracy & robustness | `output_controls.hallucination_threshold` |

---

## 9. Integration Reference

### 9.1 Python SDK (`opengpl-sdk`)

```python
from opengpl import PolicyEngine

engine = PolicyEngine("policy.gpl")

# Evaluate before sending to LLM
input_result = engine.check_input(
    text=user_message,
)

if not input_result.passed:
    return "Request blocked by policy."

# Send to LLM
response = llm.complete(prompt=user_message)

# Evaluate LLM output
output_result = engine.check_output(text=response)
return response if output_result.passed else "Response blocked by policy."
```

---

### 9.2 LangChain Integration

```python
from langchain.callbacks import OpenGPLCallback
from opengpl import PolicyEngine

policy = PolicyEngine("policy.gpl")
callback = OpenGPLCallback(policy=policy)

llm = ChatOpenAI(callbacks=[callback])
# Policy is automatically enforced on all LLM calls
```

---

### 9.3 Validation API (`opengpl-sdk`)

```bash
# Validate a policy via the reference validation API
curl -X POST https://api.opengpl.org/validate \
  -H "Content-Type: application/json" \
  -d '{"policy": "...yaml contents...", "version": "0.1"}'
```

---

### 9.4 OpenID.ai Identity Integration

When `require_user_auth: true` is set, an OpenGPL-compatible runtime can validate the requesting agent's identity token via services such as OpenID.ai before policy evaluation proceeds.

```yaml
# Policy with OpenID.ai enforcement
model_controls:
  trust_level: LOW
  require_user_auth: true
  # Trust level is automatically elevated based on
  # OpenID.ai identity verification result
```

---

### 9.5 ControlGate (OpenCIQ) Integration

ControlGate natively imports OpenGPL policies and uses them as the source of truth for automated compliance evidence assembly. When `evidence_export: true` and `format: OSCAL` are set, ControlGate automatically assembles OSCAL System Security Plan artifacts from runtime enforcement logs.

```yaml
audit:
  format: OSCAL
  evidence_export: true
  compliance: [FedRAMP-Moderate]
  # ControlGate / OpenCIQ picks up OSCAL artifacts
  # and assembles SSP documentation automatically
```

---

## 10. Versioning & Governance

### 10.1 Specification Versioning

OpenGPL follows semantic versioning for the specification:

- **MAJOR** — Breaking changes to the schema (require policy migration)
- **MINOR** — New fields, new enumeration values, new control blocks (backward-compatible)
- **PATCH** — Clarifications, corrections, non-normative changes

The `opengpl` field in policy documents references `MAJOR.MINOR` only (e.g., `'0.1'`). PATCH updates do not require policy changes.

### 10.2 Governance

OpenGPL is an open standard maintained by **OpenAstra** at [openastra.org](https://openastra.org):

- Specification changes require a public comment period of **minimum 30 days**
- Decisions are made by rough consensus among active contributors
- Any organization or individual may contribute via GitHub
- Specification text is licensed under **Creative Commons CC BY 4.0**
- Reference implementations are licensed under **Apache License 2.0**

> Community governance will be formalized at v1.0. Until then, OpenAstra maintains editorial control with full transparency via GitHub.

### 10.3 IP Notice

OpenGPL is an open standard. The specification itself (schema, field definitions, compliance mappings, this document) is published as prior art under CC BY 4.0. Certain methods implemented in commercial enforcement engines are protected under pending patent applications filed by OpenAstra. Use of the OpenGPL specification to build compatible implementations is expressly permitted under the FRAND commitment at [openastra.org/opengpl/frand](https://openastra.org/opengpl/frand).

---

## 11. Appendices

### Appendix A — Threat Category Definitions

| Category | Definition |
|---|---|
| `prompt_injection` | An attempt to override system instructions via crafted user input |
| `jailbreak` | An attempt to cause the model to ignore safety guidelines or policy constraints |
| `context_stuffing` | Injection of false or misleading context into the prompt to manipulate model behavior |
| `role_confusion` | Attempts to cause the model to adopt an unauthorized role or persona |
| `data_exfiltration` | Prompts designed to cause the model to reveal system context, other users' data, or internal information |
| `adversarial_elicitation` | Systematic probing designed to map model capabilities or extract training data |

---

### Appendix B — Data Classification Categories

| Category | Examples | Regulatory Reference |
|---|---|---|
| `PII` | Name, address, email, phone | GDPR, CCPA, DPDPA |
| `PHI` | Medical records, diagnoses, prescriptions | HIPAA |
| `SSN` | US Social Security Numbers | US Federal Law |
| `credit_card` | Payment card numbers (PAN) | PCI-DSS |
| `credentials` | Passwords, API keys, tokens, secrets | SOC2, FedRAMP |
| `date_of_birth` | Full or partial dates of birth | COPPA, HIPAA |
| `biometric` | Fingerprints, face data, voice prints | BIPA, GDPR |
| `financial` | Account numbers, tax IDs, salary data | GLBA, SOX |

---

### Appendix C — Compliance Framework Identifiers

Valid values for the `audit.compliance` array:

| Identifier | Framework | Issuer |
|---|---|---|
| `FedRAMP-Low` | FedRAMP Low Baseline | US GSA / CISA |
| `FedRAMP-Moderate` | FedRAMP Moderate Baseline | US GSA / CISA |
| `FedRAMP-High` | FedRAMP High Baseline | US GSA / CISA |
| `HIPAA` | Health Insurance Portability and Accountability Act | US HHS |
| `SOC2` | SOC 2 Type II (Trust Service Criteria) | AICPA |
| `EU-AI-Act` | EU Artificial Intelligence Act | European Commission |
| `NIST-AI-RMF` | NIST AI Risk Management Framework | NIST |
| `ISO-42001` | AI Management System Standard | ISO/IEC |
| `DPDPA` | Digital Personal Data Protection Act | Government of India |
| `CCPA` | California Consumer Privacy Act | State of California |

---

### Appendix D — References

- [NIST AI Risk Management Framework (AI 100-1)](https://airc.nist.gov)
- [OSCAL — Open Security Controls Assessment Language](https://pages.nist.gov/OSCAL)
- [EU AI Act (Regulation (EU) 2024/1689)](https://eur-lex.europa.eu)
- [FedRAMP Authorization Framework](https://www.fedramp.gov)
- [OPA / Rego Specification](https://www.openpolicyagent.org/docs)
- [AWS Cedar Policy Language](https://cedarpolicy.com)
- [OpenAstra](https://openastra.org/opengpl)

---

## Copyright & License

**Specification text:** Copyright © 2025 OpenAstra. Licensed under [Creative Commons CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
You are free to share and adapt this specification with attribution.

**Reference implementations, schemas, examples:** Licensed under [Apache License 2.0](https://opensource.org/licenses/Apache-2.0).

---

<div align="center">

**OpenGPL is an [OpenAstra](https://openastra.ai) initiative**  
An [OpenAstra](https://openastra.org) Open Standard

[opengpl.org](https://opengpl.org/opengpl) · [openastra.org/opengpl](https://openastra.org/opengpl) · [openastra.ai](https://openastra.ai)

End of OpenGPL v0.1 Specification

</div>
