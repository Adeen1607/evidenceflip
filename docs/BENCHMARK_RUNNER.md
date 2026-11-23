# Labeled retrieval comparison (prelaunch)

Install: `python -m pip install -e .`. The following toy corpus and labels are project-authored synthetic MIT examples, **not a pretrained-model benchmark**.

```python
from evidenceflip.benchmark_runner import run_labeled_benchmark
from evidenceflip.rag import Source, chunk_sources, BM25Retriever
sources = [Source('a', 'Alpha is a fictional river.', license='MIT'), Source('b', 'Beta is a fictional mountain.', license='MIT')]
retriever = BM25Retriever(chunk_sources(sources, size=20, overlap=0))
splits = {'development': [{'id': 'dev', 'question': 'What is Alpha?'}], 'test': [{'id': 'test', 'question': 'Where is Beta?', 'relevant_sources': ['b']}]}
report = run_labeled_benchmark(splits, {'bm25': retriever}, known_sources=['a', 'b'], k=2)
print(report['retrievers']['bm25']['metrics'])
```

Pass another retriever implementing `search(question, top_k)` to compare against the same test questions. Optional dense dependencies: `python -m pip install -e '.[dense]'`. Record exact model ID/revision, license, corpus digests, seed, hardware and embedding configuration separately; this runner does not attest to them. It does not invoke a generator or download a model. Both retrievers receive a **k chunk** budget, and duplicate chunks are collapsed to source IDs. Thus fewer than k unique sources can be scored. Latency is per-query retrieval only, excluding model loading and indexing. Labels are supplied by the caller, not independently verified. Exact question split auditing does not detect paraphrases or corpus contamination. Do not generalize from toy data.

Tests: `python -m unittest tests.test_benchmark_runner -v` and `python -m unittest discover -s tests -v`.

Research context: [Lewis RAG](https://arxiv.org/abs/2005.11401), [BEIR](https://arxiv.org/abs/2104.08663), [RAGAs](https://arxiv.org/abs/2309.15217). Retrieval relevance is distinct from generated-answer faithfulness.

## Adapter preflight and failure behavior

Before executing **any** retrieval query, the runner now checks that every named adapter exposes a callable `search(question, top_k)` method. If a later adapter is missing that method, it raises `ValueError` naming the adapter and does not call an earlier retriever. This prevents wasted computation and misleading partially executed comparisons. Preflight checks the method shape only: an adapter can still raise during retrieval, return malformed hits, or depend on an unavailable model. Such failures propagate; no partial report is returned. Validate dependencies and model availability before starting costly experiments.

Regression tests include an invalid later adapter, a non-callable `search` attribute, and a valid two-adapter comparison. All fixtures are project-authored synthetic MIT examples. This is not evidence of real pretrained-model inference.
