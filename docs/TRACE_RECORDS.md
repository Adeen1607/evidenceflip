# Portable content-addressed BM25 retrieval records

This optional utility seals a BM25 trace with a deterministic SHA-256 digest, then replays the query against the SHA-256-verified local corpus. Version 2 records also contain informational runtime metadata: installed EvidenceFlip package version (or `uninstalled`), Python version, Python implementation and retriever identifier. No network, Ollama, or model weights are required.

Install: `python -m pip install -e .` (Python 3.10+). Keep the licensed source manifest and documents available locally.

```python
import json
from pathlib import Path
from evidenceflip.retrieval_trace import capture_bm25_trace
from evidenceflip.trace_record import seal_trace, verify_trace_record

root = Path(".")
trace = capture_bm25_trace("What does the refund policy say?", root)
record = seal_trace(trace)
Path("trace-record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
loaded = json.loads(Path("trace-record.json").read_text(encoding="utf-8"))
report = verify_trace_record(loaded, root)
print(report["record_verified"], report["environment_matches"])
```

**What is verified:** Strict schema, digest over canonical UTF-8 JSON, SHA-256-checked source corpus, and exact BM25 ranking/score replay. Version 2 includes metadata inside the digest. Older version 1 records remain verifiable. `environment_matches` is `True` when recorded descriptors equal the current environment, `False` when different, and `None` for version 1. A mismatch is reported rather than rejected because replay may still succeed across Python/package versions.

**Limitations:** The version is an installed distribution version, not a Git commit or dependency lockfile. Two different source revisions can share a package version. The Python and package fields are self-reported and can be forged; a new digest can be calculated by anyone. The digest is not a signature, historical run attestation, timestamp, or proof of factual support. A matching environment does not guarantee reproducibility; different source data or dependency versions may matter. The utility does not run a live LLM, sentence transformer, or external benchmark. Do not share traces containing sensitive questions. Examples and tests use project-authored MIT-licensed synthetic data; do not ingest unlicensed material.

Run `python -m unittest discover -s tests -v`. See [retrieval replay](RETRIEVAL_TRACE.md) and [chunk-bound support](CHUNK_BOUND_SUPPORT.md).
