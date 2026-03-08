# Governance Policy Language Rename Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace all 5 occurrences of "Generative Policy Language" with "Governance Policy Language" in README.md and spec/SPEC.md.

**Architecture:** Pure text substitution in two documentation files. No code changes, no package renames, no file renames. The acronym GPL and project name OpenGPL are unaffected.

**Tech Stack:** None — text editing only.

---

### Task 1: Update README.md

**Files:**
- Modify: `README.md:7` and `README.md:28`

**Step 1: Make the replacements**

In `README.md`, replace both occurrences:

- Line 7: `## Generative Policy Language` → `## Governance Policy Language`
- Line 28: `OpenGPL (Generative Policy Language) is` → `OpenGPL (Governance Policy Language) is`

**Step 2: Verify**

Run:
```bash
grep "Generative Policy Language" README.md
```
Expected: no output (zero matches)

Run:
```bash
grep "Governance Policy Language" README.md
```
Expected: 2 matches

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: rename Generative Policy Language to Governance Policy Language in README"
```

---

### Task 2: Update spec/SPEC.md

**Files:**
- Modify: `spec/SPEC.md:3`, `spec/SPEC.md:9`, `spec/SPEC.md:39`

**Step 1: Make the replacements**

In `spec/SPEC.md`, replace all three occurrences:

- Line 3: `Generative Policy Language — Full Technical Specification` → `Governance Policy Language — Full Technical Specification`
- Line 9: `OpenGPL — Generative Policy Language Specification` → `OpenGPL — Governance Policy Language Specification`
- Line 39: `OpenGPL (Generative Policy Language) is` → `OpenGPL (Governance Policy Language) is`

**Step 2: Verify**

Run:
```bash
grep "Generative Policy Language" spec/SPEC.md
```
Expected: no output (zero matches)

Run:
```bash
grep "Governance Policy Language" spec/SPEC.md
```
Expected: 3 matches

**Step 3: Commit**

```bash
git add spec/SPEC.md
git commit -m "docs: rename Generative Policy Language to Governance Policy Language in SPEC"
```

---

### Task 3: Final verification

**Step 1: Confirm no remaining occurrences**

Run:
```bash
grep -ri "Generative Policy Language" . --exclude-dir=".venv" --exclude-dir=".git" --exclude-dir="docs/plans"
```
Expected: no output

**Step 2: Confirm all replacements landed**

Run:
```bash
grep -ri "Governance Policy Language" . --exclude-dir=".venv" --exclude-dir=".git"
```
Expected: 5 matches across README.md and spec/SPEC.md
