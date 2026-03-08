# GitHub Workflows Review and Fixes

**Date:** 2026-03-06
**Approach:** Minimal targeted fixes (Approach A)

## Problem Summary

Four issues identified across the GitHub Actions workflows:

1. **Critical:** `check-version.yml` missing `pull-requests: read` permission, causing `dorny/paths-filter@v3` to fail on PR events.
2. **Fragile condition:** `release-sidecar.yml` Docker Hub login uses `env.DOCKERHUB_USERNAME` in `if:`, which is evaluated before the step's `env` block is in scope.
3. **Version source mismatch:** `release-sdk.yml` reads `sdk/VERSION` for the release tag, but `python -m build` uses the version from `sdk/pyproject.toml`. These can diverge.
4. **Unintended sidecar trigger:** `release-sidecar.yml` triggers on `sdk/**` changes but always reads `sidecar/VERSION`, risking "tag already exists" errors when only SDK changes.

## Design

### Fix 1: `check-version.yml` — add `pull-requests: read` and remove `sdk/VERSION`

**Permission fix:**
```yaml
permissions:
  contents: read
  pull-requests: read   # required by dorny/paths-filter on pull_request
```

**SDK version check — read from `pyproject.toml` instead of `sdk/VERSION`:**

Get PR version step:
```bash
version=$(python3 -c "import tomllib; f=open('sdk/pyproject.toml','rb'); d=tomllib.load(f); print(d['project']['version'])")
echo "version=$version" >> "$GITHUB_OUTPUT"
```

Get main version step:
```bash
git fetch origin main --depth=1
version=$(git show origin/main:sdk/pyproject.toml | python3 -c "import sys,tomllib; print(tomllib.load(sys.stdin.buffer)['project']['version'])")
echo "version=$version" >> "$GITHUB_OUTPUT"
```

Also: delete `sdk/VERSION` from the repo.

### Fix 2: `release-sdk.yml` — read version from `pyproject.toml`

Replace the `sdk/VERSION` read in "Read and validate VERSION":
```bash
VERSION=$(python3 -c "import tomllib; f=open('sdk/pyproject.toml','rb'); d=tomllib.load(f); print(d['project']['version'])")
if ! echo "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "::error::sdk/pyproject.toml version '$VERSION' is not valid semver"
  exit 1
fi
echo "version=$VERSION" >> "$GITHUB_OUTPUT"
```

### Fix 3: `release-sidecar.yml` — fix trigger and Docker Hub condition

**Remove `sdk/**` from push trigger:**
```yaml
paths:
  - 'sidecar/**'
```

**Fix Docker Hub login condition:**
```yaml
if: ${{ secrets.DOCKERHUB_USERNAME != '' }}
```

## Files Changed

| File | Change |
|------|--------|
| `.github/workflows/check-version.yml` | Add `pull-requests: read`; update SDK version check to use `pyproject.toml` |
| `.github/workflows/release-sdk.yml` | Read version from `pyproject.toml` instead of `sdk/VERSION` |
| `.github/workflows/release-sidecar.yml` | Remove `sdk/**` trigger; fix Docker Hub `if` condition |
| `sdk/VERSION` | Delete — `pyproject.toml` is now sole source of truth |

## Out of Scope

- Extracting repeated version-check logic into a composite action (separate PR)
- Adding `workflow_dispatch` to release workflows (separate PR)
