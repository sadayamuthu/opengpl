# Contributing to OpenGPL

Thanks for helping. OpenGPL's output goes to security engineers and
assessors, so three things have to hold, and most of this guide is about
keeping them:

1. **No overclaiming.** A control appears in the output only when a policy
   field implements it, its status (`enforced`, `heuristic` or `declared`)
   matches what the code does, and nothing says a control is met.
2. **Untrusted text can't stall the runtime.** Every regular expression on
   the input, output and logging paths runs in linear time, with a timing
   test to prove it.
3. **Logs never leak what the policy keeps out.** Redaction failures drop the
   text; they never fall back to writing it raw.

This guide covers the code: the SDK, the sidecar, the GitHub Action and the
compliance mappings. Changes to the specification itself follow the process
in [spec/CONTRIBUTING.md](spec/CONTRIBUTING.md), which includes a 30-day
public comment period for normative changes.

- [Ways to help](#ways-to-help)
- [Development setup](#development-setup)
- [Code layout](#code-layout)
- [Adding or changing a mapping](#adding-or-changing-a-mapping)
- [Adding a detector](#adding-a-detector)
- [Pull requests](#pull-requests)
- [Security](#security)
- [License](#license)

## Ways to help

- **Report a wrong mapping or status.** A control listed without a field
  that implements it, or a status stronger than what the code does, is the
  most serious kind of bug. Name the control, the policy field and the
  source text you're comparing against.
- **Report a missed detection or a missed redaction**, with a made-up example
  that reproduces it. Never paste real prompts, logs or secrets.
- **Pick up a ⏳ row** in [Implementation status](USAGE.md#implementation-status):
  `model_controls`, `input_controls.sanitize` and `enforcement.on_violation`
  are the next pieces of the spec to enforce.
- **Write an example policy** for a use case the
  [examples](spec/examples/) don't cover yet.

For anything larger than a small fix, open an issue first so we can agree on
the approach before you write the code.

## Development setup

You need Python 3.11 or newer.

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e "sdk[dev]"
(cd sdk && pytest -q)
ruff check . && ruff format --check .
python spec/scripts/validate_examples.py
python spec/scripts/gen_compliance_mapping.py --check
npx markdownlint-cli2 "**/*.md"
```

The PII detector has two backends: a dependency-free regex one, and
Microsoft Presidio with the `[pii]` extra. They behave differently (Presidio
skips some numbers the regexes catch), so CI tests both. To run the
Presidio suite locally:

```sh
pip install -e "sdk[dev,pii]"
python -m spacy download en_core_web_lg
(cd sdk && pytest -q)
```

To try the sidecar, build it from the repository root:

```sh
docker build -f sidecar/Dockerfile -t opengpl-sidecar:dev .
```

## Code layout

```text
sdk/src/opengpl/
  engine.py, loader.py, models.py   PolicyEngine, policy loading and validation
  gates/                            input, model and output gates
  detectors/                        prompt-injection, jailbreak and PII detectors
  audit/ledger.py                   the JSONL decision log and its redaction
  audit/oscal.py                    OSCAL component definitions and assessment results
  compliance/status.py              what the SDK enforces, per policy field and value
  compliance/mapping.py             which controls a policy addresses
  compliance/mappings/*.yaml        the mapping data, one file per framework
  compliance/data/                  pinned NIST reference data
  cli.py                            the opengpl command
sidecar/                            the HTTP sidecar
spec/                               the specification, schema, examples and docs
action.yml                          the GitHub Action
```

## Adding or changing a mapping

Mappings live in `sdk/src/opengpl/compliance/mappings/<framework>.yaml`:

```yaml
- control: au-2
  field: audit.log_level
  when: {in: [STANDARD, FULL, DEBUG]}
  statement: "audit.log_level is {value}; the runtime writes a decision record …"
  rationale: "AU-2 event logging: gate decisions are the logged event type."
```

- `when` takes exactly one of `equals`, `in`, `any_of`, `true`, `false` or
  `present`. Entries are validated when they load.
- The status is never written in the YAML. It comes from
  `compliance/status.py`, so a mapping can't claim more than the code does.
- **The rationale must name the specific requirement the field supports**,
  and say "policy declaration" when the SDK doesn't act on the field. Don't
  map a control to the policy document as a whole, to practices outside the
  policy (such as version control), or to a field with no defined meaning.
- **Control IDs must be real.** SP 800-53 IDs are checked against the pinned
  NIST catalog, and AI RMF IDs against the list of subcategories in
  `compliance/data/`. Cite your source for EU AI Act, HIPAA and SOC 2 IDs in
  the pull request.
- Regenerate the tables in `spec/docs/compliance-mapping.md` with
  `python spec/scripts/gen_compliance_mapping.py`. CI fails if they're out of
  date.

To refresh the pinned NIST data, run `python sdk/scripts/update_nist_data.py`
and review the diff.

## Adding a detector

- Register what it enforces in `compliance/status.py`: `heuristic` for
  pattern matching, `enforced` only when the SDK reliably acts on the field.
- **Bound every quantifier** (`{0,64}`, not `*` or `+`) and avoid patterns
  that can match the same text in more than one way. Add the new pattern to
  the timing tests in `sdk/tests/test_decision_log.py` (log redaction) or
  `sdk/tests/test_detectors.py` (detectors), with adversarial input of 100 KB or more,
  asserting it finishes in under a second.
- Test what it catches and what it must not touch. For redaction, include a
  case showing earlier placeholders such as `[REDACTED-US_SSN]` survive.

## Pull requests

- Keep each pull request to one change, with tests. CI runs lint, tests on
  Python 3.11 to 3.13 and on both PII backends, the spec checks and a sidecar
  smoke test.
- **Bump the version** of each component you change. A pull request that
  changes `sdk/src/` must bump `sdk/pyproject.toml`; one that changes the
  sidecar's Python files or Dockerfile must bump `sidecar/VERSION`; a check
  enforces both. Merging to `main` publishes the new versions.
- Write commit messages in the present tense ("Add a HIPAA example"), and
  sign them off for the DCO: `git commit -s`.

## Security

Report vulnerabilities privately; see [SECURITY.md](SECURITY.md). A missed
detection or redaction in an unusual format is a normal bug, not a
vulnerability.

## License

By contributing, you agree that your code, schemas and examples are licensed
under the [Apache License 2.0](LICENSE), and changes to the specification
text under [CC BY 4.0](spec/LICENSE-SPEC).
