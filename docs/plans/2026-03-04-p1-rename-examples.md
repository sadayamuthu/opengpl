# Priority 1: Rename Examples to .gpl Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename all example `.yaml` files to `.gpl`, add `.gitattributes` for GitHub language detection, and update all references.

**Architecture:** Pure rename + config change in `sadayamuthu/opengpl`. No logic changes.

**Tech Stack:** Git, GitHub Actions (path filter update)

---

### Task 1: Rename example files

**Files:**
- Modify: `examples/minimal.yaml` → `examples/minimal.gpl`
- Modify: `examples/healthcare-hipaa.yaml` → `examples/healthcare-hipaa.gpl`
- Modify: `examples/fedramp-moderate.yaml` → `examples/fedramp-moderate.gpl`
- Modify: `examples/multi-agent.yaml` → `examples/multi-agent.gpl`
- Modify: `examples/dev-sandbox.yaml` → `examples/dev-sandbox.gpl`

**Step 1: Rename all files**

```bash
cd /Users/karthik/Downloads/opengpl
for f in examples/*.yaml; do git mv "$f" "${f%.yaml}.gpl"; done
```

**Step 2: Verify renames**

```bash
ls examples/
```

Expected output:
```
dev-sandbox.gpl  fedramp-moderate.gpl  healthcare-hipaa.gpl  minimal.gpl  multi-agent.gpl
```

**Step 3: Commit**

```bash
git add examples/
git commit -m "feat: rename example policies to .gpl extension"
```

---

### Task 2: Add .gitattributes

**Files:**
- Create: `.gitattributes`

**Step 1: Create the file**

```
# .gitattributes
*.gpl linguist-language=YAML
```

**Step 2: Verify**

```bash
cat .gitattributes
```

Expected: `*.gpl linguist-language=YAML`

**Step 3: Commit**

```bash
git add .gitattributes
git commit -m "chore: add .gitattributes for .gpl linguist detection"
```

---

### Task 3: Update validate.yml CI path filter

**Files:**
- Modify: `.github/workflows/validate.yml:5-6`

**Step 1: Read current path filter**

```bash
grep -n "yaml" .github/workflows/validate.yml
```

Expected: line with `examples/**/*.yaml`

**Step 2: Update the path filter**

In `.github/workflows/validate.yml`, change:
```yaml
      - 'examples/**/*.yaml'
```
to:
```yaml
      - 'examples/**/*.gpl'
```

**Step 3: Verify**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/validate.yml')); print('YAML valid')"
```

**Step 4: Commit**

```bash
git add .github/workflows/validate.yml
git commit -m "ci: update validate workflow path filter for .gpl files"
```

---

### Task 4: Update README and SPEC references

**Files:**
- Modify: `README.md`
- Modify: `SPEC.md`

**Step 1: Find all .yaml references in docs**

```bash
grep -rn "\.yaml" README.md SPEC.md docs/
```

**Step 2: Update README.md**

Replace all occurrences of `examples/*.yaml` and `examples/minimal.yaml`, `examples/healthcare-hipaa.yaml`, etc. with their `.gpl` equivalents.

Also update the repo tree in README.md that shows example filenames.

**Step 3: Update SPEC.md**

Replace any references to `.yaml` example files with `.gpl`.

**Step 4: Verify no stale .yaml example references remain**

```bash
grep -n "examples/.*\.yaml" README.md SPEC.md docs/
```

Expected: no output.

**Step 5: Commit**

```bash
git add README.md SPEC.md docs/
git commit -m "docs: update example file references from .yaml to .gpl"
```

---

### Task 5: Push

```bash
git push origin main
```
