"""Execute labeled retrieval experiments without generation or benchmark inflation.

Project-authored MIT-licensed code. Caller supplies a licensed corpus, labels,
and already initialized retrievers. Times are machine-specific observations.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import platform
import time

from .labeled_eval import collect_ranked_sources, evaluate_ranked_sources
from .split_audit import require_disjoint_question_splits


def run_labeled_benchmark(
    splits: Mapping[str, list[dict]], retrievers: Mapping[str, object],
    *, known_sources: list[str], k: int = 5, test_split: str = "test",
) -> dict:
    """Evaluate source relevance using the same labeled test queries for each retriever.

    Each test case must contain id, question, relevant_sources. All partition
    question IDs/text are audited before retrieval. Each search requests k
    chunks, not necessarily k unique sources; this limitation is reported.
    """
    audit = require_disjoint_question_splits(splits)
    if test_split not in splits:
        raise ValueError("Requested test split does not exist")
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if not isinstance(retrievers, Mapping) or not retrievers:
        raise ValueError("At least one named retriever is required")
    if any(not isinstance(name, str) or not name.strip() for name in retrievers):
        raise ValueError("Retriever names must be nonblank")
    if not isinstance(known_sources, list) or not known_sources:
        raise ValueError("known_sources must be a nonempty list")
    if any(not isinstance(s, str) or not s.strip() for s in known_sources):
        raise ValueError("known_sources must contain nonblank strings")
    if len(set(known_sources)) != len(known_sources):
        raise ValueError("known_sources contains duplicates")
    cases = splits[test_split]
    # Validate labels and question structure before invoking any retriever.
    templates = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"id", "question", "relevant_sources"}:
            raise ValueError("Each case requires id, question and relevant_sources")
        templates.append(dict(case, retrieved_sources=[]))
    evaluate_ranked_sources(templates, k=k, known_sources=known_sources)

    results = {}
    for name, retriever in retrievers.items():
        if not callable(getattr(retriever, "search", None)):
            raise ValueError("Retriever must implement search(question, top_k)")
        measured = []
        durations = []
        for case in cases:
            start = time.perf_counter_ns()
            retrieved = collect_ranked_sources(retriever, case["question"], k=k)
            elapsed = (time.perf_counter_ns() - start) / 1_000_000
            durations.append(elapsed)
            measured.append(dict(case, retrieved_sources=retrieved))
        scores = evaluate_ranked_sources(measured, k=k, known_sources=known_sources)
        results[name] = {
            "metrics": scores,
            "latency_ms": {
                "per_query": durations,
                "mean": sum(durations) / len(durations),
            },
        }
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "k_chunks_requested": k,
        "test_split": test_split,
        "split_audit": audit,
        "retrievers": results,
        "limitations": (
            "Source-level relevance on caller-supplied labels; no independent "
            "judgment or generalization claim. Search requests k chunks, then "
            "deduplicates sources. Timings are environment-dependent and exclude "
            "index construction, model loading and document ingestion."
        ),
    }
