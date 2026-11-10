# Interview guide

## 20-second pitch

I built EvidenceFlip, a DATA INTEGRITY framework that checks the integrity of source documents and tests whether an AI assistant actually reacts to changes in retrieved evidence.

## Methodology

I used counterfactual and metamorphic testing. I keep the question fixed, modify one source, and compare the resulting answer with a predefined expectation. I also use negative controls to detect unnecessary changes when irrelevant evidence is removed.

## Architecture

Source registry → hash verification → baseline evaluation → controlled interventions → assertions and citation checks → audit report.

## Key distinction

The project checks integrity of retrieved evidence, not the private training data of an AI model. It identifies potential grounding problems, not definitive proof of hallucination or correctness.