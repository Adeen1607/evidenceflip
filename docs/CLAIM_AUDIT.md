# Claim-level citation coverage (development preview)

EvidenceFlip's `ask` command now emits a `citation_audit` object alongside the answer and source trace. It checks **whether each heuristically segmented sentence has a citation to a source that was actually retrieved**. It does **not** decide whether the passage supports the sentence. A confidently false sentence citing a real document still counts as citation-covered.

## Try it

```bash
python -m pip install -e .
python -m unittest tests.test_claim_audit -v
ollama pull llama3.2
evidenceflip-rag --root . ask "How many observations are in the Orion dataset?" --model llama3.2
```

The `ollama` command and model download require local installation and are **not** run by CI. The returned JSON includes `citation_audit.claims`, `uncited_claims`, `unknown_citation_claims`, and `citation_coverage`. The denominator excludes recognized abstention sentences. When no assessable claims remain, coverage is `null` rather than a misleading perfect score.

For offline research or custom generators:

```python
from evidenceflip.claim_audit import audit_answer
print(audit_answer("Orion has 480 observations [dataset-card].", ["dataset-card"]))
```

## Interpretation and limitations

- A citation ID only shows that a retrieved source was named. **It does not establish factual support, entailment, relevance, or truth.**
- Sentence segmentation is a simple regex heuristic. Abbreviations, lists, Markdown, quotations, decimals, and unusual punctuation can create false positives or negatives.
- Unknown source citations are reported separately and never counted as covered. Multiple citations to the same source count once.
- No answer or document content is sent to a remote evaluator by this audit.
- This is an inexpensive screening signal to help researchers select claims for manual annotation. A future faithfulness study needs a licensed held-out corpus, human-reviewed claim/passage support labels, inter-annotator agreement, and explicit scoring of abstentions and partial support.
- A high citation coverage score is **not** a RAGAs faithfulness score and must not be advertised as one.

Background: [RAGAs (Es et al., EACL 2024)](https://aclanthology.org/2024.eacl-demo.16/), [RAG (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401), [BEIR (Thakur et al., 2021)](https://arxiv.org/abs/2104.08663).

All example source material is project-authored synthetic data with licenses declared in `sources/manifest.json`. Do not redistribute third-party research documents without authorization.
