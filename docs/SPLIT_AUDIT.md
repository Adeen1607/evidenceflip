# Audit question split leakage before retrieval evaluation

EvidenceFlip's `audit_question_splits` detects repeated case IDs and **exact normalized question text** across named development/test partitions. `require_disjoint_question_splits` raises a `ValueError` if a collision is found, so benchmark scripts can fail closed before reporting scores.

Install with `python -m pip install -e .` from the checkout. This example is project-authored synthetic material under MIT:

```python
from evidenceflip.split_audit import require_disjoint_question_splits

splits = {
    "development": [{"id": "d1", "question": "How are refunds processed?"}],
    "test": [{"id": "t1", "question": "What evidence supports delivery?"}],
}
audit = require_disjoint_question_splits(splits)
print(audit["disjoint"], audit["split_sizes"])
```

For intentionally overlapping partitions, `audit_question_splits(splits)` returns `question_overlaps` as SHA-256 digests of normalized text and `case_id_overlaps` as IDs. This avoids repeating raw question text in the report, but **digests are not anonymization**: short/common questions can be guessed. Avoid publishing sensitive question sets or even their hashes without permission.

Normalization uses Unicode casefolding and whitespace collapse. This does **not** catch paraphrases, near-duplicates, shared passages between training and testing, document contamination, or tuning on test labels. It does not create a held-out dataset, run a model, or establish source licensing. Audit question authorship, source licenses, dataset splits, corpus overlap, and semantic leakage separately before claiming generalization.

Run `python -m unittest tests.test_split_audit -v` or `python -m unittest discover -s tests -v`. Relevant methodology: [BEIR](https://arxiv.org/abs/2104.08663), [Lewis et al. RAG](https://arxiv.org/abs/2005.11401), and [RAGAs](https://arxiv.org/abs/2309.15217).
