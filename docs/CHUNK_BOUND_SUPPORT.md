# Reconstructable chunk-bound support annotations

This opt-in evaluator extends [source-bound annotations](PROVENANCE_BOUND_SUPPORT.md). It checks whether a cited excerpt belongs to a **specific, deterministically reconstructed chunk** of a SHA-256-verified manifest source. This is more precise than matching a passage anywhere in the source.

## Acceptance criteria

1. Preserve the existing human-label confusion matrix and source SHA-256 validation.
2. Reject unknown chunk IDs, wrong source IDs, mismatched word offsets, missing or malformed bindings, and passages outside the specified chunk.
3. Support configurable word-window size and overlap with deterministic reconstruction.
4. Run offline without downloading an LLM or embeddings. Do not deploy Pages.

## Run

From the feature branch, install with `python -m pip install -e .` and run `python -m unittest tests.test_chunk_support -v`.

Each annotation uses the fields from the source-bound evaluator plus `retrieval_chunks`:

```json
[
  {
    "id": "claim-1",
    "claim": "Alpha beta",
    "retrieved_source_ids": ["example"],
    "evidence_passages": {"example": "Alpha beta"},
    "retrieval_chunks": {
      "example": {
        "chunk_id": "example#w0",
        "start_word": 0,
        "end_word": 3,
        "passage": "Alpha beta"
      }
    },
    "gold": "supported",
    "predicted": "supported"
  }
]
```

The fixture is project-authored synthetic example text. Register a source with ID `example`, text `Alpha beta gamma delta epsilon zeta.`, its correct SHA-256 and an appropriate declared license in your local manifest. Then run:

```python
import json
from evidenceflip.chunk_support import evaluate_chunk_bound_annotations

with open("my_annotations.json", encoding="utf-8") as f:
    annotations = json.load(f)
report = evaluate_chunk_bound_annotations(annotations, ".", chunk_size=3, overlap=0)
print(json.dumps(report, indent=2))
```

**Interpretation:** Chunk IDs and word offsets are reconstructed using the current `chunk_sources` implementation. Record the code revision, chunk size and overlap with research results. This does **not** prove a retrieval engine returned the chunk for a particular query or run, nor that the excerpt entails the claim. Independent labels, saved retrieval traces, dataset permissions, and held-out benchmarks remain necessary. The synthetic fixture is not a scientific accuracy benchmark.

Research context: [Lewis et al.](https://arxiv.org/abs/2005.11401), [BEIR](https://arxiv.org/abs/2104.08663), [RAGAs](https://aclanthology.org/2024.eacl-demo.16/).

**Release embargo:** No Pages or hosting changes. No main-branch push or merge while branch publishing remains unverified; public launch requires explicit approval no earlier than November 30, 2026.
