"""Bridge counterfactual EvidenceFlip scenarios to the real local RAG pipeline."""
from __future__ import annotations

from typing import Callable

from .core import Answer, Evidence
from .rag import BM25Retriever, RAGPipeline, Source, chunk_sources


def make_rag_agent(generator: Callable[[str], str], *, top_k: int = 3,
                   chunk_size: int = 120, overlap: int = 20):
    """Build a new retriever from *supplied* evidence for each intervention.

    This is essential: reusing an unmodified corpus would defeat counterfactual
    tests because removing/replacing a document would never reach retrieval.
    """
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    def agent(question: str, evidence: tuple[Evidence, ...]) -> Answer:
        sources = [Source(item.id, item.text) for item in evidence]
        retriever = BM25Retriever(chunk_sources(sources, size=chunk_size, overlap=overlap))
        result = RAGPipeline(retriever, generator).ask(question, top_k=top_k)
        return Answer(result.answer, result.citations)

    return agent
