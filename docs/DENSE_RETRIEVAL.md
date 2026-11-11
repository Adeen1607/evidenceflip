# Comparing BM25 and dense retrieval locally

EvidenceFlip can search the **same SHA-256-verified source corpus** using
dependency-free BM25 or a pretrained sentence-transformer encoder. This is an
engineering baseline, not a new foundation model or a peer-reviewed comparison.

## Install and run

Python 3.10+ is required. Run these commands from a checkout of the development
branch. BM25 requires no model download:

```bash
python -m pip install -e .
evidenceflip-rag --root . --retriever bm25 retrieve "What is the Orion dataset size?"
evidenceflip-rag --root . --retriever bm25 benchmark --set examples/retrieval_benchmark.json --top-k 3 > bm25.json
```

Dense retrieval is opt-in. The optional dependency is large and its first run
may download pretrained weights. Check the selected model card, license,
hardware requirements, and your institution's data policies first:

```bash
python -m pip install -e '.[dense]'
evidenceflip-rag --root . --retriever dense \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 \
  retrieve "What is the Orion dataset size?"
evidenceflip-rag --root . --retriever dense \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 \
  benchmark --set examples/retrieval_benchmark.json --top-k 3 > dense.json
```

The model identifier is a pretrained embedding model, **not** a model trained
by EvidenceFlip. The project does not bundle model weights. An internet
connection or an already cached model may be needed for the first run. Do not
upload restricted research text or commit model caches. No live embedding model
was executed by the CI tests that introduced this adapter.

Both benchmark outputs include Hit@k and MRR@k, the query-level retrieved
source IDs, corpus and benchmark SHA-256 fingerprints, chunk settings, Python
and OS metadata, and measured retrieval-loop wall time. The wall time excludes
index/model loading and is not a portable performance claim. No stochastic
seed is used by the deterministic BM25 and cosine-ranking code. Actual
sentence-transformer execution may depend on library, model, device and
backend versions, so record those separately for a published experiment.

## Important interpretation

- The included 11-document corpus and 11 labels are **project-authored
  synthetic regression fixtures**, distributed under the repository's MIT
  license. They are not held-out scholarly data or an external benchmark.
- BM25 scores and cosine similarities are different scales. Do not compare
  their raw scores or interpret a high similarity as calibrated confidence.
- Dense retrieval always returns the closest chunks when the index is
  nonempty, even if they are irrelevant. Inspect passages before generating
  claims. BM25 may return zero hits when query terms do not match.
- The current metrics evaluate **source retrieval**, not claim-level
  entailment, hallucination rate, answer quality, or user productivity.
- The unit tests inject a tiny deterministic fake encoder to check ranking,
  provenance, malformed embeddings, and CLI wiring. They do **not** establish
  performance of any real sentence-transformer checkpoint.
- The source registry records caller-declared licenses and file fingerprints.
  Neither metadata field proves a document is accurate or legally reusable.

## Designing a real comparison

Use an explicitly permitted corpus and held-out, human-reviewed relevance
labels. Freeze corpus, query set, chunking, top-k, model revision, and
preprocessing before evaluation. Report per-query failures and metrics on
multiple domains, including paraphrases and out-of-distribution queries.
Record exact embedding-model revision, dependency versions, CPU/GPU, memory,
indexing time, and query latency separately. Use human-reviewed claim support
judgments for generated answers rather than treating valid citation IDs as
proof of faithfulness.

Scientific grounding: [Lewis et al. (2020)](https://arxiv.org/abs/2005.11401),
[BEIR (Thakur et al., 2021)](https://arxiv.org/abs/2104.08663), and
[RAGAs (Es et al., 2024)](https://aclanthology.org/2024.eacl-demo.16/).
