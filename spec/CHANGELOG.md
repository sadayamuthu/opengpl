# Changelog

All notable changes to the OpenGPL specification are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
OpenGPL uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2025-03-01

### Initial Public Draft

This is the first public draft of the OpenGPL specification, released for community review under the OpenAstra.

#### Added
- Core policy schema: `opengpl`, `policy`, `version`, `status`, `owner`, `description`
- `applies_to` block: model, agent, context, environment, and date scoping
- `input_controls` block: threat detection, data sanitization, token limits, auth requirements
- `model_controls` block: tool access, trust levels, human-in-loop triggers, execution controls
- `output_controls` block: data blocking, redaction, topic restrictions, hallucination thresholds
- `audit` block: log levels, OSCAL output format, retention, compliance declarations, alerting
- `enforcement` block: engine declaration, violation actions, fallback behavior
- Policy inheritance via `extends` field
- Trust level model (UNTRUSTED → LOW → MEDIUM → HIGH → SYSTEM)
- Violation action model (ALLOW → LOG → REDACT → ALERT → BLOCK → ESCALATE → DENY)
- Full compliance mappings: NIST AI RMF, FedRAMP Moderate, HIPAA, EU AI Act
- Integration reference: OpenLSP SDK, LangChain, API gateway, OpenID.ai, ControlGate
- Appendices: threat categories, data classifications, compliance identifiers

---

## Upcoming

### [0.2.0] — Q3 2025 (Planned)
- Training-time policy hooks
- Multi-tenant policy stores
- Policy testing framework (`opengpl test`)
- ISO 42001 and DPDPA compliance mappings
- Extended `model_routing` schema

### [0.3.0] — Q1 2026 (Planned)
- Multi-modal content policy (image, audio)
- Attribution tracking and provenance chains
- Agent-to-agent trust delegation

### [1.0.0] — Q3 2026 (Planned)
- Stable specification
- NIST NCCoE submission
- Formal certification program launch
