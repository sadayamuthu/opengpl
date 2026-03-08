# Schema Distribution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Publish OpenGPL schema files to `https://opengpl.org/schemas/v0.1/` on every release and document how consumers use them for editor support and CI validation.

**Architecture:** The existing `release.yml` workflow gets a new final step that clones `sadayamuthu/opengpl.org`, copies both schema files into `schemas/v0.1/`, and pushes. GitHub Pages serves those files at `opengpl.org`. Consumers reference the URL directly — no install needed.

**Tech Stack:** GitHub Actions, Bash, GitHub Pages (`sadayamuthu/opengpl.org`), JSON Schema draft 2020-12

---

## Prerequisites (Manual — Do Before Running This Plan)

These steps must be completed by the repo owner in the GitHub UI before the automated steps will work:

1. Create repo `sadayamuthu/opengpl.org` on GitHub (public)
2. Go to Settings → Pages → Source: Deploy from branch `main`, folder `/`
3. Add a custom domain `opengpl.org` and configure your DNS to point to GitHub Pages
4. Create a GitHub PAT (classic or fine-grained) with `contents: write` access to `sadayamuthu/opengpl.org`
5. In the `sadayamuthu/opengpl` repo settings → Secrets → Actions, add secret named `OPENGPL_ORG_DEPLOY_TOKEN` with the PAT value

---

### Task 1: Update `$id` in JSON schema

**Files:**
- Modify: `schema/opengpl-v0.1.json:3`

**Context:** The JSON schema's `$id` currently points to the old openastra.org URL. This must be updated to match the new canonical URL before the schema is published.

**Step 1: Verify current value**

```bash
grep '"$id"' schema/opengpl-v0.1.json
```

Expected output:
```
"$id": "https://openastra.org/schemas/opengpl/v0.1/opengpl.schema.json",
```

**Step 2: Update the `$id`**

Edit `schema/opengpl-v0.1.json` line 3. Replace:
```json
"$id": "https://openastra.org/schemas/opengpl/v0.1/opengpl.schema.json",
```
with:
```json
"$id": "https://opengpl.org/schemas/v0.1/opengpl.schema.json",
```

**Step 3: Verify the change**

```bash
grep '"$id"' schema/opengpl-v0.1.json
```

Expected output:
```
"$id": "https://opengpl.org/schemas/v0.1/opengpl.schema.json",
```

**Step 4: Verify JSON is still valid**

```bash
python3 -c "import json; json.load(open('schema/opengpl-v0.1.json')); print('JSON valid')"
```

Expected output: `JSON valid`

**Step 5: Commit**

```bash
git add schema/opengpl-v0.1.json
git commit -m "fix: update schema \$id to opengpl.org canonical URL

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Add schema publish step to release.yml

**Files:**
- Modify: `.github/workflows/release.yml`

**Context:** Add a final step after "Create release" that clones `sadayamuthu/opengpl.org`, copies the schema files to `schemas/v0.1/`, and pushes. This step is gated on `tag_check.outputs.exists == 'false'` (same as all other release steps) so it only runs for new versions.

The step uses `OPENGPL_ORG_DEPLOY_TOKEN` secret to authenticate. It sets git user config to `github-actions[bot]` — the standard identity for automated commits.

**Step 1: Add the publish step**

Append the following step to `.github/workflows/release.yml`, after the "Create release" step (after line 70):

```yaml
      - name: Publish schema to opengpl.org
        if: steps.tag_check.outputs.exists == 'false'
        env:
          VERSION: ${{ steps.version.outputs.version }}
          DEPLOY_TOKEN: ${{ secrets.OPENGPL_ORG_DEPLOY_TOKEN }}
        run: |
          git clone "https://x-access-token:${DEPLOY_TOKEN}@github.com/sadayamuthu/opengpl.org.git" opengpl-org
          mkdir -p opengpl-org/schemas/v0.1
          cp schema/opengpl-v0.1.json opengpl-org/schemas/v0.1/opengpl.schema.json
          cp schema/opengpl-v0.1.yaml opengpl-org/schemas/v0.1/opengpl.schema.yaml
          cd opengpl-org
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add schemas/v0.1/
          git diff --cached --quiet && echo "No schema changes to publish." || \
            git commit -m "chore: publish OpenGPL v${VERSION} schema" && git push
```

**Step 2: Verify YAML is valid**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml')); print('YAML valid')"
```

Expected output: `YAML valid`

**Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: publish schema to opengpl.org on release

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Add "Using the Schema" section to README.md

**Files:**
- Modify: `README.md`

**Context:** Insert a new section between "Compliance Frameworks Supported" and "Contributing" so consumers know exactly how to use the schema URL for editor support and CI validation.

**Step 1: Add the section**

In `README.md`, insert the following block between the `---` after line 178 and `## Contributing` (line 180):

```markdown
## Using the Schema

The OpenGPL JSON Schema is published at:

```
https://opengpl.org/schemas/v0.1/opengpl.schema.json
```

### Editor Support (VS Code)

Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) and add this comment to the top of any policy file:

```yaml
# yaml-language-server: $schema=https://opengpl.org/schemas/v0.1/opengpl.schema.json
opengpl: '0.1'
policy: my-agent-policy
version: '1.0.0'
```

You will get auto-complete and inline validation errors as you type — no install needed.

### CI Validation (Python)

```bash
pip install jsonschema pyyaml
python3 - <<'EOF'
import yaml, jsonschema, urllib.request, json, sys

schema_url = 'https://opengpl.org/schemas/v0.1/opengpl.schema.json'
policy_file = sys.argv[1] if len(sys.argv) > 1 else 'my-policy.yaml'

schema = json.loads(urllib.request.urlopen(schema_url).read())
policy = yaml.safe_load(open(policy_file))
jsonschema.validate(policy, schema)
print(f'✓ {policy_file} is valid')
EOF
```

Run as: `python3 validate.py my-policy.yaml`

---

```

**Step 2: Verify the section was added correctly**

```bash
grep -n "Using the Schema" README.md
```

Expected output: a single matching line with the section heading.

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add Using the Schema section with editor and CI examples

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Summary of Files Changed

| File | Change |
|---|---|
| `schema/opengpl-v0.1.json` | Update `$id` to `https://opengpl.org/schemas/v0.1/opengpl.schema.json` |
| `.github/workflows/release.yml` | Add "Publish schema to opengpl.org" step |
| `README.md` | Add "Using the Schema" section |
