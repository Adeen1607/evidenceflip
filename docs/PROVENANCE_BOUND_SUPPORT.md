# Provenance-bound human support annotations

This opt-in evaluator builds on [human support scoring](HUMAN_SUPPORT_EVAL.md). It **verifies that every annotated evidence excerpt occurs verbatim in a source registered in the local manifest**. The existing source loader checks each source's SHA-256 before any annotation is scored.

## Acceptance criteria

- Every referenced source ID must exist in the SHA-256-verified manifest.
- Each annotation must include an `evidence_passages` object with exactly the same keys as `retrieved_source_ids`.
- Excerpts must be nonempty, literal substrings of the corresponding source text. Missing, invented, mismatched or tampered sources fail closed.
- Existing confusion-matrix, abstention and invalid-label semantics remain unchanged.
- Offline regression tests run without a model download or network request.

## Beginner workflow

Install from the checked-out feature branch with `python -m pip install -e .`. Run `python -m unittest tests.test_bound_support -v`.

Use your own authorized text sources registered with the normal `sources/manifest.json` workflow. For an annotation, add the exact passage you reviewed:

```json
[
  {
    "id": "claim-001",
    "claim": "Alpha is a synthetic observation.",
    "retrieved_source_ids": ["example"],
    "evidence_passages": {"example": "Alpha is a synthetic observation."},
    "gold": "supported",
    "predicted": "supported"
  }
]
```

The example is **invented for schema illustration**. It only works if your manifest includes source `example` with that exact text and correct SHA-256. Run from the repository root:

```bash
python -c "import json; from evidenceflip.support_eval import evaluate_bound_annotations; print(json.dumps(evaluate_bound_annotations(json.load(open('my_annotations.json', encoding='utf-8')), '.'), indent=2))"
```

## What this does not establish

Exact substring matching does not establish that a passage supports a claim, that a human label is correct, or that a generated response is faithful. It also does not prove that the excerpt was actually returned by a particular retrieval run. For research, save retrieval run IDs, chunk offsets, query and model configuration, dataset license, and independent human judgments; freeze held-out evaluation data before comparison. Do not include confidential, copyrighted or patient data without permission. Source SHA-256 is an integrity check, not a legal license or factual truth guarantee.

Research context: [Lewis et al. (2020)](https://arxiv.org/abs/2005.11401), [BEIR (2021)](https://arxiv.org/abs/2104.08663), [RAGAs (2024)](https://aclanthology.org/2024.eacl-demo.16/).

**Prelaunch:** Do not merge to main, enable or modify Pages, or deploy before November 30, 2026 and explicit owner authorization. Pages branch publishing remains unverified.
