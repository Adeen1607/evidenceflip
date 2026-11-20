"""Audit labeled evaluation partitions for exact normalized question leakage.

Project-authored MIT-licensed implementation. Exact matching is not semantic
paraphrase detection and does not establish independent source provenance.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib


def _normalize(question: str) -> str:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Each question must be a nonblank string")
    return " ".join(question.casefold().split())


def audit_question_splits(splits: Mapping[str, list[dict]]) -> dict:
    """Validate split structure and report overlapping normalized questions.

    Input: {"train": [{"id": "q1", "question": "..."}], "test": [...]}
    Additional per-case fields (such as relevance judgments) are permitted.
    The report contains no raw question text, only SHA-256 question digests.
    """
    if not isinstance(splits, Mapping) or len(splits) < 2:
        raise ValueError("At least two named splits are required")
    names = list(splits)
    if any(not isinstance(n, str) or not n.strip() for n in names):
        raise ValueError("Split names must be nonblank strings")
    by_question: dict[str, list[str]] = {}
    by_id: dict[str, list[str]] = {}
    counts = {}
    for name, cases in splits.items():
        if not isinstance(cases, list) or not cases:
            raise ValueError(f"Split {name!r} must contain cases")
        local_ids = set()
        local_questions = set()
        for case in cases:
            if not isinstance(case, dict) or "id" not in case or "question" not in case:
                raise ValueError("Cases require id and question")
            cid = case["id"]
            if not isinstance(cid, str) or not cid.strip():
                raise ValueError("Case IDs must be nonblank strings")
            normalized = _normalize(case["question"])
            if cid in local_ids:
                raise ValueError(f"Duplicate case ID in split {name!r}")
            if normalized in local_questions:
                raise ValueError(f"Duplicate normalized question in split {name!r}")
            local_ids.add(cid)
            local_questions.add(normalized)
            by_question.setdefault(normalized, []).append(name)
            by_id.setdefault(cid, []).append(name)
        counts[name] = len(cases)
    overlaps = [
        {"question_sha256": hashlib.sha256(q.encode("utf-8")).hexdigest(),
         "splits": sorted(owners)}
        for q, owners in by_question.items() if len(owners) > 1
    ]
    overlaps.sort(key=lambda x: x["question_sha256"])
    duplicate_ids = [
        {"id": cid, "splits": sorted(owners)}
        for cid, owners in by_id.items() if len(owners) > 1
    ]
    duplicate_ids.sort(key=lambda x: x["id"])
    return {
        "split_sizes": counts,
        "question_overlaps": overlaps,
        "case_id_overlaps": duplicate_ids,
        "disjoint": not overlaps and not duplicate_ids,
        "scope": "Exact normalized text/ID audit only; paraphrases and corpus leakage not detected",
    }


def require_disjoint_question_splits(splits: Mapping[str, list[dict]]) -> dict:
    """Fail closed before benchmark evaluation when exact split leakage exists."""
    report = audit_question_splits(splits)
    if not report["disjoint"]:
        raise ValueError("Evaluation splits overlap in normalized questions or case IDs")
    return report
