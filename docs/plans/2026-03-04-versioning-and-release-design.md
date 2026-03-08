# Versioning and Release Design

**Date:** 2026-03-04
**Status:** Approved

## Goal

Add a GitHub Actions-based CI/CD pipeline that:

1. Hard-blocks PRs from merging to `main` unless the `VERSION` file has been bumped
2. Automatically publishes a GitHub Release (with a full repo archive) on every merge to `main`

## Version Source of Truth

A plain text `VERSION` file at the repo root contains the current spec version (e.g., `0.1.0`).
This is the single canonical source. Developers bump it manually before opening a PR.

Versioning follows [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

## Approach: Manual VERSION + CI Enforcement

Chosen over alternatives (conventional commits + release-please, tag-triggered releases) because:

- Simple — no external tooling or commit message conventions required
- Appropriate for a specification project where version bumps are intentional decisions
- Matches the requirement exactly: hard block on PRs + release on every main merge

## Workflow 1: Version Bump Check (`check-version.yml`)

**Trigger:** `pull_request` targeting `main`

**Steps:**
1. Check out the PR branch
2. Fetch `VERSION` from `origin/main`
3. Compare PR version against main version using semver
4. Fail if versions are identical (no bump)
5. Fail if PR version is lower than main version (downgrade)
6. Pass if PR version is strictly higher

**Effect:** Hard-blocks the PR. Branch protection rules on GitHub must require this check to pass.

## Workflow 2: Release Publisher (`release.yml`)

**Trigger:** `push` to `main`

**Steps:**
1. Read `VERSION` file → version string (e.g., `0.2.0`)
2. Create git tag `v0.2.0` (idempotent — skips if tag already exists)
3. Build release archives:
   - `opengpl-v0.2.0.tar.gz`
   - `opengpl-v0.2.0.zip`
4. Create GitHub Release titled `OpenGPL v0.2.0`
   - Auto-generated release notes from commits since last tag
   - Both archive files attached as assets
5. Uses `softprops/action-gh-release`

## Edge Cases

| Scenario | Behavior |
|---|---|
| Direct push to main (no PR) | Release workflow runs; no version check fires |
| Tag already exists for this version | Release step skips gracefully, workflow passes |
| CHANGELOG not updated | Not enforced — out of scope |
| PR version lower than main | `check-version` fails, PR blocked |

## Recommended Manual Step

Enable branch protection on `main` in GitHub Settings:

- Require status check: `check-version` to pass before merging
- This is what makes the hard block effective for direct-to-main pushes via PR

## Files to Create

| File | Purpose |
|---|---|
| `VERSION` | Single source of truth for spec version (initial: `0.1.0`) |
| `.github/workflows/check-version.yml` | PR enforcement workflow |
| `.github/workflows/release.yml` | Release publisher workflow |
