"""Recompute BM25 retrieval to check whether annotated chunks were actually returned.

This is reproducible local replay, not an immutable or independently signed run log.
"""
from __future__ import annotations

from pathlib import Path

from evidenceflip.chunk_support import evaluate_chunk_bound_annotations
from evidenceflip.rag import BM25Retriever, chunk_sources, load_sources


def capture_bm25_trace(question: str, root: str | Path, *, top_k: int = 3,
                       chunk_size: int = 120, overlap: int = 20,
                       manifest: str = "sources/manifest.json") -> dict:
    """Return a deterministic, provenance-bearing BM25 retrieval trace."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be nonblank")
    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k must be a positive integer")
    chunks = chunk_sources(load_sources(root, manifest), size=chunk_size, overlap=overlap)
    hits = BM25Retriever(chunks).search(question, top_k)
    return {
        "method": "bm25_replay_v1", "question": question, "top_k": top_k,
        "chunk_size": chunk_size, "overlap": overlap,
        "hits": [{
            "chunk_id": hit.chunk.id, "source_id": hit.chunk.source_id,
            "start_word": hit.chunk.start_word, "end_word": hit.chunk.end_word,
            "source_sha256": hit.chunk.source_sha256, "score": hit.score,
        } for hit in hits],
    }


def evaluate_trace_bound_annotations(records: list[dict], root: str | Path, *,
                                     chunk_size: int = 120, overlap: int = 20,
                                     manifest: str = "sources/manifest.json") -> dict:
    """Require each annotation's chunk to appear in a freshly replayed BM25 top-k.

    Every annotation must include a retrieval_trace captured by capture_bm25_trace.
    The full trace must equal the deterministic replay, including ranking and scores.
    This cannot prove that a historical retrieval happened or that claims are true.
    """
    report = evaluate_chunk_bound_annotations(
        records, root, chunk_size=chunk_size, overlap=overlap, manifest=manifest)
    for row in records:
        trace = row.get("retrieval_trace")
        if not isinstance(trace, dict) or set(trace) != {
            "method", "question", "top_k", "chunk_size", "overlap", "hits"
        }:
            raise ValueError(f"Malformed retrieval trace for {row['id']}")
        if trace["method"] != "bm25_replay_v1":
            raise ValueError(f"Unsupported retrieval method for {row['id']}")
        if type(trace["chunk_size"]) is not int or type(trace["overlap"]) is not int:
            raise ValueError(f"Invalid trace chunk settings for {row['id']}")
        if (trace["chunk_size"], trace["overlap"]) != (chunk_size, overlap):
            raise ValueError(f"Trace chunk settings mismatch for {row['id']}")
        expected = capture_bm25_trace(
            trace["question"], root, top_k=trace["top_k"],
            chunk_size=chunk_size, overlap=overlap, manifest=manifest)
        if trace != expected:
            raise ValueError(f"Retrieval trace differs from BM25 replay for {row['id']}")
        returned = {(h["source_id"], h["chunk_id"]) for h in expected["hits"]}
        for sid, binding in row["retrieval_chunks"].items():
            if (sid, binding["chunk_id"]) not in returned:
                raise ValueError(f"Annotated chunk not returned by retrieval for {row['id']}")
    report["retrieval_replay_verified"] = True
    report["retrieval_replay_scope"] = (
        "Deterministic BM25 top-k replay against SHA-256 checked sources; "
        "not historical run attestation, semantic entailment or model faithfulness")
    return report
