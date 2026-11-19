# Labeled source-level retrieval evaluation

EvidenceFlip now provides `evaluate_ranked_sources` for source-level hit@k, mean reciprocal rank (MRR@k), precision@k and recall@k, plus a retriever adapter compatible with BM25 and optional sentence-transformer dense retrieval. It uses **explicit human or researcher relevance labels**, not an LLM judge. These are retrieval metrics, not claim faithfulness.

Install from your checkout: `python -m pip install -e .`. For dense retrieval install `python -m pip install -e ".[dense]"` and download the model separately with its license terms. This example uses project-authored synthetic labels under MIT and needs no model downloads.

```python
from pathlib import Path
from evidenceflip.rag import BM25Retriever, chunk_sources, load_sources
from evidenceflip.labeled_eval import collect_ranked_sources, evaluate_ranked_sources

root = Path(".")
sources = load_sources(root)
retriever = BM25Retriever(chunk_sources(sources))
question = "What does the refund policy say?"
labels = [{"id": "example-1", "question": question,
           "relevant_sources": ["refund-policy"],
           "retrieved_sources": collect_ranked_sources(retriever, question, k=3)}]
report = evaluate_ranked_sources(labels, k=3, known_sources=[s.id for s in sources])
print(report)
```

The synthetic example is a **smoke test, not a held-out benchmark**. For research, freeze your dataset, questions and judgments before model selection. Keep training/development and test questions separate; use the same corpus, labels, and k for BM25 and dense comparisons. Do not tune hyperparameters on the test set. Store corpus source hashes, label provenance, split IDs, seed, package/dependency versions, retrieval latency, model ID/license and hardware information with results. Source-level relevance is a coarser target than passage relevance; repeated chunks from one source are deduplicated. The denominator of precision@k is k even if fewer than k sources are returned, matching a fixed retrieval budget. Queries with no relevant sources are intentionally rejected rather than silently included in recall. Duplicate normalized questions are rejected within one evaluation batch, but this cannot detect semantic paraphrase leakage across splits.

The `collect_ranked_sources` adapter requests k **chunks**, then deduplicates sources. Consequently, it may return fewer than k distinct sources, and this must be held constant when comparing retrievers. It never runs a local LLM. Run `python -m unittest discover -s tests -v` to check regression coverage.

Research context: [Lewis et al., Retrieval-Augmented Generation (2020)](https://arxiv.org/abs/2005.11401), [Thakur et al., BEIR (2021)](https://arxiv.org/abs/2104.08663), and [Es et al., RAGAs (2023)](https://arxiv.org/abs/2309.15217). These motivate evaluating retrieval separately from generation and faithfulness.
