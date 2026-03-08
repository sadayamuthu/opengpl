# Versioning and Release Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `VERSION` file, a hard-blocking PR version-bump check, and an automated GitHub Release publisher triggered on every merge to `main`.

**Architecture:** A plain-text `VERSION` file at the repo root is the single source of truth. A PR workflow (`check-version.yml`) fetches the version from `main` and fails if the PR hasn't bumped it. A release workflow (`release.yml`) fires on every push to `main`, reads `VERSION`, creates a git tag, and publishes a GitHub Release with `.tar.gz` and `.zip` archives.

**Tech Stack:** GitHub Actions, Bash (semver comparison via `sort -V`), `softprops/action-gh-release@v2`

---

### Task 1: Create the VERSION file

**Files:**
- Create: `VERSION`

**Step 1: Create the file**

```bash
echo "0.1.0" > VERSION
```

**Step 2: Verify contents**

```bash
cat VERSION
```

Expected output: `0.1.0`

**Step 3: Commit**

```bash
git add VERSION
git commit -m "chore: add VERSION file (0.1.0)"
```

---

### Task 2: Create the version-bump check workflow

**Files:**
- Create: `.github/workflows/check-version.yml`

**Context:** This workflow runs on every PR targeting `main`. It compares the `VERSION` in the PR branch against the `VERSION` on `main`. If they are the same or the PR version is lower, it fails and blocks the merge.

The semver comparison uses `sort -V` (version sort, available on all Linux runners) to determine ordering without any external dependencies.

**Step 1: Create the workflow file**

```yaml
# .github/workflows/check-version.yml
name: Check Version Bump

on:
  pull_request:
    branches:
      - main

jobs:
  check-version:
    name: Verify VERSION is bumped
    runs-on: ubuntu-latest
    steps:
      - name: Checkout PR branch
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get PR version
        id: pr_version
        run: echo "version=$(cat VERSION | tr -d '[:space:]')" >> "$GITHUB_OUTPUT"

      - name: Get main version
        id: main_version
        run: |
          git fetch origin main --depth=1
          echo "version=$(git show origin/main:VERSION | tr -d '[:space:]')" >> "$GITHUB_OUTPUT"

      - name: Compare versions
        env:
          PR_VERSION: ${{ steps.pr_version.outputs.version }}
          MAIN_VERSION: ${{ steps.main_version.outputs.version }}
        run: |
          echo "PR version:   $PR_VERSION"
          echo "Main version: $MAIN_VERSION"

          if [ "$PR_VERSION" = "$MAIN_VERSION" ]; then
            echo "::error::VERSION has not been bumped. PR=$PR_VERSION, main=$MAIN_VERSION"
            exit 1
          fi

          # Use sort -V to compare: the higher version should sort last
          HIGHER=$(printf '%s\n%s\n' "$MAIN_VERSION" "$PR_VERSION" | sort -V | tail -n1)
          if [ "$HIGHER" != "$PR_VERSION" ]; then
            echo "::error::PR version ($PR_VERSION) is lower than main ($MAIN_VERSION). Must bump forward."
            exit 1
          fi

          echo "Version bump confirmed: $MAIN_VERSION -> $PR_VERSION"
```

