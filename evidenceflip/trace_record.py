"""Content-addressed, portable BM25 replay records.

A digest is not a signature, timestamp, or proof of a historical run.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from evidenceflip.retrieval_trace import capture_bm25_trace


def canonical_bytes(value: dict) -> bytes:
    """Encode a JSON object reproducibly without NaN or Infinity."""
    if not isinstance(value, dict):
        raise ValueError("Record payload must be a JSON object")
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ValueError("Record contains non-JSON or non-finite values") from exc


def runtime_metadata() -> dict:
    """Record environment descriptors; these are informational, not attested."""
    try:
        package_version = version("evidenceflip")
    except PackageNotFoundError:
        package_version = "uninstalled"
    return {
        "package_version": package_version,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "retriever": "bm25_replay_v1",
    }


def seal_trace(trace: dict, *, metadata: dict | None = None) -> dict:
    """Seal a trace and environment metadata in schema v2.

    An explicit metadata mapping allows reproducing records in other environments.
    It must not contain secrets; metadata is not proof of where a run occurred.
    """
    if not isinstance(trace, dict) or trace.get("method") != "bm25_replay_v1":
        raise ValueError("Only BM25 replay v1 traces are supported")
    details = runtime_metadata() if metadata is None else metadata
    _validate_metadata(details)
    payload = {"trace": trace, "metadata": details}
    return {
        "schema": "evidenceflip.trace_record.v2",
        **payload,
        "sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
    }


def _validate_metadata(metadata: dict) -> None:
    expected = {"package_version", "python_version", "python_implementation", "retriever"}
    if not isinstance(metadata, dict) or set(metadata) != expected:
        raise ValueError("Malformed runtime metadata")
    if any(not isinstance(v, str) or not v.strip() or len(v) > 128
           for v in metadata.values()):
        raise ValueError("Invalid runtime metadata value")
    if metadata["retriever"] != "bm25_replay_v1":
        raise ValueError("Unsupported retriever metadata")


def verify_trace_record(record: dict, root: str | Path, *,
                        manifest: str = "sources/manifest.json") -> dict:
    """Validate a v1/v2 record, source integrity and deterministic BM25 replay."""
    if not isinstance(record, dict):
        raise ValueError("Malformed retrieval record")
    schema = record.get("schema")
    if schema == "evidenceflip.trace_record.v1":
        if set(record) != {"schema", "trace", "sha256"}:
            raise ValueError("Malformed retrieval record")
        payload = record.get("trace")
    elif schema == "evidenceflip.trace_record.v2":
        if set(record) != {"schema", "trace", "metadata", "sha256"}:
            raise ValueError("Malformed retrieval record")
        _validate_metadata(record["metadata"])
        payload = {"trace": record["trace"], "metadata": record["metadata"]}
    else:
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
    actual = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    if digest != actual:
        raise ValueError("Retrieval record digest mismatch")
    replay = capture_bm25_trace(
        trace["question"], root, top_k=trace["top_k"],
        chunk_size=trace["chunk_size"], overlap=trace["overlap"],
        manifest=manifest,
    )
    if trace != replay:
        raise ValueError("Retrieval record differs from verified BM25 replay")
    return {
        "record_verified": True, "sha256": digest,
        "metadata": record.get("metadata"),
        "environment_matches": (
            record["metadata"] == runtime_metadata() if schema.endswith(".v2") else None
        ),
        "scope": "Digest and current verified-corpus replay; no historical attestation",
    }
