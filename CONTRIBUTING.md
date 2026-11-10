# Contributing to EvidenceFlip

Thank you for helping improve DATA INTEGRITY evaluation for AI systems.

## Before opening a pull request

1. Open an issue describing the observed failure or the feature's use case.
2. Add or update a test. Prefer the smallest deterministic fixture that demonstrates the problem.
3. Implement the change without silently weakening source-integrity, citation, or assertion checks.
4. Run `python -m unittest discover -s tests -v`, `python -m evidenceflip verify`, and `python -m evidenceflip demo`.
5. Document changed behavior and any limitations. Do not call a deterministic demonstration a live model evaluation.

## What belongs in sources/

Use project-authored synthetic examples or openly licensed sources with clear attribution.
For each source, declare its provenance, license, path, and exact SHA-256 hash in `sources/manifest.json`.
Never commit private customer data, copyrighted articles without permission, credentials, or complete external LLM training datasets.

## Engineering standards

- Preserve Python 3.10+ compatibility, unless an intentional breaking change is approved.
- Keep the core evaluator usable without a hosted model or API key.
- Do not automatically discard fabricated citation IDs; those must remain visible to integrity checks.
- Describe checks precisely. A matching SHA-256 hash establishes file consistency against a registry, not truth.
- Use readable code, focused commits, and explanatory PR descriptions.

## Pull request template

**Problem:** What fails today?

**Change:** What behavior is different?

**Proof:** What test or reproducible example demonstrates it?

**Risk:** What might regress and how is it mitigated?

**Documentation:** What was updated?

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) when participating.
