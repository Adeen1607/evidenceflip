"""Dependency-free, adapter-driven counterfactual evidence evaluation."""
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable
import hashlib
import json
import re

@dataclass(frozen=True)
class Evidence:
    id: str
    text: str

@dataclass(frozen=True)
class Answer:
    text: str
    citations: tuple[str, ...] = ()

@dataclass(frozen=True)
class Scenario:
    name: str
    question: str
    evidence: tuple[Evidence, ...]
    expected_text: str | None = None
    expected_citations: tuple[str, ...] | None = None
    expect_abstention: bool = False

@dataclass(frozen=True)
class Evaluation:
    scenario: str
    question: str
    answer: str
    citations: tuple[str, ...]
    checks: dict[str, bool]
    passed: bool

def verify_registry(root: str | Path, manifest: str = "sources/manifest.json") -> list[dict]:
    """Verify all manifest paths and SHA-256 digests. Never trust unchecked paths."""
    root = Path(root).resolve()
    entries = json.loads((root / manifest).read_text(encoding="utf-8"))["sources"]
    results = []
    for entry in entries:
        target = (root / entry["path"]).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"Source escapes repository root: {entry['path']}")
        if not target.is_file():
            results.append({"id": entry["id"], "valid": False, "reason": "missing"})
            continue
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        results.append({"id": entry["id"], "valid": digest == entry["sha256"], "expected": entry["sha256"], "actual": digest})
    return results

def evaluate(scenario: Scenario, agent: Callable[[str, tuple[Evidence, ...]], Answer]) -> Evaluation:
    """Execute one controlled scenario and report each independent assertion."""
    if len({e.id for e in scenario.evidence}) != len(scenario.evidence):
        raise ValueError("Duplicate evidence IDs")
    response = agent(scenario.question, scenario.evidence)
    available = {e.id for e in scenario.evidence}
    checks = {"citations_available": all(c in available for c in response.citations)}
    if scenario.expected_text is not None:
        checks["expected_text"] = scenario.expected_text.casefold() in response.text.casefold()
    if scenario.expected_citations is not None:
        checks["expected_citations"] = set(response.citations) == set(scenario.expected_citations)
    if scenario.expect_abstention:
        checks["abstained"] = bool(re.search(r"cannot determine|not enough evidence|don't know|insufficient evidence", response.text, re.I))
    return Evaluation(scenario.name, scenario.question, response.text, response.citations, checks, all(checks.values()))

def compare(baseline: Evaluation, intervention: Evaluation, should_change: bool) -> dict:
    changed = baseline.answer.strip() != intervention.answer.strip()
    return {"baseline": baseline.scenario, "intervention": intervention.scenario, "answer_changed": changed, "expected_change": should_change, "passed": changed == should_change}

def to_dict(result: Evaluation) -> dict:
    return asdict(result)
