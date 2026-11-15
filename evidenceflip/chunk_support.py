"""Bind human support annotations to reproducibly reconstructed retrieval chunks.

Checks chunk identity and excerpt membership, not that a retriever actually
returned the chunk in a particular run or that the excerpt entails the claim.
"""
from __future__ import annotations

from pathlib import Path

from evidenceflip.rag import chunk_sources, load_sources
from evidenceflip.support_eval import evaluate_bound_annotations


def evaluate_chunk_bound_annotations(
    records: list[dict], root: str | Path, *,
    chunk_size: int = 120, overlap: int = 20,
    manifest: str = "sources/manifest.json",
) -> dict:
    """Validate per-source chunk references and score human labels.

    Each record has retrieval_chunks, a mapping of source ID to a dictionary
    containing chunk_id, start_word, end_word and passage. Passage must be
    an exact nonempty substring of the referenced chunk. The corresponding
    evidence_passages value must match passage exactly.
    """
    report = evaluate_bound_annotations(records, root, manifest)
    chunks = chunk_sources(load_sources(root, manifest), size=chunk_size, overlap=overlap)
    by_id = {chunk.id: chunk for chunk in chunks}
    for row in records:
        rid = row["id"]
        ids = row["retrieved_source_ids"]
        bindings = row.get("retrieval_chunks")
        if not isinstance(bindings, dict) or set(bindings) != set(ids):
            raise ValueError(f"Retrieval chunk IDs must match retrieved sources for {rid}")
        for sid in ids:
            item = bindings[sid]
            if not isinstance(item, dict) or set(item) != {
                "chunk_id", "start_word", "end_word", "passage"
            }:
                raise ValueError(f"Malformed chunk binding for {sid} in {rid}")
            chunk_id = item["chunk_id"]
            if not isinstance(chunk_id, str) or chunk_id not in by_id:
                raise ValueError(f"Unknown chunk ID for {sid} in {rid}")
            chunk = by_id[chunk_id]
            if chunk.source_id != sid:
                raise ValueError(f"Chunk source mismatch for {sid} in {rid}")
            if type(item["start_word"]) is not int or type(item["end_word"]) is not int:
                raise ValueError(f"Invalid chunk offsets for {sid} in {rid}")
            if (item["start_word"], item["end_word"]) != (chunk.start_word, chunk.end_word):
                raise ValueError(f"Chunk offset mismatch for {sid} in {rid}")
            passage = item["passage"]
            if (not isinstance(passage, str) or not passage.strip()
                    or passage != row["evidence_passages"][sid]
                    or passage not in chunk.text):
                raise ValueError(f"Passage is not bound to chunk for {sid} in {rid}")
    report["chunk_provenance_verified"] = True
    report["chunk_provenance_scope"] = (
        "Manifest hash, deterministic chunk ID/word offsets and exact excerpt membership; "
        "not retrieval-run attestation or semantic entailment"
    )
    report["chunk_size"] = chunk_size
    report["overlap"] = overlap
    return report
