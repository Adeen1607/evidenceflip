# BM25 retrieval replay and annotated evidence

EvidenceFlip can now verify that a human-annotated chunk is returned by a **fresh deterministic BM25 search**, rather than merely reconstructing the chunk from a source document.

## Use

Install locally with `python -m pip install -e .`. For an existing manifest of UTF-8 documents with verified SHA-256 hashes:

```python
from evidenceflip.retrieval_trace import capture_bm25_trace, evaluate_trace_bound_annotations

trace = capture_bm25_trace("alpha", ".", top_k=3, chunk_size=120, overlap=20)
# Add the trace to each existing chunk-bound annotation under retrieval_trace.
# Each annotation's retrieval_chunks must reference chunks in trace["hits"].
report = evaluate_trace_bound_annotations(records, ".", chunk_size=120, overlap=20)
print(report["retrieval_replay_verified"])
```

`records` follows [chunk-bound support](CHUNK_BOUND_SUPPORT.md): each annotation includes `id`, `claim`, `retrieved_source_ids`, `evidence_passages`, `retrieval_chunks`, `gold`, and `predicted`. Add the exact `retrieval_trace` dictionary returned above.

The replay checks the complete ranked top-k list, scores, source IDs, chunk IDs, word offsets, source hashes and chunk settings. If a cited chunk was not returned, evaluation fails. A query change, altered ranking or source tampering also fails.

**Limits:** This is a reproducible **replay**, not proof that a historical retrieval run happened. A user can construct a valid trace after the fact. It is not cryptographically signed or externally timestamped. BM25 rankings depend on this implementation and corpus. It does not verify semantic entailment, annotator correctness, actual Ollama output, or sentence-transformer retrieval. No external benchmark figures are reported.

Test offline: `python -m unittest discover -s tests -v`. The project-authored synthetic test fixture declares MIT licensing. Only import documents you have permission to process, and record their licensing and provenance in the source manifest.
