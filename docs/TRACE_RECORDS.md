# Portable content-addressed BM25 retrieval records

This optional research utility adds a deterministic SHA-256 identifier to a BM25 retrieval trace and checks it against a fresh retrieval replay. It helps detect altered exported JSON and compare records across machines. It does **not** establish that a historical query was run, provide a digital signature, or prove factual support.

Install: `python -m pip install -e .` (Python 3.10+). Keep the source manifest and documents available locally.

```python
import json
from pathlib import Path
from evidenceflip.retrieval_trace import capture_bm25_trace
from evidenceflip.trace_record import seal_trace, verify_trace_record

root = Path(".")
trace = capture_bm25_trace("What does the refund policy say?", root)
record = seal_trace(trace)
Path("trace-record.json").write_text(
    json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
)
loaded = json.loads(Path("trace-record.json").read_text(encoding="utf-8"))
print(verify_trace_record(loaded, root))
```

The digest is SHA-256 over UTF-8 JSON with sorted keys, compact separators, no NaN/Infinity, and Unicode preserved. `verify_trace_record` checks exact fields, the digest, the SHA-256-checked source corpus, and a fresh BM25 replay with the recorded query and chunk settings. The record intentionally contains no hostnames, user identifiers, or timestamps. Avoid recording sensitive questions or source metadata in shared traces.

**Acceptance cases:** Round-trip JSON succeeds; key order does not change canonical bytes; modified rankings fail digest validation; recomputed digests on forged rankings still fail replay; changed documents fail source integrity; malformed records and nonfinite numbers fail.

**Limitations:** SHA-256 is unkeyed. An attacker can regenerate a digest, so this is not authentication. Reproducibility depends on matching source content and the retrieval implementation. Record the package revision separately for cross-version comparisons. No live Ollama or sentence-transformer model is run by this utility. The examples are project-authored MIT-licensed synthetic text. Do not ingest unlicensed or sensitive documents.

Run offline tests with `python -m unittest discover -s tests -v`. See [retrieval replay](RETRIEVAL_TRACE.md) and [chunk-bound support](CHUNK_BOUND_SUPPORT.md) for context.
