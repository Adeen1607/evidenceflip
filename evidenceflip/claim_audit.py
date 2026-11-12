"""Conservative, deterministic citation-coverage audit for generated RAG answers.

Coverage is NOT semantic entailment or factual faithfulness. A known citation
only identifies a retrieved source; a human or separate evaluator must verify
that its text actually supports the associated claim.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable

from .rag import CITATIONS, RAGResult

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\[])")
_CLAIM_TEXT = re.compile(r"[A-Za-z0-9]")
_ABSTENTION = re.compile(
    r"^(?:insufficient evidence(?: in the indexed sources)?|"
    r"i (?:do not|don't) know|cannot determine|not enough information)"
    r"[.!\s]*$", re.IGNORECASE
)


@dataclass(frozen=True)
class ClaimAudit:
    text: str
    cited_sources: tuple[str, ...]
    unknown_citations: tuple[str, ...]
    retrieved_citations: tuple[str, ...]
    has_retrieved_citation: bool


def audit_answer(answer: str, retrieved_source_ids: Iterable[str]) -> dict:
    """Check whether each non-abstaining sentence cites retrieved evidence.

    Splits on sentence-ending punctuation followed by whitespace and an
    uppercase letter, digit or citation. This heuristic is deliberately
    inspectable and may mis-segment abbreviations, bullet points, or prose.
    """
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Answer must be a nonempty string")
    available = set(retrieved_source_ids)
    if any(not isinstance(sid, str) or not sid for sid in available):
        raise ValueError("Retrieved source IDs must be nonempty strings")
    claims: list[ClaimAudit] = []
    for line in answer.splitlines():
        for part in _SENTENCE_END.split(line.strip()):
            sentence = part.strip()
            if not sentence or not _CLAIM_TEXT.search(CITATIONS.sub("", sentence)):
                continue
            if _ABSTENTION.fullmatch(sentence):
                continue
            cited = tuple(dict.fromkeys(CITATIONS.findall(sentence)))
            known = tuple(sid for sid in cited if sid in available)
            unknown = tuple(sid for sid in cited if sid not in available)
            claims.append(ClaimAudit(sentence, cited, unknown, known, bool(known)))
    covered = sum(claim.has_retrieved_citation for claim in claims)
    return {
        "method": "heuristic_sentence_citation_coverage_v1",
        "claims_total": len(claims),
        "claims_with_retrieved_citation": covered,
        "citation_coverage": round(covered / len(claims), 4) if claims else None,
        "uncited_claims": [claim.text for claim in claims if not claim.cited_sources],
        "unknown_citation_claims": [claim.text for claim in claims if claim.unknown_citations],
        "claims": [asdict(claim) for claim in claims],
        "warning": "Citation coverage is not entailment, factual correctness, or faithfulness.",
    }


def audit_result(result: RAGResult) -> dict:
    """Audit an actual pipeline result against only its retrieved source IDs."""
    return audit_answer(result.answer, (hit.chunk.source_id for hit in result.hits))
