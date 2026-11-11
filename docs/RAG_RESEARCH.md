# EvidenceFlip: RAG research and evaluation methodology

## Scientific objective

Build an **inspectable research workbench** for document-grounded question answering. The engineering goal is to separate and independently test (a) corpus fidelity, (b) retrieval quality, (c) generated responses, and (d) dependence on supplied evidence.

This is a software prototype, **not a claim of algorithmic novelty, peer review, or model superiority**. The current 11-document synthetic corpus and 11 question/source labels are a functionality check. They are not suitable for making broad empirical conclusions.

## Research foundations

- **RAG systems.** Lewis et al. (NeurIPS 2020) established the parametric plus non-parametric memory paradigm. EvidenceFlip implements a practical, non-differentiable retrieval-then-generate pipeline, not their end-to-end trained RAG architecture. https://arxiv.org/abs/2005.11401
- **Heterogeneous retrieval evaluation.** Thakur et al. (BEIR, 2021) show the importance of evaluating retrievers across diverse retrieval tasks and treat BM25 as a robust baseline. Our initial BM25 implementation is deliberately transparent. We **have not run BEIR**. https://arxiv.org/abs/2104.08663
- **RAG assessment.** Es et al. (RAGAs, EACL 2024) distinguish retrieval quality, context faithfulness, and answer relevance. Our current source-ID check does not implement or reproduce the RAGAs faithfulness metric. https://aclanthology.org/2024.eacl-demo.16/
- **Metamorphic testing.** The experimental pattern uses controlled source transformations and expected response relationships, supplemented by negative controls. These tests are diagnostics, not proof of a causal mechanism.

## Reproducible system architecture

