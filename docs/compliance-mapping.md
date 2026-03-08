# OpenGPL Compliance Mapping Reference

This document provides detailed mapping between OpenGPL policy controls and major compliance frameworks. Use this reference when designing policies for regulated environments.

**Maintained by OpenAstra — [openastra.org/opengpl](https://openastra.org/opengpl)**

---

## Table of Contents

1. [NIST AI Risk Management Framework](#1-nist-ai-risk-management-framework)
2. [FedRAMP (Low / Moderate / High)](#2-fedramp)
3. [HIPAA Technical Safeguards](#3-hipaa)
4. [EU AI Act](#4-eu-ai-act)
5. [SOC 2 Trust Service Criteria](#5-soc-2)
6. [ISO/IEC 42001](#6-isoiec-42001)
7. [India DPDPA](#7-india-dpdpa)
8. [OSCAL Evidence Generation](#8-oscal-evidence-generation)

---

## 1. NIST AI Risk Management Framework

The NIST AI RMF (NIST AI 100-1) organizes AI governance into four core functions: GOVERN, MAP, MEASURE, and MANAGE.

### GOVERN

| RMF Sub-Function | OpenGPL Control | Notes |
|---|---|---|
| GV-1: Policies and procedures | Policy document itself | Each policy is a governance artifact |
| GV-2: Accountability | `owner` field | Assigns responsibility |
| GV-3: Organizational roles | `owner`, `metadata.approved_by` | Role-based accountability |
| GV-4: Risk tolerance | `enforcement.on_violation` | Defines organizational risk posture |
| GV-6: Review cadence | `metadata.review_cycle` | Formal review schedule |

### MAP

| RMF Sub-Function | OpenGPL Control | Notes |
|---|---|---|
| MP-2: Impact classification | `applies_to.contexts` | Context maps to risk level |
| MP-3: AI system inventory | `applies_to.models`, `applies_to.agents` | Model and agent inventory |
| MP-4: Risk identification | `input_controls.detect` | Threat category enumeration |
| MP-5: Stakeholder identification | `owner`, `audit.alert_channels` | Defines who is notified |

### MEASURE

| RMF Sub-Function | OpenGPL Control | Notes |
|---|---|---|
| MS-1: Measurement methods | `audit.log_level`, `audit.format` | Defines evidence collection |
| MS-2: Evaluation | `output_controls.hallucination_threshold` | Quantified quality metric |
| MS-2.5: Bias/fairness | `output_controls.deny_topics` | Topic restrictions reduce discriminatory outputs |
| MS-4: Incident tracking | `audit.alert_on_violation`, `audit.alert_channels` | Incident notification |

### MANAGE

| RMF Sub-Function | OpenGPL Control | Notes |
|---|---|---|
| MG-1: Response plans | `enforcement.on_violation` | Defines violation response |
| MG-2: Incident response | `enforcement.on_detection`, `audit.alert_channels` | Detection and escalation |
| MG-3: Risk treatment | `model_controls.trust_level` | Risk-based access control |
| MG-4: Residual risk | `enforcement.fallback` | Fail-safe behavior |

---

## 2. FedRAMP

### FedRAMP Low Baseline

Minimum controls for low-impact federal systems. Suitable for publicly available information.

```yaml
audit:
  compliance: [FedRAMP-Low]
  log_level: SUMMARY
  format: OSCAL
  retention_days: 365

enforcement:
  on_violation: LOG
```

### FedRAMP Moderate Baseline

Required controls for most federal civilian agency systems handling Controlled Unclassified Information (CUI).

| Control Family | Control ID | OpenGPL Mapping |
|---|---|---|
| Access Control | AC-2 | `model_controls.trust_level`, `require_user_auth` |
| Access Control | AC-3 | `model_controls.allow_tools`, `deny_tools` |
| Access Control | AC-6 | `trust_level: LOW` for least privilege |
| Audit & Accountability | AU-2 | `audit.log_level: STANDARD` or higher |
| Audit & Accountability | AU-3 | `audit.format: OSCAL` |
| Audit & Accountability | AU-9 | `audit.pii_in_logs: false` |
| Audit & Accountability | AU-12 | `audit.evidence_export: true` |
| Config Management | CM-2 | Policy `version` field + Git history |
| Config Management | CM-6 | Policy as code in version control |
| Config Management | CM-9 | `status: ACTIVE/DRAFT/DEPRECATED` |
| Identification & Auth | IA-2 | `require_user_auth: true` + OpenID.ai |
| Identification & Auth | IA-3 | Agent identity via OpenID.ai |
| System Integrity | SI-3 | `input_controls.detect: [prompt_injection, jailbreak]` |
| System Integrity | SI-10 | `input_controls.sanitize` |
| System & Comm. Protection | SC-7 | `allow_external_calls: false` |
| System & Comm. Protection | SC-8 | `audit.format: OSCAL` (transmission integrity) |

**Recommended minimum policy for FedRAMP Moderate:**

```yaml
input_controls:
  detect: [prompt_injection, jailbreak, context_stuffing]
  sanitize: [pii, credentials]
  require_user_auth: true

model_controls:
  trust_level: LOW
  allow_code_execution: false
  allow_external_calls: false

output_controls:
  block: [PII, credentials, SSN]
  hallucination_threshold: 0.10

audit:
  log_level: FULL
  format: OSCAL
  retention_days: 365
  compliance: [FedRAMP-Moderate, NIST-AI-RMF]
  pii_in_logs: false
  evidence_export: true

enforcement:
  on_violation: BLOCK
  fallback: DENY
```

### FedRAMP High Baseline

For systems handling national security information. Adds:
- `trust_level: UNTRUSTED` as default
- `log_level: FULL` mandatory
- `retention_days: 3650` (10 years)
- `hallucination_threshold: 0.05` or lower
- `require_human_in_loop` for all consequential actions

---

## 3. HIPAA

HIPAA Technical Safeguards (45 CFR Part 164, Subpart C) apply to systems handling Protected Health Information (PHI).

| Safeguard | 45 CFR Reference | Required Standard | OpenGPL Control |
|---|---|---|---|
| Access Control | 164.312(a)(1) | Unique user ID | `require_user_auth: true` + OpenID.ai |
| Access Control | 164.312(a)(1) | Automatic logoff | `applies_to.effective_until` (session scope) |
| Access Control | 164.312(a)(1) | Encryption/decryption | Handled by OpenLSP transport layer |
| Audit Controls | 164.312(b) | Activity logging | `log_level: FULL`, `format: OSCAL` |
| Integrity | 164.312(c)(1) | PHI alteration protection | `output_controls.block: [PHI]` |
| Integrity | 164.312(c)(2) | Transmission integrity | `allow_external_calls: false` |
| Person Auth | 164.312(d) | Verify identity | `require_user_auth: true` |
| Transmission Security | 164.312(e)(1) | Guard against unauthorized access | `allow_external_calls: false` |

**Required fields for HIPAA compliance:**

```yaml
output_controls:
  block: [PHI, SSN, date_of_birth, biometric]

audit:
  log_level: FULL
  format: OSCAL
  retention_days: 2555   # 7 years required by 45 CFR 164.530(j)
  compliance: [HIPAA]
  pii_in_logs: false
  evidence_export: true

enforcement:
  on_violation: BLOCK
  fallback: DENY
```

---

## 4. EU AI Act

The EU AI Act (Regulation (EU) 2024/1689) applies different requirements based on AI system risk level.

### High-Risk AI Systems (Annex III)

For AI systems in high-risk categories (healthcare, education, employment, law enforcement, etc.):

| Article | Requirement | OpenGPL Control |
|---|---|---|
| Art. 9 — Risk management | Ongoing risk monitoring | `audit.alert_on_violation: true` |
| Art. 10 — Data governance | Input data quality and bias | `input_controls.sanitize` |
| Art. 11 — Technical documentation | System documentation | Policy document serves as technical doc |
| Art. 12 — Record-keeping | Automatic logging | `audit.log_level: FULL` |
| Art. 13 — Transparency | Informing users | `output_controls.require: [disclaimer]` |
| Art. 13 — Transparency | Source attribution | `output_controls.require: [source_attribution]` |
| Art. 14 — Human oversight | Human review mechanisms | `model_controls.require_human_in_loop` |
| Art. 15 — Accuracy | Performance metrics | `output_controls.hallucination_threshold` |
| Art. 15 — Robustness | Resilience to errors | `enforcement.fallback: DENY` |

**Recommended policy additions for EU AI Act compliance:**

```yaml
output_controls:
  require:
    - disclaimer
    - source_attribution
    - confidence_score
  hallucination_threshold: 0.10

model_controls:
  require_human_in_loop:
    - consequential_decision
    - user_rights_impact

audit:
  compliance: [EU-AI-Act]
  log_level: FULL
  evidence_export: true
```

---

## 5. SOC 2

SOC 2 Trust Service Criteria (TSC) relevant to AI systems:

| TSC | Criteria | OpenGPL Control |
|---|---|---|
| CC6.1 | Logical access security | `trust_level`, `require_user_auth` |
| CC6.2 | Authentication | `require_user_auth: true` + OpenID.ai |
| CC6.3 | Access removal | `applies_to.effective_until` |
| CC6.7 — Common Criteria | Transmission protection | `allow_external_calls: false` |
| CC7.1 | System monitoring | `audit.log_level`, `alert_on_violation` |
| CC7.2 | Anomaly detection | `input_controls.detect` |
| CC7.3 | Incident response | `audit.alert_channels` |
| A1.1 — Availability | Processing commitments | `enforcement.fallback` |
| C1.1 — Confidentiality | Confidential information | `output_controls.block`, `redact` |
| P3.1 — Privacy | Data collection limitation | `input_controls.sanitize` |
| P4.1 — Privacy | Data use limitation | `output_controls.deny_topics` |

---

## 6. ISO/IEC 42001

ISO 42001 (AI Management System) partial mapping (full mapping available in OpenGPL v0.2):

| Clause | Requirement | OpenGPL Control |
|---|---|---|
| 6.1 — Risk assessment | AI risk identification | `input_controls.detect` |
| 8.4 — AI system impact | Impact documentation | Policy `description`, `metadata` |
| 9.1 — Monitoring | Performance monitoring | `audit.log_level`, `evidence_export` |
| 10.1 — Improvement | Corrective actions | `metadata.review_cycle` |

---

## 7. India DPDPA

India Digital Personal Data Protection Act, 2023 — partial mapping:

| Section | Requirement | OpenGPL Control |
|---|---|---|
| Sec. 4 — Lawful processing | Purpose limitation | `applies_to.contexts` |
| Sec. 6 — Consent | User consent verification | `require_user_auth: true` |
| Sec. 8 — Data accuracy | Output accuracy | `hallucination_threshold` |
| Sec. 9 — Data retention | Retention limits | `audit.retention_days` |
| Sec. 11 — Access rights | Audit trail for access | `audit.log_level: FULL` |

```yaml
audit:
  compliance: [DPDPA]
  retention_days: 365
  pii_in_logs: false

output_controls:
  block: [PII]
  redact: [phone_number, email_address]
```

---

## 8. OSCAL Evidence Generation

When `audit.format: OSCAL` and `audit.evidence_export: true` are set, OpenLSP automatically generates OSCAL-compatible artifacts that can be consumed by ControlGate / OpenCIQ for compliance assembly.

### Generated Artifacts

| OSCAL Document | Generated When | Contents |
|---|---|---|
| Component Definition | Policy is loaded | Policy controls mapped to NIST 800-53 components |
| System Security Plan | On first evaluation | Authorization boundary, control implementation statements |
| Assessment Results | On violation or alert | Findings, observations, risk entries |
| POA&M | On BLOCK/DENY violation | Plan of Action and Milestones entries |

### OSCAL Component Definition Example

OpenLSP auto-generates the following OSCAL component for each active policy:

```json
{
  "component-definition": {
    "uuid": "<auto-generated>",
    "metadata": {
      "title": "OpenGPL Policy: healthcare-customer-service",
      "version": "2.1.0"
    },
    "components": [{
      "type": "software",
      "title": "Patient Portal AI Agent",
      "implemented-requirements": [
        {
          "control-id": "ac-2",
          "description": "OpenGPL trust_level: LOW with require_user_auth enforced via OpenID.ai"
        },
        {
          "control-id": "au-2",
          "description": "OpenGPL audit.log_level: FULL with OSCAL format output"
        }
      ]
    }]
  }
}
```

---

*For questions or contributions, see [CONTRIBUTING.md](../CONTRIBUTING.md) or open a [GitHub Discussion](https://github.com/sadayamuthu/opengpl/discussions).*
