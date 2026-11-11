"""Optional sentence-transformer cosine retriever with inspectable chunk traces.

The encoder can be injected for offline, deterministic tests. Production usage
requires the separately installed ``sentence-transformers`` optional extra.
"""
from __future__ import annotations

import math
from typing import Protocol, Sequence

from .rag import Chunk, Hit


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class Encoder(Protocol):
    def encode(self, texts: list[str]) -> Sequence[Sequence[float]]: ...


class SentenceTransformerEncoder:
    """Lazy adapter; selecting BM25 never imports or downloads model weights."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("Embedding model name must be nonempty")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Dense retrieval requires the optional dependency: "
                "python -m pip install -e '.[dense]'"
            ) from exc
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> Sequence[Sequence[float]]:
        if not texts:
            return []
        return self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()


def _unit_vector(vector: Sequence[float], dimension: int | None = None) -> tuple[float, ...]:
    try:
        values = tuple(float(x) for x in vector if not isinstance(x, (str, bytes, bool)))
        if len(values) != len(vector):
            raise ValueError("Embedding components must be numeric")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Embedding must be a finite numeric vector") from exc
    if not values or any(not math.isfinite(x) for x in values):
        raise ValueError("Embedding must be a nonempty finite vector")
    if dimension is not None and len(values) != dimension:
        raise ValueError("Embedding dimensions do not match the index")
    magnitude = math.hypot(*values)
    if magnitude == 0 or not math.isfinite(magnitude):
        raise ValueError("Embedding must have nonzero finite magnitude")
    return tuple(x / magnitude for x in values)


class DenseRetriever:
    """In-memory cosine search. Scores are similarities, not evidence confidence.

    All indexed chunks are considered, including negative-similarity matches.
    Unlike BM25, nearest-neighbor search cannot certify that a query has no
    relevant evidence. Review returned excerpts before treating them as support.
    """

    def __init__(self, chunks: list[Chunk], encoder: Encoder):
        self.chunks = list(chunks)
        self.encoder = encoder
        raw = encoder.encode([chunk.text for chunk in self.chunks]) if self.chunks else []
        if len(raw) != len(self.chunks):
            raise ValueError("Encoder returned the wrong number of document vectors")
        self.vectors: list[tuple[float, ...]] = []
        self.dimension: int | None = None
        for vector in raw:
            normalized = _unit_vector(vector, self.dimension)
            self.dimension = len(normalized)
            self.vectors.append(normalized)

    def search(self, question: str, top_k: int = 3) -> list[Hit]:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        if not question.strip() or not self.chunks:
            return []
        encoded = self.encoder.encode([question])
        if len(encoded) != 1:
            raise ValueError("Encoder must return exactly one query vector")
        query = _unit_vector(encoded[0], self.dimension)
        hits = [Hit(chunk, round(sum(a * b for a, b in zip(query, vector)), 8))
                for chunk, vector in zip(self.chunks, self.vectors)]
        return sorted(hits, key=lambda hit: (-hit.score, hit.chunk.id))[:top_k]