\`\`\`text
Source files (.md, .txt)
    -> source manifest (path, provenance, license, SHA-256)
    -> verify original bytes (reject mismatch)
    -> word-window chunker (source ID, word offsets)
    -> BM25 retrieval OR optional pretrained dense cosine retrieval
       (rank and score top-k passages; scores not cross-model comparable)
    -> prompt with retrieved text and instruction boundary
    -> Ollama locally installed LLM (/api/chat, temperature 0)
    -> answer + citation IDs + invalid source IDs + retrieved passages
    -> retrieval evaluation / counterfactual test harness
\`\`\`

The model's actual training data are unknown. The corpus in \`sources/\` is **retrieved at inference time**, not claimed to be a training corpus.

### Default configuration

| Parameter | Default | Notes |
| --- | --- | --- |
| Word chunk size | 120 | Inspectable sliding window |
| Word overlap | 20 | Must be less than size |
| Retriever | BM25 | k1=1.5, b=0.75; optional sentence-transformer dense cosine search |
| Retrieval depth | top 3 chunks | Includes multiple chunks from same source when applicable |
| Generator | Ollama model selected by user | Default CLI model name: \`llama3.2\`; no weights included |
| Temperature | 0 | Does not guarantee complete determinism |
| Corpus | 11 project-authored fixtures | All synthetic and source-manifest-verified |

## Evaluation protocol

### Retrieval protocol

Given a query \(q_i\), a set of source documents, and a manually labeled relevant-source set \(R_i\):

- **Hit@k:** 1 if any of the first k *retrieved chunks* belongs to a relevant source, otherwise 0.
- **Reciprocal rank@k:** \(1/r_i\) where \(r_i\) is the rank of the first distinct retrieved source in \(R_i\), or 0 if none is found.
- **MRR@k:** mean reciprocal rank over all queries. Report k, the number of queries, the corpus revision, and retrieval configuration.

These metrics do not evaluate factual correctness of generated answers. Our initial benchmark contains terms strongly overlapping the documents. High scores are expected and should never be marketed as performance on unseen research questions.

### Optional dense retrieval and provenance

The opt-in dense adapter uses an external pretrained sentence-transformer
checkpoint and normalized cosine similarity, with the same chunk IDs and
source paths, SHA-256 digests, and declared licenses as BM25. The adapter
rejects empty, nonfinite, zero-length and inconsistent embeddings. Dense
nearest neighbors are **not** guaranteed to be relevant, and cosine scores
are not calibrated confidence. A small injected-vector unit test checks
semantic-style ranking without downloading weights; it is not an empirical
claim about any pretrained checkpoint. The CLI benchmark now records
retriever/model selection, source and label fingerprints, chunk settings,
Python/platform metadata, and retrieval-loop time (excluding model/index
initialization). No real embedding-model benchmark has yet been run.

See [the BM25/dense tutorial](DENSE_RETRIEVAL.md) for installation,
reproduction commands, data-rights cautions, and a held-out evaluation
protocol.

### Answer and source checks

- **Available citation ID:** a citation names one of the retrieved sources. This does not establish that the passage supports the generated claim.
- **Invalid citation ID:** model supplied a citation not included in retrieved evidence. Preserve and report it.
- **Abstention behavior:** missing supporting evidence should prompt an explicit statement of uncertainty.
- **Answer dependency:** controlled edits may or may not change the answer appropriately. An answer changing by itself is not success.
- **Negative control:** remove irrelevant evidence without changing relevant facts. The answer should often remain stable.

Counterfactual tests rebuild the retrieval index from the scenario's supplied evidence **each time**. This prevents an unchanged index from accidentally invalidating the intervention.

### Future controlled experiments (not yet run)

1. Evaluate BM25 and the new optional dense adapter on **the same** explicitly licensed corpus and held-out questions, then add a hybrid baseline.
2. Evaluate generation with and without retrieval using the same model, prompts, answer format, and compute budget.
3. Preregister answer-level expectations for source removal, source contradiction, distractor addition, and unchanged-evidence controls.
4. Repeat stochastic model trials and report both mean and variability, including confidence intervals when statistically justified.
5. Use human-reviewed claim-level support labels and inter-annotator agreement, not source IDs alone.
6. Test robustness to conflicting documents, misleading passages, prompt injection, missing attribution, and long contexts.
7. Document all model licenses, compute hardware, inference settings, source permissions and potential benchmark leakage.
8. Publish code, per-query traces, full failures, and negative findings. Do not discard runs that contradict the hypothesis.

## Threats to validity

| Threat | Mitigation or current limitation |
| --- | --- |
| **Synthetic corpus overfitting** | Small smoke test only; use separate held-out datasets before research claims |
| **Lexical bias** | BM25 matches query terms; the optional dense adapter exists but no pretrained embedding benchmark has been run |
| **Citation laundering** | Source-ID availability alone is not entailment, human claim review still required |
| **Model randomness** | Temperature 0 may vary across versions and hardware; run repeated trials |
| **Retrieval leakage** | Counterfactual adapter rebuilds from supplied documents |
| **Trust in registry** | SHA-256 ensures byte consistency, not authenticity, legality or correctness |
| **Prompt injection** | Source text treated as untrusted, but prompt instructions alone are not a security guarantee |
| **External validity** | Model backend is not exercised by CI; mocked adapter tests are not live-model benchmarks |
| **Data rights** | All project-authored research fixtures are synthetic; do not scrape copyrighted full papers |

## Reproducing today's engineering tests

\`\`\`bash
python -m pip install -e .
python -m unittest discover -s tests -v
evidenceflip verify --root .
evidenceflip-rag --root . retrieve "How many observations are in the Orion dataset?"
evidenceflip-rag --root . benchmark --set examples/retrieval_benchmark.json --top-k 3
\`\`\`

To test actual generation, install and run Ollama separately and record the full installed model tag, model digest, runtime version, model configuration, system environment, and response transcript. Do not confuse a successful mocked HTTP adapter test with a real model evaluation.

## Proposed publication standard

Before requesting external researchers to cite findings, provide an appropriate public dataset with permissions, transparent split definition, a strong retrieval baseline, a generation baseline, preregistered hypotheses, meaningful uncertainty estimates, shared scripts, and limitations. If these steps are not complete, present the project as research infrastructure rather than validated scientific results.
