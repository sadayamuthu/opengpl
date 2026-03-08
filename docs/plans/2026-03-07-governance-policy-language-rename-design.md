# Design: Rename "Generative Policy Language" to "Governance Policy Language"

**Date:** 2026-03-07
**Status:** Approved

## Summary

Replace all occurrences of the proper name "Generative Policy Language" with "Governance Policy Language" in documentation files. The acronym GPL and the project name OpenGPL remain unchanged.

## Scope

Only the proper name is updated. General references to "generative AI" as a technical term are not changed.

**Files affected:**

| File | Occurrences |
|---|---|
| `README.md` | 2 |
| `spec/SPEC.md` | 3 |

## Changes

| File | Line | Before | After |
|---|---|---|---|
| `README.md` | 7 | `## Generative Policy Language` | `## Governance Policy Language` |
| `README.md` | 28 | `OpenGPL (Generative Policy Language) is...` | `OpenGPL (Governance Policy Language) is...` |
| `spec/SPEC.md` | 3 | `Generative Policy Language — Full Technical Specification` | `Governance Policy Language — Full Technical Specification` |
| `spec/SPEC.md` | 9 | `OpenGPL — Generative Policy Language Specification` | `OpenGPL — Governance Policy Language Specification` |
| `spec/SPEC.md` | 39 | `OpenGPL (Generative Policy Language) is...` | `OpenGPL (Governance Policy Language) is...` |

## Out of Scope

- Package names (`opengpl`, `opengpl-sdk`) — unchanged
- Module paths (`src/opengpl/`) — unchanged
- File names (`opengpl-v0.1.yaml`, etc.) — unchanged
- General uses of "generative AI" as a technical descriptor — unchanged
