"""Source-level retrieval evaluation against explicitly labeled relevance judgments.

No model is trained or called here. This module reports measured results only
when the caller supplies actual retrieval outputs and labels.
"""
from __future__ import annotations

from collections.abc import Iterable
from math import isfinite


def evaluate_ranked_sources(cases: list[dict], *, k: int = 5,
                            known_sources: Iterable[str] | None = None) -> dict:
    """Evaluate ranked source IDs with hit@k, MRR@k, precision@k and recall@k.

    Each case has a unique id, nonempty question, relevant_sources (nonempty
    unique IDs), and retrieved_sources (ranked unique IDs). A retrieved source
    counts only once, even when a retriever returned multiple chunks from it.
    The input must already be held out from model/prompt selection.
    """
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if not isinstance(cases, list) or not cases:
        raise ValueError("At least one labeled case is required")
    universe = None
    if known_sources is not None:
        universe = set(known_sources)
        if not universe or any(not isinstance(s, str) or not s.strip() for s in universe):
            raise ValueError("known_sources must contain valid source IDs")
    seen_ids: set[str] = set()
    seen_questions: set[str] = set()
    rows = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != {
            "id", "question", "relevant_sources", "retrieved_sources"
        }:
            raise ValueError("Case must have id, question, relevant_sources and retrieved_sources")
        cid, question = case["id"], case["question"]
        if not isinstance(cid, str) or not cid.strip() or cid in seen_ids:
            raise ValueError("Case IDs must be unique nonblank strings")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be nonblank")
        normalized = " ".join(question.casefold().split())
        if normalized in seen_questions:
            raise ValueError("Duplicate normalized question risks evaluation leakage")
        seen_ids.add(cid)
        seen_questions.add(normalized)
        relevant, retrieved = case["relevant_sources"], case["retrieved_sources"]
        if not isinstance(relevant, list) or not relevant or not isinstance(retrieved, list):
            raise ValueError("Relevant and retrieved sources must be lists; relevant cannot be empty")
        for name, ids in (("relevant", relevant), ("retrieved", retrieved)):
            if any(not isinstance(s, str) or not s.strip() for s in ids):
                raise ValueError(f"{name} source IDs must be nonblank strings")
            if len(set(ids)) != len(ids):
                raise ValueError(f"Duplicate {name} source ID")
            if universe is not None and not set(ids).issubset(universe):
                raise ValueError(f"Unknown {name} source ID")
        selected = retrieved[:k]
        matches = set(selected) & set(relevant)
        first = next((i for i, sid in enumerate(selected, 1) if sid in relevant), None)
        rows.append({
            "id": cid, "hit": bool(matches),
            "reciprocal_rank": 1 / first if first else 0.0,
            "precision": len(matches) / k,
            "recall": len(matches) / len(relevant),
            "retrieved_at_k": selected,
        })
    n = len(rows)
    return {
        "cases": n, "k": k,
        "hit_rate": sum(r["hit"] for r in rows) / n,
        "mrr": sum(r["reciprocal_rank"] for r in rows) / n,
        "precision_at_k": sum(r["precision"] for r in rows) / n,
        "recall_at_k": sum(r["recall"] for r in rows) / n,
        "details": rows,
        "scope": "Source-level labeled retrieval only; not generation faithfulness or generalization",
    }


def collect_ranked_sources(retriever, question: str, *, k: int = 5) -> list[str]:
    """Adapt the existing BM25/dense Retriever.search protocol to source IDs.

    Searches at k chunks, then deduplicates source IDs in ranked order.
    """
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be nonblank")
    hits = retriever.search(question, k)
    sources: list[str] = []
    for hit in hits:
        source = hit.chunk.source_id
        if not isinstance(source, str) or not source.strip():
            raise ValueError("Retriever returned invalid source ID")
        if source not in sources:
            sources.append(source)
    return sources
