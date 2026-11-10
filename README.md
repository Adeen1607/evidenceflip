# EvidenceFlip | DATA INTEGRITY for AI Evidence

**DATA INTEGRITY** is the central focus: traceable evidence, verifiable source files, and counterfactual evaluation of AI answers.

EvidenceFlip tests whether a retrieval-augmented generation (RAG) assistant responds appropriately when evidence is changed, removed, or left untouched as a negative control.

## How it works

1. Register evidence documents in `sources/` with metadata and SHA-256 fingerprints.
2. Verify that the documents match their registered fingerprints.
3. Ask an AI assistant a question with the original evidence.
4. Replace or remove one document while keeping the question unchanged.
5. Evaluate answer changes, citation IDs, and predefined expectations.
6. Record an auditable report for review.

**Important:** This evaluates evidence sensitivity and source-file integrity, not whether a model's hidden training corpus is accurate or whether a citation necessarily supports a claim. Example source documents are synthetic retrieval-time fixtures, not claimed training data.

## Local project

The full Python framework, tests, examples, documentation, and interactive demonstration are being transferred into this repository. Until all files are present, use the previously supplied project archive for local execution.

## Interview summary

> I built EvidenceFlip, a DATA INTEGRITY framework for evidence-grounded AI systems. It registers and fingerprints source documents, performs controlled counterfactual interventions, and checks whether model answers and citations behave as expected. The objective is reproducible and auditable evaluation of RAG systems.

MIT License.