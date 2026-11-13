"""Evaluate supplied human claim-support labels; no entailment model is run."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

LABELS = frozenset({"supported", "unsupported", "unanswerable"})


def evaluate_annotations(records: list[dict]) -> dict:
    """Score binary labels, excluding unanswerable gold and predicted abstentions."""
    if not isinstance(records, list) or not records:
        raise ValueError("Expected a nonempty list of annotations")
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("Each annotation must be an object")
        rid, claim = row.get("id"), row.get("claim")
        sources = row.get("retrieved_source_ids")
        gold, predicted = row.get("gold"), row.get("predicted")
        if not isinstance(rid, str) or not rid.strip() or rid in seen:
            raise ValueError("Annotation IDs must be nonempty and unique")
        seen.add(rid)
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError(f"Missing claim for {rid}")
        if not isinstance(sources, list) or not sources or any(
            not isinstance(s, str) or not s.strip() for s in sources
        ) or len(set(sources)) != len(sources):
            raise ValueError(f"Invalid retrieved source IDs for {rid}")
        if gold not in LABELS or predicted not in LABELS:
            raise ValueError(f"Invalid label for {rid}")
        if gold == "unanswerable":
            counts["excluded_unanswerable_gold"] += 1
            continue
        if predicted == "unanswerable":
            counts["predicted_abstentions"] += 1
            continue
        key = ("tp" if gold == predicted == "supported" else
               "tn" if gold == predicted == "unsupported" else
               "fp" if predicted == "supported" else "fn")
        counts[key] += 1
    tp, fp, fn, tn = (counts[k] for k in ("tp", "fp", "fn", "tn"))
    def ratio(numerator: int, denominator: int) -> float | None:
        return round(numerator / denominator, 4) if denominator else None
    return {
        "method": "human_labeled_binary_support_v1",
        "total": len(records),
        "scored": tp + fp + fn + tn,
        "excluded_unanswerable_gold": counts["excluded_unanswerable_gold"],
        "predicted_abstentions": counts["predicted_abstentions"],
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": ratio(tp, tp + fp),
        "recall": ratio(tp, tp + fn),
        "f1": ratio(2 * tp, 2 * tp + fp + fn),
        "warning": "Only evaluates supplied labels; does not infer support or verify annotator quality.",
    }


def evaluate_file(path: str | Path) -> dict:
    """Read local JSON annotations without any network calls."""
    return evaluate_annotations(json.loads(Path(path).read_text(encoding="utf-8")))
