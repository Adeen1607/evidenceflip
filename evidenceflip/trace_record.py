"""Content-addressed, portable BM25 replay records.

SHA-256 detects accidental or untrusted modifications to an exported record.
It is not a signature, trusted timestamp, or proof a historical run occurred.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from evidenceflip.retrieval_trace import capture_bm25_trace


def canonical_bytes(value: dict) -> bytes:
    """Encode a JSON object reproducibly without NaN or Infinity."""
    if not isinstance(value, dict):
        raise ValueError("Record payload must be a JSON object")
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ValueError("Record contains non-JSON or non-finite values") from exc
    return encoded


def seal_trace(trace: dict) -> dict:
    """Create a detached content digest for an unmodified retrieval trace."""
    if not isinstance(trace, dict) or trace.get("method") != "bm25_replay_v1":
        raise ValueError("Only BM25 replay v1 traces are supported")
    return {
        "schema": "evidenceflip.trace_record.v1",
        "trace": trace,
        "sha256": hashlib.sha256(canonical_bytes(trace)).hexdigest(),
    }


def verify_trace_record(record: dict, root: str | Path, *,
                        manifest: str = "sources/manifest.json") -> dict:
    """Check record structure, content digest, and fresh verified-corpus replay."""
    if not isinstance(record, dict) or set(record) != {"schema", "trace", "sha256"}:
        raise ValueError("Malformed retrieval record")
    if record["schema"] != "evidenceflip.trace_record.v1":
        raise ValueError("Unsupported record schema")
    trace = record["trace"]
    if not isinstance(trace, dict) or set(trace) != {
        "method", "question", "top_k", "chunk_size", "overlap", "hits"
    } or trace["method"] != "bm25_replay_v1":
        raise ValueError("Malformed retrieval trace")
    digest = record["sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(
        ch not in "0123456789abcdef" for ch in digest
    ):
        raise ValueError("Invalid SHA-256 digest")
    actual = hashlib.sha256(canonical_bytes(trace)).hexdigest()
    if digest != actual:
        raise ValueError("Retrieval record digest mismatch")
    replay = capture_bm25_trace(
        trace["question"], root, top_k=trace["top_k"],
        chunk_size=trace["chunk_size"], overlap=trace["overlap"],
        manifest=manifest,
    )
    if trace != replay:
        raise ValueError("Retrieval record differs from verified BM25 replay")
    return {"record_verified": True, "sha256": digest,
            "scope": "Digest and current verified-corpus replay; no historical attestation"}
