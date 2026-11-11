# EvidenceFlip

**A research-oriented RAG workbench for retrieval, grounded generation, and evidence interventions.**

EvidenceFlip lets you load a documented source corpus, ask a locally running language model questions about it, inspect exactly which passages were retrieved, and run controlled experiments to see how answers react when evidence changes. It combines a working RAG reference implementation with an evaluation harness rather than presenting a static chat mockup as an AI product.

> **Development preview.** Research examples are project-authored synthetic fixtures, not model training documents, licensed third-party articles, or proof of published scientific performance. The public portfolio launch is deliberately frozen until the 20-day development period is complete and the owner approves release.

## What works now

| Layer | Implementation | What is verified |
| --- | --- | --- |
| Source registry | UTF-8 source files, provenance metadata, SHA-256 checks | Tampering, duplicates, and unsafe paths rejected |
| Ingestion | Word-window chunking with configurable overlap | Stable source and chunk identifiers |
| Retrieval | Inspectable BM25 lexical ranking and optional sentence-transformer cosine retrieval | BM25 smoke benchmark and offline dense adapter tests |
| Generation | Local Ollama /api/chat adapter | HTTP contract tested with mocked responses |
| Attribution | Generated answer plus retrieved excerpts and citation identifiers | Unknown source IDs are flagged, not filtered |
| Interventions | Reindex from supplied evidence for each experimental scenario | Replacement and removal reach the generator |
| CI | Python compatibility checks and source verification | No Pages deployment in the prelaunch workflow |

No new foundation-model weights are trained or bundled. RAG uses an existing local language model, such as a model pulled through Ollama. The Python retrieval and benchmarking implementation has **no mandatory external dependencies**. Dense embeddings require an optional extra and separately obtained pretrained weights.

## Quick start: see real retrieval (no model required)

Python 3.10+:

\`\`\`bash
git clone https://github.com/Adeen1607/evidenceflip.git
cd evidenceflip
git checkout feature/dense-retrieval-20261111  # development preview, not released on main
python -m pip install -e .
evidenceflip-rag --root . retrieve "How many observations are in the Orion dataset?"
\`\`\`

Output contains source IDs, exact retrieved passages and BM25 scores. The example corpus currently holds **11 registered synthetic documents**, including research-methodology notes, an incident playbook, and a fictional dataset card.

## Bring your own research documents

Import a plain-text or Markdown document that you are permitted to store and redistribute. Declare its title, origin, and license explicitly:

\`\`\`bash
evidenceflip-rag --root . register \
  --file ./my-study.md \
  --id my-study \
  --title "My Study Notes" \
  --origin "Original notes written by the author" \
  --license "MIT"
\`\`\`

The command copies the file into \`sources/imported/\`, computes its SHA-256 fingerprint, and updates \`sources/manifest.json\`. Subsequent searches load and verify the imported document alongside the examples. Importing a file **does not** establish that its facts, license declaration, or scholarly conclusions are correct.

Only UTF-8 \`.md\` and \`.txt\` documents under 2 MB are supported for now. **Do not commit confidential, restricted, or third-party copyrighted papers without permission**. PDF parsing and larger research-corpus ingestion remain planned work.

## Ask a local language model

Install [Ollama](https://ollama.com/), pull a model appropriate for your machine, and ensure its local server is running:

\`\`\`bash
ollama pull llama3.2
evidenceflip-rag --root . ask "How many observations are in the Orion dataset?" --model llama3.2
\`\`\`

The RAG pipeline retrieves relevant source passages, sends **only those passages** as context to the configured local model, and returns an answer with citation IDs and the retrieval trace. Your model may still answer incorrectly, refuse, or invent citations; the framework does not silently label such behavior correct. Ollama must be running separately. A live-model accuracy benchmark has **not yet been performed**.

To target a different Ollama server, supply \`--ollama-url\`. Be careful with remote endpoints: supplied research documents would leave your machine.

## Optional semantic retrieval

BM25 is the default and needs no model. To compare it with pretrained
sentence-transformer cosine retrieval, install the optional dependency:

```bash
python -m pip install -e '.[dense]'
evidenceflip-rag --root . --retriever dense \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 \
  retrieve "How many observations are in the Orion dataset?"
```

The embedding model may be downloaded on first use. Review its model card and
license before running it. Dense similarity is **not** a calibrated measure of
evidence relevance and a nearest-neighbor hit does not prove a claim. The
offline CI tests use injected vectors, not real model weights. Read the
[BM25 versus dense tutorial](docs/DENSE_RETRIEVAL.md) for reproducible
comparison commands and interpretation cautions.

## Retrieval evaluation

\`\`\`bash
evidenceflip-rag --root . benchmark --set examples/retrieval_benchmark.json --top-k 3
\`\`\`

The benchmark has 11 **author-labeled, synthetic** question/source pairs, intended to test wiring and catch regressions. Hit@k and MRR@k measure retrieval ranking, **not answer accuracy or faithfulness**. Results on these documents are not evidence of generalization to BEIR or other research corpora.

## Counterfactual evaluation

The existing independent test-suite evaluator can operate with a real Ollama model instead of the deterministic reference agent:

\`\`\`bash
evidenceflip evaluate examples/refund_scenarios.json --ollama-model llama3.2 --output results.json
\`\`\`

It reruns the question with the original source, a removed policy, a replacement policy, and an irrelevant-source negative control. Each intervention **rebuilds retrieval from the provided evidence**, so the model cannot unintentionally reuse a hidden, unchanged index. In a stochastic model, a single changed answer is not proof of causation. Review the full test trace and repeat trials where necessary.

For deterministic CI smoke tests:

\`\`\`bash
python -m unittest discover -s tests -v
evidenceflip verify --root .
evidenceflip demo
\`\`\`

## Methodology and honest boundaries

EvidenceFlip follows three established ideas:

1. **Retrieval-augmented generation:** separate parametric model knowledge from retrieved source passages.
2. **Information retrieval evaluation:** use explicit relevance labels and ranking metrics, starting with a transparent BM25 baseline.
3. **Counterfactual and metamorphic testing:** hold the question constant while removing or changing evidence, then compare against preregistered expectations.

A matching SHA-256 digest proves **file consistency against the registry**, not factual truth. A valid citation identifier proves **source availability**, not claim-level entailment. A working RAG pipeline is not the same as a benchmarked or peer-reviewed research system.

Read [Research methodology](docs/RAG_RESEARCH.md), [Development plan](docs/ENGINEERING_PLAN.md), [Build log](docs/BUILD_LOG.md), and [Release policy](docs/RELEASE_POLICY.md).

## Research references

- Lewis et al., [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401), NeurIPS 2020.
- Thakur et al., [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663), 2021.
- Es et al., [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://aclanthology.org/2024.eacl-demo.16/), EACL 2024.

## Contribute

Use [CONTRIBUTING.md](CONTRIBUTING.md) to add a focused regression test, source ingestion format, retriever, generator adapter, benchmark, or scientific replication. Do not upload sensitive research data or redistribute copyrighted corpora without permission.

**License:** [MIT](LICENSE). **Current status:** active development. CI workflow has no Pages deployment job, but the repository's branch-based Pages publishing setting is unverified. Do not push to main or authorize a site launch.
