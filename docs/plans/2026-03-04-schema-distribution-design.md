# Schema Distribution Design

**Date:** 2026-03-04
**Status:** Approved

## Goal

Make the OpenGPL JSON schema publicly available at a stable URL on `opengpl.org` so consumers can validate their policy files in CI and get editor auto-complete without installing anything.

## Approach: Public URL via GitHub Pages (opengpl.org)

Schema files are served from `https://opengpl.org/schemas/v0.1/...` via a GitHub Pages site at `sadayamuthu/opengpl.org`. The opengpl `release.yml` workflow automatically copies schema files to the Pages repo on every release.

Chosen over npm distribution and schedule-based pull because it is zero-infrastructure, automatic, and matches the `$id` already embedded in the JSON schema.

## Schema URLs

| File | Public URL |
|---|---|
| JSON Schema | `https://opengpl.org/schemas/v0.1/opengpl.schema.json` |
| YAML Schema | `https://opengpl.org/schemas/v0.1/opengpl.schema.yaml` |

Paths are version-pinned (`/v0.1/`) — old URLs remain valid forever when new versions ship.

## Changes to This Repo

### 1. Update `$id` in JSON schema

`schema/opengpl-v0.1.json` — change `$id` from:
```
https://openastra.org/schemas/opengpl/v0.1/opengpl.schema.json
```
to:
```
https://opengpl.org/schemas/v0.1/opengpl.schema.json
```

### 2. Extend `release.yml`

Add a final step to `.github/workflows/release.yml` that runs after the GitHub Release is published:

1. Clone `sadayamuthu/opengpl.org` using `OPENGPL_ORG_DEPLOY_TOKEN` secret
2. Create `schemas/v0.1/` directory
3. Copy `schema/opengpl-v0.1.json` → `schemas/v0.1/opengpl.schema.json`
4. Copy `schema/opengpl-v0.1.yaml` → `schemas/v0.1/opengpl.schema.yaml`
5. Commit and push to `opengpl.org` main branch

### 3. Add "Using the Schema" section to README.md

Document both consumer workflows:

**Editor support** — `yaml-language-server` comment at top of policy file:
```yaml
# yaml-language-server: $schema=https://opengpl.org/schemas/v0.1/opengpl.schema.json
```

**CI validation** — Python one-liner using `jsonschema` and `pyyaml`:
```bash
pip install jsonschema pyyaml
python -c "
import yaml, jsonschema, urllib.request, json
schema = json.loads(urllib.request.urlopen('https://opengpl.org/schemas/v0.1/opengpl.schema.json').read())
policy = yaml.safe_load(open('my-policy.yaml'))
jsonschema.validate(policy, schema)
print('Policy valid')
"
```

## One-Time Manual Setup

These steps are done once by the repo owner, not automated:

1. Create `sadayamuthu/opengpl.org` on GitHub
2. Enable GitHub Pages (branch: `main`, root `/`)
3. Configure custom domain `opengpl.org` in repo settings
4. Create a GitHub PAT with `contents: write` scope
5. Store as secret `OPENGPL_ORG_DEPLOY_TOKEN` in the opengpl repo settings

## Files Changed

| File | Change |
|---|---|
| `schema/opengpl-v0.1.json` | Update `$id` to `https://opengpl.org/schemas/v0.1/opengpl.schema.json` |
| `.github/workflows/release.yml` | Add schema publish step |
| `README.md` | Add "Using the Schema" section |
