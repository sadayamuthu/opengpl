# GitHub Workflows Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix four confirmed bugs in the GitHub Actions workflows: missing permission, fragile Docker Hub condition, SDK version source mismatch, and unintended sidecar trigger.

**Architecture:** Each task is a targeted edit to one workflow file or file deletion. No new infrastructure, no new files. Changes are independent and can be reviewed separately. `pyproject.toml` becomes the sole source of truth for the SDK version.

**Tech Stack:** GitHub Actions YAML, Python 3.11 `tomllib` (stdlib), `dorny/paths-filter@v3`, `docker/login-action@v3`

---

### Task 1: Fix `check-version.yml` — add `pull-requests: read` permission

**Files:**
- Modify: `.github/workflows/check-version.yml:8-9`

**Step 1: Make the edit**

In `.github/workflows/check-version.yml`, change:
```yaml
permissions:
  contents: read
```
to:
```yaml
permissions:
  contents: read
  pull-requests: read
```

**Step 2: Verify the file looks correct**

Run: `cat -n .github/workflows/check-version.yml | head -15`
Expected: Lines 8-10 show both `contents: read` and `pull-requests: read`.

**Step 3: Commit**

```bash
git add .github/workflows/check-version.yml
git commit -m "fix(ci): add pull-requests: read for dorny/paths-filter on PR events"
```

---

### Task 2: Fix `check-version.yml` — replace `sdk/VERSION` read with `pyproject.toml`

**Files:**
- Modify: `.github/workflows/check-version.yml` (the `check-sdk-version` job)

**Step 1: Update "Get PR version" step in `check-sdk-version` job**

Find the step named "Get PR version" inside the `check-sdk-version` job. Replace the `run` block:

Old:
```bash
if [ ! -f sdk/VERSION ]; then
  echo "::error::sdk/VERSION file is missing from this PR."
  exit 1
fi
echo "version=$(tr -d '[:space:]' < sdk/VERSION)" >> "$GITHUB_OUTPUT"
```

New:
```bash
if [ ! -f sdk/pyproject.toml ]; then
  echo "::error::sdk/pyproject.toml is missing from this PR."
  exit 1
fi
version=$(python3 -c "import tomllib; f=open('sdk/pyproject.toml','rb'); d=tomllib.load(f); print(d['project']['version'])")
echo "version=$version" >> "$GITHUB_OUTPUT"
```

**Step 2: Update "Get main version" step in `check-sdk-version` job**

Find the step named "Get main version" inside the `check-sdk-version` job. Replace the `run` block:

Old:
```bash
git fetch origin main --depth=1
echo "version=$(git show origin/main:sdk/VERSION | tr -d '[:space:]')" >> "$GITHUB_OUTPUT"
```

New:
```bash
git fetch origin main --depth=1
version=$(git show origin/main:sdk/pyproject.toml | python3 -c "import sys,tomllib; print(tomllib.load(sys.stdin.buffer)['project']['version'])")
echo "version=$version" >> "$GITHUB_OUTPUT"
```

**Step 3: Verify the file looks correct**

Run: `grep -n "pyproject.toml\|VERSION" .github/workflows/check-version.yml`
Expected: `sdk/VERSION` references are gone from the `check-sdk-version` job; only `pyproject.toml` references remain for SDK. `spec/VERSION` and `sidecar/VERSION` references are still present (those are unchanged).

**Step 4: Commit**

```bash
git add .github/workflows/check-version.yml
git commit -m "fix(ci): read sdk version from pyproject.toml in check-version workflow"
```

---

### Task 3: Delete `sdk/VERSION`

**Files:**
- Delete: `sdk/VERSION`

**Step 1: Delete the file**

```bash
git rm sdk/VERSION
```

**Step 2: Commit**

```bash
git commit -m "chore: remove sdk/VERSION — pyproject.toml is now sole version source"
```

---

### Task 4: Fix `release-sdk.yml` — read version from `pyproject.toml`

**Files:**
- Modify: `.github/workflows/release-sdk.yml` (the `publish` job, "Read and validate VERSION" step)

**Step 1: Update the "Read and validate VERSION" step**

Find the step named "Read and validate VERSION" in the `publish` job. Replace the `run` block:

Old:
```bash
VERSION=$(tr -d '[:space:]' < sdk/VERSION)
if ! echo "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "::error::sdk/VERSION '$VERSION' is not valid semver"
  exit 1
fi
echo "version=$VERSION" >> "$GITHUB_OUTPUT"
```

New:
```bash
VERSION=$(python3 -c "import tomllib; f=open('sdk/pyproject.toml','rb'); d=tomllib.load(f); print(d['project']['version'])")
if ! echo "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "::error::sdk/pyproject.toml version '$VERSION' is not valid semver"
  exit 1
fi
echo "version=$VERSION" >> "$GITHUB_OUTPUT"
```

**Step 2: Verify no remaining `sdk/VERSION` references**

Run: `grep -n "sdk/VERSION" .github/workflows/release-sdk.yml`
Expected: no output.

**Step 3: Commit**

```bash
git add .github/workflows/release-sdk.yml
git commit -m "fix(ci): read sdk release version from pyproject.toml"
```

---

### Task 5: Fix `release-sidecar.yml` — remove `sdk/**` trigger and fix Docker Hub condition

**Files:**
- Modify: `.github/workflows/release-sidecar.yml:8-9` (trigger)
- Modify: `.github/workflows/release-sidecar.yml:43` (Docker Hub `if` condition)

**Step 1: Remove `sdk/**` from the push trigger**

Find the `paths:` block under `on.push`. Remove the `- 'sdk/**'` line so only `sidecar/**` remains:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'sidecar/**'
```

**Step 2: Fix the Docker Hub login condition**

Find the step named "Login to Docker Hub". Change:
```yaml
if: env.DOCKERHUB_USERNAME != ''
```
to:
```yaml
if: ${{ secrets.DOCKERHUB_USERNAME != '' }}
```

Also remove the `env` block from that step (it was only there to expose the secret for the condition):
```yaml
# Remove this:
env:
  DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
```

**Step 3: Verify**

Run: `grep -n "sdk/\*\*\|env.DOCKERHUB" .github/workflows/release-sidecar.yml`
Expected: no output.

**Step 4: Commit**

```bash
git add .github/workflows/release-sidecar.yml
git commit -m "fix(ci): remove sdk trigger from sidecar workflow; fix Docker Hub login condition"
```

---

## Verification Checklist

After all tasks are complete:

- [ ] `check-version.yml` has `pull-requests: read`
- [ ] `check-version.yml` SDK version check reads from `pyproject.toml`, not `sdk/VERSION`
- [ ] `sdk/VERSION` file is deleted
- [ ] `release-sdk.yml` reads version from `pyproject.toml`
- [ ] `release-sidecar.yml` only triggers on `sidecar/**`
- [ ] `release-sidecar.yml` Docker Hub login uses `${{ secrets.DOCKERHUB_USERNAME != '' }}`
- [ ] No remaining references to `sdk/VERSION` anywhere: `grep -r "sdk/VERSION" .github/`
