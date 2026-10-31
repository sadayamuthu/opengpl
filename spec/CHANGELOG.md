# Changelog

All notable changes to the OpenGPL specification are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
OpenGPL uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.1] — 2026-10-31

### Changed (editorial, no schema changes)

- `enforcement.engine` default and examples now name the reference implementation `opengpl-sdk` (was `OpenLSP`)
- Identity and compliance-tool integrations described generically (any OIDC provider, any OSCAL-aware tool) rather than by product
- Integration guide rewritten against the real `opengpl-sdk` API; planned features marked as planned
- Enforcement-model performance figures labelled as design targets
- Removed a non-normative note about OPA's maintainers
- Corrected publication dates to 2026

## [0.1.0] — 2026-03-08

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
- Integration reference: `opengpl-sdk` reference implementation, framework patterns, HTTP sidecar, identity and OSCAL tooling
- Appendices: threat categories, data classifications, compliance identifiers

---

## Upcoming

### [0.2.0] — In design

- Principals, entitlements and delegation chains (`human → agent → agent → tool → resource`)
- Governance blocks: inventory, usage vs. grant, access reviews with OSCAL evidence
- Gateway integration via Envoy `ext_authz` and OpenID AuthZEN, starting with agentgateway
- Policy testing framework (`opengpl test`)
- ISO 42001 and DPDPA compliance mappings

### [0.3.0] — Q1 2026 (Planned)

- Multi-modal content policy (image, audio)
- Attribution tracking and provenance chains
- Agent-to-agent trust delegation

### [1.0.0] — Q3 2026 (Planned)

- Stable specification
- NIST NCCoE submission
- Formal certification program launch
