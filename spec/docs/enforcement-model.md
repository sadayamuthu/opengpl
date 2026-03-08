# OpenGPL Enforcement Model

This document describes how OpenGPL policies are evaluated and enforced at runtime by the OpenLSP enforcement engine.

**Maintained by OpenAstra — [openastra.org/opengpl](https://openastra.org/opengpl)**

---

## Overview

OpenGPL enforcement follows the **Policy Decision Point / Policy Enforcement Point (PDP/PEP)** model, adapted for the generative AI context. Unlike deterministic systems where policies evaluate known inputs against fixed rules, OpenGPL must handle:

- **Probabilistic outputs** — LLM responses are stochastic
- **Semantic violations** — violations may be implied rather than explicit
- **Multi-step tool calls** — each tool invocation is an independent enforcement point
- **Context-dependent risk** — the same text may be acceptable in one context and a violation in another

---

## Architecture

```
  ┌─────────────────────────────────────────────────────────────┐
  │                     OpenLSP Gateway                         │
  │                                                             │
  │  User/Agent Request                                         │
  │         │                                                   │
  │         ▼                                                   │
  │  ┌─────────────────┐    ┌──────────────────────────────┐   │
  │  │  PEP: Input     │───▶│  PDP: OpenGPL Policy Engine  │   │
  │  │  Gate           │    │                              │   │
  │  │  • detect       │    │  • Loads applicable policy   │   │
  │  │  • sanitize     │    │  • Resolves inheritance      │   │
  │  │  • token limits │    │  • Determines trust level    │   │
  │  └─────────────────┘    │  • Evaluates control blocks  │   │
  │                         └──────────────┬───────────────┘   │
  │                                        │ Decision           │
  │                                        ▼                   │
  │  ┌─────────────────┐    ┌─────────────────────────────┐   │
  │  │  LLM Provider   │◀───│  Enforcement Action          │   │
  │  │  (any model)    │    │  ALLOW / LOG / BLOCK / etc.  │   │
  │  └────────┬────────┘    └─────────────────────────────┘   │
  │           │                                                 │
  │           ▼  (per tool call)                                │
  │  ┌─────────────────┐                                       │
  │  │  Tool Call PEP  │  ← model_controls evaluated per-call  │
  │  └────────┬────────┘                                       │
  │           │                                                 │
  │           ▼                                                 │
  │  ┌─────────────────┐                                       │
  │  │  PEP: Output    │  ← output_controls evaluated          │
  │  │  Gate           │  ← redaction applied                  │
  │  └────────┬────────┘                                       │
  │           │                                                 │
  │           ▼                                                 │
  │  ┌─────────────────┐                                       │
  │  │  Audit Ledger   │  ← OSCAL artifacts assembled          │
  │  └────────┬────────┘  ← alerts dispatched                  │
  │           │                                                 │
  │           ▼                                                 │
  │     Final Response                                          │
  └─────────────────────────────────────────────────────────────┘
```

---

## Evaluation Order

When a request is received, controls are applied in strict sequence:

### Step 1 — Policy Resolution
- Identify which policy applies based on `applies_to` (model, agent, context, environment)
- If `extends` is set, merge child policy over parent
- Validate policy status (`ACTIVE` only — `DRAFT`/`DEPRECATED` policies are not enforced)
- Check `effective_from` and `effective_until` date bounds

### Step 2 — Trust Level Assignment
- Determine trust level from `model_controls.trust_level`
- If OpenID.ai is integrated, trust level may be elevated based on verified identity
- Trust level affects default permissiveness of subsequent evaluations

### Step 3 — Input Gate (input_controls)
- Run threat detection (`detect` categories)
- Apply data sanitization (`sanitize` categories)
- Enforce token limits (`max_context_tokens`, `max_prompt_tokens`)
- Validate user authentication if `require_user_auth: true`
- Apply language filter if `language_filter` is set

### Step 4 — Model Controls Validation (pre-dispatch)
- Validate that the requested model is in `applies_to.models`
- Apply `temperature_ceiling` to the request parameters
- Gate tool declarations against `allow_tools` / `deny_tools`

### Step 5 — Tool Call Evaluation (per-call, during execution)
- Each tool invocation is evaluated independently
- Tool name is matched against `allow_tools` and `deny_tools`
- `require_human_in_loop` conditions are evaluated for each tool call context
- `max_tool_calls` counter is incremented and checked

### Step 6 — Output Gate (output_controls)
- Scan generated response for blocked data categories (`block`)
- Apply redaction for `redact` categories
- Check for `deny_topics` in response content
- Validate `require` attributes are present
- Enforce `max_response_tokens`
- Evaluate `hallucination_threshold` if configured
- Apply `tone_enforcement` assessment
- Check for `deny_formats`

### Step 7 — Audit Record Generation
- Write evaluation record at configured `log_level`
- Generate OSCAL artifacts if `evidence_export: true`
- Dispatch alerts via `alert_channels` if violations occurred

### Step 8 — Violation Action Execution
- Apply `on_violation` or `on_detection` action as appropriate
- If engine unavailable, apply `fallback` action

---

## Violation Actions

| Action | Description | Request Processed | Alert Sent | Audit Written |
|---|---|---|---|---|
| `ALLOW` | Pass through, no modification | ✅ | ❌ | ❌ |
| `LOG` | Pass through, write audit record | ✅ | ❌ | ✅ |
| `REDACT` | Pass through, sensitive data replaced | ✅ (modified) | ❌ | ✅ |
| `ALERT` | Pass through, alert dispatched | ✅ | ✅ | ✅ |
| `BLOCK` | Return error, request not processed | ❌ | ✅ | ✅ |
| `ESCALATE` | Pause, route to human reviewer | ❌ (pending) | ✅ | ✅ |
| `DENY` | Hard rejection, no fallback | ❌ | ✅ | ✅ |

> **Rule:** `DENY` always overrides all other actions. When in doubt, fail closed.

---

## Conflict Resolution

When multiple policies could apply to the same request:

### 1. Specificity wins
A policy with more specific `applies_to` criteria takes precedence over a less specific one. Order of specificity (most to least):
- `agent` + `context` + `environment`
- `agent` + `context`
- `agent` only
- `context` + `environment`
- `context` only
- Wildcard (`models: ['*']`)

### 2. Inheritance
Child policies (via `extends`) override parent fields. The child is evaluated after the parent, and any field defined in the child replaces the parent's value entirely for that field.

### 3. Stricter wins (sibling conflict)
When two policies of equal specificity both apply, the stricter control is used:
- Lower `hallucination_threshold` wins
- `BLOCK` beats `LOG` beats `ALLOW`
- `DENY` beats everything, always
- Shorter token limits win
- `false` beats `true` for `allow_*` fields

### 4. DENY is absolute
If any applicable policy evaluates to `DENY`, the request is denied regardless of what any other policy says.

---

## Fail-Safe Behavior

The `enforcement.fallback` field defines what happens when OpenLSP is unavailable or fails to evaluate:

```yaml
enforcement:
  fallback: DENY    # Recommended for production
  # fallback: ALLOW  # Only for non-critical development
```

**Best practice:** Always set `fallback: DENY` in production. An unavailable enforcement engine should never silently permit requests.

---

## Hallucination Threshold

The `hallucination_threshold` field is a novel OpenGPL primitive with no equivalent in prior policy languages.

OpenLSP computes a hallucination risk score (0.0–1.0) for each response using a combination of:
- Factual consistency checks against retrieved context
- Confidence calibration signals from the model
- Self-consistency sampling across multiple passes

If the computed score exceeds the configured threshold, the `on_violation` action is triggered.

**Recommended thresholds by context:**

| Context | Threshold | Rationale |
|---|---|---|
| Legal / regulatory | 0.05 | Near-zero tolerance |
| Healthcare | 0.10 | Patient safety |
| Government / FedRAMP | 0.10 | Public trust |
| Financial | 0.15 | Fiduciary duty |
| Enterprise general | 0.20 | Balanced |
| Customer service | 0.25 | Conversational tolerance |
| Development / sandbox | 0.90 | Observability only |

---

## Performance Considerations

OpenLSP is designed for sub-50ms policy evaluation overhead on standard hardware. Key performance characteristics:

- Policy compilation is cached on load — no per-request compilation cost
- Input gate evaluation: ~5–15ms (detection + sanitization)
- Output gate evaluation: ~10–30ms (depends on response length and block categories)
- OSCAL artifact generation: async — does not block response delivery
- Alert dispatch: async — does not block response delivery

For high-throughput deployments, OpenLSP supports horizontal scaling with shared policy store.

---

*For questions or contributions, see [CONTRIBUTING.md](../CONTRIBUTING.md) or open a [GitHub Discussion](https://github.com/sadayamuthu/opengpl/discussions).*
