# Contributing to OpenGPL

Thank you for your interest in contributing to OpenGPL — the open policy language for generative AI systems.

OpenGPL is an **OpenAstra open standard**, maintained at [openastra.org](https://openastra.org). This document explains how to contribute to the specification, schema, examples, and tooling.

---

## Ways to Contribute

### 1. Specification Feedback

- Open a [GitHub Discussion](https://github.com/sadayamuthu/opengpl/discussions) for general questions or ideas
- File a [GitHub Issue](https://github.com/sadayamuthu/opengpl/issues) for spec clarifications, errors, or gaps
- Submit a Pull Request for non-normative fixes (typos, formatting, example corrections)

### 2. Policy Examples

Contributions to the [`examples/`](./examples/) directory are especially welcome:

- New use case examples (finance, legal, education, government)
- Framework-specific examples (AutoGen, CrewAI, Semantic Kernel)
- Edge case examples (multi-agent, cross-tenant, air-gapped)

### 3. Schema Contributions

- Bug fixes in schema validation rules
- Additional `$defs` for reusable types
- Stricter pattern validation for slug fields

### 4. Integration Guides

- Framework integration walkthroughs
- Compliance mapping documentation
- Tutorials and getting started guides

---

## Governance

OpenGPL is maintained by **OpenAstra**. The governance model is intentionally lightweight at this stage:

| Change Type | Process | Timeline |
|---|---|---|
| **Normative** (schema, behavior, enums) | Issue → Draft PR → 30-day comment → Review → Merge | ~6–8 weeks |
| **Non-normative** (examples, docs, typos) | PR → Review → Merge | ~1–2 weeks |
| **PATCH clarification** | Issue → PR → Quick review | ~1 week |

All **normative changes** require:

1. A GitHub Issue describing the problem and proposed solution
2. A minimum **30-day public comment period**
3. No unresolved objections from active contributors

> Community governance will be formalized at v1.0 when OpenGPL reaches stable status.

---

## Pull Request Guidelines

- Keep PRs focused — one change per PR
- For spec changes, reference the GitHub Issue number
- For examples, ensure the policy validates against the JSON Schema
- Use present tense in commit messages: "Add healthcare example" not "Added"
- Sign your commits with DCO: `git commit -s`

---

## Code of Conduct

OpenGPL follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

---

## License

By contributing to OpenGPL you agree that your contributions will be licensed under:

- **Specification text**: Creative Commons CC BY 4.0
- **Code, schemas, examples**: Apache License 2.0

---

## Questions?

- GitHub Discussions: [github.com/sadayamuthu/opengpl/discussions](https://github.com/sadayamuthu/opengpl/discussions)
- Email: [opengpl@openastra.org](mailto:opengpl@openastra.org)
- Website: [openastra.org/opengpl](https://openastra.org/opengpl)
