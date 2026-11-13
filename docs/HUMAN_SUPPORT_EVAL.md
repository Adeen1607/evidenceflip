# Human-labeled claim-to-evidence support evaluation (prelaunch)

EvidenceFlip now includes a **manual annotation scoring utility**, distinct from the heuristic citation-coverage audit. It computes binary precision, recall, F1 and confusion counts from **supplied human labels**, not from an LLM or a semantic entailment model. The tool does not infer labels or prove that claims are true.

## Acceptance criteria

1. Score supported versus unsupported claims with explicit TP, FP, FN, TN and null-safe precision, recall and F1.
2. Reject duplicate IDs, malformed source lists, missing claims and invalid labels.
3. Exclude gold `unanswerable` cases and predicted abstentions from binary scoring, with counts visible.
4. Work offline with a local JSON file, with no model download or external data transfer.
5. Test each failure mode and keep the publishing embargo.

## Beginner example

Create a file named `my_annotations.json` containing **your own reviewed annotations**:

```json
[
  {
    "id": "claim-001",
    "claim": "The synthetic Orion dataset contains 480 observations.",
    "retrieved_source_ids": ["dataset-card"],
    "gold": "supported",
    "predicted": "supported"
  }
]
```

Run:

```bash
python -m pip install -e .
python -m unittest tests.test_support_eval -v
python -c "import json; from evidenceflip.support_eval import evaluate_file; print(json.dumps(evaluate_file('my_annotations.json'), indent=2))"
```

The example above is **illustrative input**, not a validated held-out benchmark or evidence that an actual model made a prediction. `gold` should be assigned by a human reviewing the *exact retrieved passage* and its source. `predicted` must be obtained from an explicitly identified evaluator before any model-performance claim. The `retrieved_source_ids` field records the provenance references but this first version does not independently verify the manifest or hashes.

## Research protocol and interpretation

Annotators should see the claim, exact retrieved passage, source path/hash/license, and rubric. Record disagreement and adjudication separately, freeze a held-out set before evaluating, and report annotator agreement and sample sizes. Use `supported` only when the cited passage supports the whole claim, `unsupported` when it does not, and `unanswerable` when the case cannot be judged from the available evidence. Do not use this toy example to report accuracy or generalization.

Predicted `unanswerable` rows are excluded from precision/recall and counted separately. Consequently the binary scores are **conditional on answered cases**; always report coverage and abstentions, or a system could inflate apparent quality by abstaining. Undefined precision/recall/F1 are `null`, not 1.0.

Related literature: [Lewis et al., RAG](https://arxiv.org/abs/2005.11401), [BEIR](https://arxiv.org/abs/2104.08663), [RAGAs](https://aclanthology.org/2024.eacl-demo.16/). This implementation is a scoring foundation for human evaluation, **not RAGAs**.

**Release safety:** This work is on a feature branch. Do not merge to `main`, publish a site, or alter Pages settings until the owner verifies the Pages publishing gate and explicitly authorizes a launch no earlier than November 30, 2026.