**Step 2: Verify YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/check-version.yml'))" && echo "YAML valid"
```

Expected output: `YAML valid`

**Step 3: Commit**

```bash
git add .github/workflows/check-version.yml
git commit -m "ci: add version-bump check workflow for PRs"
```

---

### Task 3: Create the release publisher workflow

**Files:**
- Create: `.github/workflows/release.yml`

**Context:** This workflow runs on every push to `main`. It reads `VERSION`, creates a git tag `vX.Y.Z` (skips if the tag already exists to handle idempotency), builds `.tar.gz` and `.zip` archives of the full repo, then publishes a GitHub Release using `softprops/action-gh-release@v2`.

The `GITHUB_TOKEN` is automatically provided by GitHub Actions — no secrets to configure.

**Step 1: Create the workflow file**

```yaml
# .github/workflows/release.yml
name: Publish Release

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  release:
    name: Create GitHub Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Read VERSION
        id: version
        run: echo "version=$(cat VERSION | tr -d '[:space:]')" >> "$GITHUB_OUTPUT"

      - name: Check if tag already exists
        id: tag_check
        env:
          VERSION: ${{ steps.version.outputs.version }}
        run: |
          if git rev-parse "v$VERSION" >/dev/null 2>&1; then
            echo "exists=true" >> "$GITHUB_OUTPUT"
            echo "Tag v$VERSION already exists — skipping release."
          else
            echo "exists=false" >> "$GITHUB_OUTPUT"
            echo "Tag v$VERSION does not exist — will create release."
          fi

      - name: Build archives
        if: steps.tag_check.outputs.exists == 'false'
        env:
          VERSION: ${{ steps.version.outputs.version }}
        run: |
          mkdir -p dist
          # tar.gz — exclude .git directory
          tar --exclude='.git' --exclude='dist' -czf "dist/opengpl-v${VERSION}.tar.gz" .
          # zip — exclude .git directory
          zip -r "dist/opengpl-v${VERSION}.zip" . --exclude '.git/*' --exclude 'dist/*'
          ls -lh dist/

      - name: Create release
        if: steps.tag_check.outputs.exists == 'false'
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v${{ steps.version.outputs.version }}
          name: OpenGPL v${{ steps.version.outputs.version }}
          generate_release_notes: true
          files: |
            dist/opengpl-v${{ steps.version.outputs.version }}.tar.gz
            dist/opengpl-v${{ steps.version.outputs.version }}.zip
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Step 2: Verify YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" && echo "YAML valid"
```

Expected output: `YAML valid`

**Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add automated release publisher workflow"
```

---

### Task 4: Enable branch protection (manual GitHub step)

**Files:** None — this is a GitHub UI configuration step.

**Context:** The `check-version` workflow only hard-blocks a PR if the repository has branch protection enabled requiring that check to pass. Without this, developers can still merge without a version bump.

**Step 1: Go to repository Settings**

Navigate to: `https://github.com/<owner>/opengpl/settings/branches`

**Step 2: Add branch protection rule for `main`**

- Click **Add rule** (or edit existing rule for `main`)
- Branch name pattern: `main`
- Enable: **Require status checks to pass before merging**
- Search for and add: `Verify VERSION is bumped` (this is the `name:` from the job in `check-version.yml`)
- Enable: **Require branches to be up to date before merging**
- Save

**Step 3: Verify**

Open a test PR without bumping `VERSION` — the merge button should be disabled with the `check-version` status showing as failed.

---

### Task 5: End-to-end smoke test

**Goal:** Verify the full pipeline works on a real PR.

**Step 1: Create a test branch**

```bash
git checkout -b test/release-pipeline
```

**Step 2: Bump VERSION**

```bash
echo "0.1.1" > VERSION
git add VERSION
git commit -m "chore: bump version to 0.1.1 (release pipeline smoke test)"
```

**Step 3: Push and open PR**

```bash
git push origin test/release-pipeline
```

Open a PR from `test/release-pipeline` → `main` on GitHub.

**Step 4: Verify check-version passes**

In the PR checks, confirm `Verify VERSION is bumped` shows green.

**Step 5: Merge and verify release**

Merge the PR. Navigate to the repository's **Releases** page and confirm:
- Release `OpenGPL v0.1.1` exists
- Both `opengpl-v0.1.1.tar.gz` and `opengpl-v0.1.1.zip` are attached
- Release notes are auto-generated

**Step 6: Revert VERSION if this was only a test**

If you don't want to actually advance the version, open another PR reverting back to `0.1.0` — but note you'll need to bump VERSION again to do so (use `0.1.2` or `0.2.0`).

---

## Summary of Files Created

| File | Purpose |
|---|---|
| `VERSION` | Canonical spec version (`0.1.0`) |
| `.github/workflows/check-version.yml` | PR hard-block if VERSION not bumped |
| `.github/workflows/release.yml` | Publish GitHub Release on every main push |
