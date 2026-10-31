# Security Policy

## Reporting a vulnerability

Please don't report security problems in a public issue, pull request or
discussion. Use
[**Report a vulnerability**](https://github.com/sadayamuthu/opengpl/security/advisories/new)
on the repository's Security tab instead. Only the maintainer can see the
report.

Include what you can of:

- the `opengpl-sdk` version (`opengpl --version`) or the sidecar image tag,
  your Python version and OS
- whether the PII extra is installed (`opengpl-sdk[pii]`) and how OpenGPL was
  run: the Python SDK, the CLI or the sidecar
- the policy file involved, reduced to the smallest one that shows the problem
- steps to reproduce, and what happened compared with what you expected

You'll get a reply when the report has been read, and again when a fix is
ready. A fix ships as a patch release; the advisory names you unless you'd
rather it didn't.

## Supported versions

OpenGPL is pre-1.0. Fixes land in the latest `opengpl-sdk` and sidecar
releases only; please upgrade before reporting.

## What counts

The decision log can hold prompts and model output, and the sidecar is an
HTTP service that reads policy files from disk. Anything that breaks one of
these promises is a security issue:

- **Logs don't leak what the policy keeps out.** Unless a policy sets
  `audit.pii_in_logs: true`, a decision record holds only a SHA-256 hash of
  the text, or, at `log_level: FULL` or `DEBUG`, the text after PII and
  credential redaction. Raw text in a record despite that, or a redaction
  failure that writes raw text, is in scope.
- **OSCAL output stays shareable.** Component definitions and assessment
  results never include prompt or response text. Text, or anything it can be
  recovered from, appearing in OSCAL output is in scope.
- **The sidecar reads only policies under `OPENGPL_POLICY_DIR`.** A policy
  name that makes it read, load or reveal a file outside that directory is in
  scope.
- **Untrusted text can't stall the runtime.** Every regex on the input,
  output and logging paths is meant to run in linear time. An input of a few
  hundred kilobytes or less that takes seconds to evaluate or redact is in
  scope.
- **Untrusted input stays data.** A policy file, prompt or decision record
  that makes the SDK, CLI or sidecar run a command or write outside the paths
  it was given is in scope.

These are known limits, not vulnerabilities:

- The detectors are heuristics: a short list of regular expressions for
  common prompt-injection and jailbreak phrasings, and pattern-based PII and
  credential matching. A missed injection or an unredacted secret in an
  unusual format is a bug. Report it in a normal issue; see
  [CONTRIBUTING.md](CONTRIBUTING.md).
- The sidecar has no authentication and no request-size limit. Run it on a
  private network or behind a proxy that provides both.
- The decision-log file is created with your process's default permissions.
  Restrict the directory if the log may hold redacted text.
- When a policy declares an `opengpl` version whose schema isn't bundled, the
  loader fetches the schema from `https://opengpl.org`. All other operations
  make no network calls.
