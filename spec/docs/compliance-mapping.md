# OpenGPL Compliance Mapping Reference

This document provides detailed mapping between OpenGPL policy controls and major compliance frameworks. Use this reference when designing policies for regulated environments.

**Maintained by OpenAstra — [openastra.org/opengpl](https://openastra.org/opengpl)**

---

## Table of Contents

- [How to read the mapping tables](#how-to-read-the-mapping-tables)

1. [NIST AI Risk Management Framework](#1-nist-ai-risk-management-framework)
2. [FedRAMP (Low / Moderate / High)](#2-fedramp)
3. [HIPAA Technical Safeguards](#3-hipaa)
4. [EU AI Act](#4-eu-ai-act)
5. [SOC 2 Trust Service Criteria](#5-soc-2)
6. [ISO/IEC 42001](#6-isoiec-42001)
7. [India DPDPA](#7-india-dpdpa)
8. [OSCAL Evidence Generation](#8-oscal-evidence-generation)

---

## How to read the mapping tables

The tables for NIST AI RMF, FedRAMP (SP 800-53), HIPAA, the EU AI Act and SOC 2 are generated from the mapping data that the reference SDK uses to build OSCAL output (`sdk/src/opengpl/compliance/mappings/`). Do not edit them by hand; run `python spec/scripts/gen_compliance_mapping.py`.

- A row exists only where a policy field supports that specific requirement. Requirements met by the policy document as a whole, or by practice outside the policy, are not listed.
- **Condition** is what the field must hold for the row to apply. A control is reported for a policy only if the condition holds.
- **Reference SDK status** is what `opengpl-sdk` does with the field: `enforced` (the SDK implements it), `heuristic` (the SDK implements it with pattern-based detection) or `declared` (the policy states it and the SDK does not enforce it). The column shows the weakest status the row can carry first, then any stronger status and the values that earn it; for example, "declared; heuristic for `prompt_injection`, `jailbreak`" means those two values are heuristic and every other value is declared. In OSCAL output the status is computed from the values the policy actually sets. Another runtime may do more.
- A row supports part of a requirement. It is evidence for an assessor, not an assessment result.

---

## 1. NIST AI Risk Management Framework

The NIST AI RMF (NIST AI 100-1) organizes AI governance into four core functions: GOVERN, MAP, MEASURE, and MANAGE.

Subcategory IDs are from NIST AI 100-1, Tables 1–4.

<!-- BEGIN GENERATED:NIST-AI-RMF -->
<!-- Generated from sdk/src/opengpl/compliance/mappings/nist-ai-rmf.yaml by spec/scripts/gen_compliance_mapping.py. Do not edit by hand. -->
| Control | Policy field | Condition | Reference SDK status | Rationale |
|---|---|---|---|---|
| `GOVERN 1.5` | `metadata.review_cycle` | set | declared | GOVERN 1.5 asks that periodic review be planned, 'including determining the frequency of periodic review'; the field records that frequency for this policy only. Policy declaration; the SDK does not schedule or track reviews. |
| `MAP 1.5` | `output_controls.hallucination_threshold` | set | declared | MAP 1.5 (risk tolerances are determined and documented): the field documents a quantified tolerance for one risk, hallucination. Policy declaration; it is not an organization-wide tolerance and the SDK does not score hallucination. |
| `MAP 3.5` | `model_controls.require_human_in_loop` | set | declared | MAP 3.5 (processes for human oversight are defined and documented): the field defines when human approval is required. Policy declaration; the reference SDK does not pause for approval. |
| `MEASURE 2.4` | `audit.log_level` | one of `STANDARD`, `FULL`, `DEBUG` | enforced | MEASURE 2.4 (functionality and behavior of the AI system and its components are monitored in production): gate decision records capture what the input and output gates allowed or blocked. |
| `MANAGE 1.3` | `input_controls.detect` | includes any of `prompt_injection`, `jailbreak`, `context_stuffing`, `role_confusion`, `data_exfiltration`, `adversarial_elicitation` | declared; heuristic for `prompt_injection`, `jailbreak` | MANAGE 1.3 (responses to high-priority AI risks are developed, planned and documented; options include mitigating): the field declares detection of named input attacks and documents the planned response (enforcement.on_detection). It does not perform the prioritization itself (MANAGE 1.2). |
| `MANAGE 4.3` | `audit.alert_on_violation` | `true` | declared | MANAGE 4.3 (incidents and errors are communicated to relevant AI actors): violation alerts communicate one class of incident. Policy declaration; the SDK does not send alerts or track incidents. |
<!-- END GENERATED:NIST-AI-RMF -->

---

## 2. FedRAMP

### FedRAMP Low Baseline

An example policy for a low-impact system. The mapping below applies to Low, Moderate and High alike.

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

The same SP 800-53 Rev 5 mapping is used for FedRAMP Low, Moderate and High. In OSCAL output, mapped controls that are not in the selected baseline are omitted with a notice (for example, `si-15` is not in the Moderate baseline).

<!-- BEGIN GENERATED:FedRAMP-Moderate -->
<!-- Generated from sdk/src/opengpl/compliance/mappings/sp800-53r5.yaml by spec/scripts/gen_compliance_mapping.py. Do not edit by hand. -->
| Control | Policy field | Condition | Reference SDK status | Rationale |
|---|---|---|---|---|
| `ac-3` | `model_controls.allow_tools` | set | declared | AC-3 access enforcement: the tool allow-list is an approved authorization for the model's access to tools (system resources). |
| `ac-3` | `model_controls.deny_tools` | set | declared | AC-3 access enforcement: the tool deny-list withholds authorization for specific tools. |
| `ac-4` | `model_controls.allow_external_calls` | `false` | declared | AC-4 information flow enforcement: restricts flow of information from the system to connected external systems. |
| `au-2` | `audit.log_level` | one of `STANDARD`, `FULL`, `DEBUG` | enforced | AU-2 event logging (item a/c): gate decisions are the event type the system is capable of logging and logs. |
| `au-3` | `audit.log_level` | one of `STANDARD`, `FULL`, `DEBUG` | enforced | AU-3 content of audit records: decision records establish what occurred, when and the outcome. |
| `au-11` | `audit.retention_days` | set | declared | AU-11 audit record retention: states the period for which audit records are to be retained. |
| `au-12` | `audit.log_level` | one of `STANDARD`, `FULL`, `DEBUG` | enforced | AU-12 audit record generation (item c): generates records for the logged event types with the AU-3 content. |
| `ia-2` | `input_controls.require_user_auth` | `true` | declared | IA-2 identification and authentication of organizational users: declaration only; the policy states that requests must come from authenticated users, and authentication is performed outside the SDK. |
| `sc-7` | `model_controls.allow_external_calls` | `false` | declared | SC-7 boundary protection (item a): policy declaration restricting communications at the system's external interface; it does not implement managed interfaces or boundary devices (item c). |
| `si-4` | `audit.alert_on_violation` | `true` | declared | SI-4 system monitoring (item g): policy declaration that monitoring information (violation alerts) is provided to personnel; it does not implement detection (item a). |
| `si-10` | `input_controls.detect` | includes any of `prompt_injection`, `jailbreak`, `context_stuffing`, `data_exfiltration` | declared; heuristic for `prompt_injection`, `jailbreak` | SI-10 input validation: checks the validity of prompts (information inputs) against the listed attack classes. |
| `si-15` | `output_controls.block` | set | declared; heuristic for `SSN`, `PHI`, `credit_card`, `credentials` | SI-15 information output filtering: for categories the runtime recognises, model output is checked and responses containing them are blocked (the reference SDK recognises SSN, PHI, credit_card and credentials by pattern; other categories are declarations). |
<!-- END GENERATED:FedRAMP-Moderate -->

**Example policy for FedRAMP Moderate.** The mapping above relies only on `input_controls.detect`, `input_controls.require_user_auth`, `model_controls.allow_tools`, `model_controls.deny_tools`, `model_controls.allow_external_calls`, `output_controls.block`, and `audit.log_level`, `audit.retention_days` and `audit.alert_on_violation`. The other fields in the example are not mapped to any SP 800-53 control:

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

An example of stricter settings. Of the fields below, only `log_level` and `retention_days` are mapped to SP 800-53 controls (`au-2`, `au-3`, `au-11`, `au-12`). The others do not change the OSCAL output:

- `trust_level: UNTRUSTED` as default
- `log_level: FULL` mandatory
- `retention_days: 3650` (10 years)
- `hallucination_threshold: 0.05` or lower
- `require_human_in_loop` for all consequential actions

---

## 3. HIPAA

HIPAA Technical Safeguards (45 CFR 164.312, in Part 164, Subpart C) apply to systems handling Protected Health Information (PHI).

<!-- BEGIN GENERATED:HIPAA -->
<!-- Generated from sdk/src/opengpl/compliance/mappings/hipaa.yaml by spec/scripts/gen_compliance_mapping.py. Do not edit by hand. -->
| Control | Policy field | Condition | Reference SDK status | Rationale |
|---|---|---|---|---|
| `164.312(b)` | `audit.log_level` | one of `STANDARD`, `FULL`, `DEBUG` | enforced | 164.312(b) audit controls: a software mechanism that records activity in a system that uses ePHI. It covers recording only; examining the records is not implemented. |
| `164.312(d)` | `input_controls.require_user_auth` | `true` | declared | 164.312(d) person or entity authentication: requires that the identity of the person making a request be verified. Policy declaration; verification is done by the deployment's identity provider, not the SDK. |
<!-- END GENERATED:HIPAA -->

**Fields that the mapping above relies on:**

```yaml
input_controls:
  require_user_auth: true   # 164.312(d), declared

audit:
  log_level: FULL           # 164.312(b), enforced (STANDARD and DEBUG also qualify)
  compliance: [HIPAA]
```

`output_controls.block` is not mapped to a HIPAA control. HIPAA has no OSCAL output; the table is a mapping only.

---

## 4. EU AI Act

The EU AI Act (Regulation (EU) 2024/1689) applies different requirements based on AI system risk level.

### High-Risk AI Systems (Annex III)

Requirements for high-risk AI systems are in Chapter III, Section 2 (Articles 9–15). Control IDs are `art-<article>.<paragraph>`. Article 9 (risk management system), Article 10 (data and data governance, which concerns training, validation and testing data) and Article 11 (technical documentation) have no policy field that implements them and are not mapped.

<!-- BEGIN GENERATED:EU-AI-Act -->
<!-- Generated from sdk/src/opengpl/compliance/mappings/eu-ai-act.yaml by spec/scripts/gen_compliance_mapping.py. Do not edit by hand. -->
| Control | Policy field | Condition | Reference SDK status | Rationale |
|---|---|---|---|---|
| `art-12.1` | `audit.log_level` | one of `STANDARD`, `FULL`, `DEBUG` | enforced | Art. 12(1) requires that the system technically allow automatic recording of events (logs); the runtime writes gate decision records. It does not by itself meet the Art. 12(3) minimum content for Annex III point 1(a) systems. |
| `art-13.1` | `output_controls.require` | includes any of `source_attribution`, `confidence_score` | declared | Art. 13(1) (operation sufficiently transparent to enable deployers to interpret the output): cited sources or a confidence indicator help interpret each output. Policy declaration; the SDK does not check responses for them. Instructions for use (Art. 13(2)-(3)) are not covered. |
| `art-14.4` | `model_controls.require_human_in_loop` | set | declared | Art. 14(4)(d): enables the overseer to decide not to use, or to disregard or override, the output in a given situation. Policy declaration; the reference SDK does not pause for approval. |
| `art-15.1` | `output_controls.hallucination_threshold` | set | declared | Art. 15(1) (an appropriate level of accuracy): the field declares an accuracy criterion. It does not establish that the level is appropriate, nor measure it; the SDK does not score hallucination, and Art. 15(3) declaration in the instructions for use is not covered. |
| `art-15.4` | `enforcement.fallback` | one of `DENY`, `BLOCK` | declared | Art. 15(4), second subparagraph: robustness may be achieved through 'backup or fail-safe plans'; failing closed on an enforcement fault is such a plan. Policy declaration; the SDK does not implement the fallback. |
| `art-15.5` | `input_controls.detect` | includes any of `prompt_injection`, `jailbreak`, `context_stuffing`, `role_confusion`, `data_exfiltration`, `adversarial_elicitation` | declared; heuristic for `prompt_injection`, `jailbreak` | Art. 15(5), third subparagraph: measures to detect and respond to inputs designed to make the model err (adversarial examples, model evasion) and to confidentiality attacks. Data and model poisoning are not covered. |
<!-- END GENERATED:EU-AI-Act -->

**Fields that the mapping above relies on:**

```yaml
input_controls:
  detect: [prompt_injection, jailbreak]

output_controls:
  require:
    - source_attribution
    - confidence_score
  hallucination_threshold: 0.10

model_controls:
  require_human_in_loop:
    - consequential_decision

enforcement:
  fallback: DENY

audit:
  compliance: [EU-AI-Act]
  log_level: FULL
```

`disclaimer` is not mapped to any article. EU AI Act has no OSCAL output; the table is a mapping only.

---

## 5. SOC 2

AICPA 2017 Trust Services Criteria (TSP Section 100), common criteria relevant to AI systems:

<!-- BEGIN GENERATED:SOC2 -->
<!-- Generated from sdk/src/opengpl/compliance/mappings/soc2.yaml by spec/scripts/gen_compliance_mapping.py. Do not edit by hand. -->
| Control | Policy field | Condition | Reference SDK status | Rationale |
|---|---|---|---|---|
| `CC6.1` | `input_controls.require_user_auth` | `true` | declared | CC6.1 logical access security (point of focus 'Identifies and Authenticates Users'): users are authenticated before access. Policy declaration; authentication is done by the deployment's identity provider. |
| `CC6.1` | `model_controls.allow_tools` | set | declared | CC6.1 logical access security (point of focus 'Restricts Logical Access' through access control rule sets): the allow-list is a rule set for the model's access to software. Policy declaration; the reference SDK does not check tool calls. |
| `CC6.1` | `model_controls.deny_tools` | set | declared | CC6.1 logical access security (point of focus 'Restricts Logical Access'): the deny-list withholds the model's access to named software. Policy declaration; the reference SDK does not check tool calls. |
| `CC6.7` | `model_controls.allow_external_calls` | `false` | declared | CC6.7 (restricts the transmission of information to authorized external users and processes): forbids the model from transmitting to external APIs or URLs. Policy declaration; it does not protect data in transit. |
| `CC6.7` | `output_controls.block` | set | declared; heuristic for `SSN`, `PHI`, `credit_card`, `credentials` | CC6.7 point of focus 'Restricts the Ability to Perform Transmission' (data loss prevention): for categories the runtime recognises, responses containing them are blocked before delivery (the reference SDK recognises SSN, PHI, credit_card and credentials by pattern; other categories are declarations). |
| `CC7.2` | `input_controls.detect` | includes any of `prompt_injection`, `jailbreak`, `context_stuffing`, `role_confusion`, `data_exfiltration`, `adversarial_elicitation` | declared; heuristic for `prompt_injection`, `jailbreak` | CC7.2 (monitors system components for anomalies indicative of malicious acts; point of focus 'Implements Detection Policies, Procedures, and Tools'): input detectors flag attack attempts, for the classes the runtime detects. It does not cover analysis into security events. |
<!-- END GENERATED:SOC2 -->

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

`opengpl audit` writes OSCAL 1.2.3 documents for `FedRAMP-Low`, `FedRAMP-Moderate` and `FedRAMP-High`. NIST AI RMF, EU AI Act, HIPAA and SOC 2 have the mapping tables above and no OSCAL output.

### Generated Artifacts

| OSCAL Document | Written when | Contents |
|---|---|---|
| Component Definition | `opengpl audit <policy> --framework <F>` | One implemented requirement per NIST SP 800-53 Rev 5 control that the policy's set fields map to, each naming those fields |
| Assessment Results | The same command with `--decisions <log>` | Observations built from the decision log. No findings and no risks; `import-ap` points to a back-matter resource that states no assessment plan exists |

The SDK does not generate a system security plan or a POA&M.

### Implementation status

Each implemented requirement carries an `implementation-status` property in the namespace `https://opengpl.org/ns/oscal`: `enforced`, `heuristic` or `declared`, as defined in [How to read the mapping tables](#how-to-read-the-mapping-tables). When several fields contribute to a control, it carries the weakest of their statuses (`declared` < `heuristic` < `enforced`). A control appears only if the policy sets a field that maps to it.

### Baseline source

Controls are checked against the SP 800-53 Rev 5 Low, Moderate and High baseline profiles that NIST publishes in [`usnistgov/oscal-content`](https://github.com/usnistgov/oscal-content), pinned to tag `v1.6.0`. They are NIST's baselines, not FedRAMP's own. A mapped control that is not in the selected baseline is omitted, and the CLI names it.

### Decision log

The assessment results come from the JSONL decision log (`PolicyEngine(path, decision_log=...)`, or `OPENGPL_DECISION_LOG` for the sidecar). A record stores the rule IDs evaluated and fired, not controls; controls are derived at audit time, so one log can be audited against different frameworks. Under `audit.log_level` FULL or DEBUG, the record holds the text, redacted unless `audit.pii_in_logs` is `true`; if redaction fails, the text is omitted and the record carries `"text_redaction": "failed"`. Otherwise only a SHA-256 of the text is stored. Under `audit.log_level` OFF, no record is written.

### Component Definition Example

An excerpt of the output for `spec/examples/fedramp-moderate.gpl` with `--framework FedRAMP-Moderate`:

```json
{
  "component-definition": {
    "metadata": { "oscal-version": "1.2.3" },
    "components": [{
      "type": "software",
      "control-implementations": [{
        "source": "https://raw.githubusercontent.com/usnistgov/oscal-content/v1.6.0/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_MODERATE-baseline_profile.json",
        "implemented-requirements": [{
          "control-id": "au-2",
          "description": "audit.log_level is FULL; the runtime writes a decision record for every gate evaluation to the configured decision log.",
          "props": [
            { "name": "implementation-status", "ns": "https://opengpl.org/ns/oscal", "value": "enforced" },
            { "name": "policy-field", "ns": "https://opengpl.org/ns/oscal", "value": "audit.log_level=FULL" }
          ]
        }]
      }]
    }]
  }
}
```

The output lists mappings from policy fields to controls. It is evidence for an assessor, not an assessment, and it does not state that any control is met.

---

*For questions or contributions, see [CONTRIBUTING.md](../CONTRIBUTING.md) or open a [GitHub Discussion](https://github.com/sadayamuthu/opengpl/discussions).*
