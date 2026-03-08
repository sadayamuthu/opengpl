# OpenGPL Build Priorities Design

**Date:** 2026-03-04
**Status:** Approved

## Scope

Priorities 1, 2, 3, and 5 from CLAUDE_CODE_HANDOFF.md. Priority 4 (VS Code extension) deferred.

## Repo Structure

| Repo | Path | Contents |
|---|---|---|
| `sadayamuthu/opengpl` | `/Users/karthik/Downloads/opengpl` | Spec, schema, examples (existing) |
| `sadayamuthu/opengpl-runtime` | new repo | Python package + CLI + FastAPI validation API |
| `sadayamuthu/opengpl.org` | `/Users/karthik/git/opengpl.org` | GitHub Pages site (HTML/CSS/JS) |

---

## Priority 1 — Rename Examples to `.gpl`

**Repo:** `sadayamuthu/opengpl`

### Changes

1. Rename all `examples/*.yaml` → `examples/*.gpl`
2. Add `.gitattributes` at repo root: `*.gpl linguist-language=YAML`
3. Update `validate.yml` CI path filter: `examples/**/*.yaml` → `examples/**/*.gpl`
4. Update README and SPEC references from `examples/*.yaml` → `examples/*.gpl`

---

## Priority 2 — `opengpl-runtime` Python Package

**Repo:** `sadayamuthu/opengpl-runtime` (new)

### Package Structure

```
src/opengpl/
├── __init__.py
├── engine.py          # PolicyEngine — load + enforce a policy
├── loader.py          # Parse + validate .gpl files against JSON Schema
├── gates/
│   ├── input_gate.py  # input_controls evaluation
│   ├── model_gate.py  # model_controls evaluation
│   └── output_gate.py # output_controls evaluation
├── detectors/
│   ├── injection.py   # prompt_injection detection (heuristic)
│   ├── jailbreak.py   # jailbreak detection (heuristic)
│   └── pii.py         # PII detection + sanitization
├── audit/
│   ├── ledger.py      # structured audit log writer
│   └── oscal.py       # basic OSCAL artifact (stub — full = ControlGate)
└── api.py             # FastAPI app — POST /validate, GET /schema-versions
```

### Tech Stack

- Python 3.11+
- `pyyaml` — parse .gpl files
- `jsonschema` — validate against OpenGPL JSON Schema
- `fastapi` + `uvicorn` — validation API
- `presidio-analyzer` — PII detection
- `click` — CLI
- `pytest` — tests

### PyPI Package Name

`opengpl-runtime`

### Patent Boundary

Open source implements: detection + blocking only.
NOT open source (ControlGate only): full OSCAL assembly, dual-gate enforcement method, hallucination threshold as enforceable primitive, policy-as-evidence pipeline.

---

## Priority 3 — CLI

**Ships inside `opengpl-runtime`**, installed via `pip install opengpl-runtime`.

### Commands

```bash
opengpl validate policy.gpl
# ✓ Policy 'name' is valid (OpenGPL v0.1)
# ✗ 3 errors: field-level messages

opengpl eval policy.gpl --prompt "..." --context customer-service
# INPUT GATE: PASS | MODEL GATE: PASS | OUTPUT: [simulated] | AUDIT: logged

opengpl audit policy.gpl --framework FedRAMP-Moderate
# OSCAL artifact written to policy-audit.json
```

### Implementation

- Built with `click`
- Entry point: `opengpl = opengpl.cli:main` in `pyproject.toml`

---

## Priority 5 — opengpl.org Website

**Repo:** `sadayamuthu/opengpl.org`
**Local path:** `/Users/karthik/git/opengpl.org`
**Hosting:** GitHub Pages (existing)

### Pages

| Path | Content |
|---|---|
| `/` | Landing — what OpenGPL is, install command, links |
| `/docs` | Spec as readable HTML |
| `/schema` | Schema download + field reference |
| `/validate` | Interactive .gpl validator |

### `/validate` Page

- Textarea for .gpl content
- Dropdown: schema version selector (`v0.1`, etc.)
- Validate button → `POST https://api.opengpl.org/validate`
- Inline results: ✓ or ✗ with field-level errors

### Validation API (`api.opengpl.org`)

- Hosted on Railway or Render (free tier)
- Source: `api.py` in `opengpl-runtime`
- `POST /validate` — `{policy: string, version: string}` → `{valid: bool, errors: []}`
- `GET /schema-versions` — returns available versions
- CORS enabled for `opengpl.org`

### Tech Stack

Plain HTML/CSS/JS — no framework, no build step. Natively compatible with GitHub Pages.

---

## Build Order

1. Priority 1 (examples rename) — in `opengpl` repo, ~30 min
2. Priority 2 (runtime package) — new `opengpl-runtime` repo, biggest piece
3. Priority 3 (CLI) — part of `opengpl-runtime`, builds on engine
4. Priority 5 (website) — in `opengpl.org` repo, after API is deployed
