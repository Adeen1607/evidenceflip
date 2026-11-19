# EvidenceFlip build log

## 2026-11-19 · Labeled source-level retrieval evaluation (prelaunch)

**Inspection:** Reviewed prior draft PR #9 and implementation of `rag.py`, `retrieval_trace.py`, `trace_record.py`, its regression suite, package metadata and the 11-source MIT-labeled synthetic manifest. GitHub issues search returned no open issues. Previous head `f714d37` passed [GitHub Actions run 44255089808](https://github.com/Adeen1607/evidenceflip/actions/runs/44255089808) on Python 3.10, 3.12 and 3.13. This is evidence for the previous branch only. Research basis: Lewis RAG, BEIR and RAGAs, distinguishing retrieval judgments from generation faithfulness.

**Acceptance criteria defined before implementation:** Evaluate ranked source IDs against explicit labels using hit@k, MRR@k, precision@k and recall@k; support existing BM25/dense retriever protocol; reject unknown/duplicate IDs, repeated normalized questions and malformed labels; provide offline regression tests and an accessible tutorial without invented benchmark scores; do not push to any publishing branch or configure Pages.

**Implementation:** Added `evidenceflip/labeled_eval.py`, an adapter from chunk hits to ordered distinct source IDs, and validated per-case/aggregate retrieval metrics. Added nine project-authored MIT-licensed synthetic regression tests and [tutorial](LABELED_RETRIEVAL_EVAL.md). Evaluation does not automatically create held-out splits or human labels; researchers must supply and freeze these. No real pretrained embedding, Ollama generation or external benchmark was run.

**Verification:** Existing parent commit CI succeeded as linked above. New branch CI is pending/not yet confirmed; nine new tests are committed but must not be represented as passing until executed. No benchmark figures are reported.

**Commits:** [implementation](https://github.com/Adeen1607/evidenceflip/commit/138b8487f9170e8d1819b94d3b1285e4be98ee73), [tests](https://github.com/Adeen1607/evidenceflip/commit/8d4bb7d635338f475e427b209f574ec95db934bf), [tutorial](https://github.com/Adeen1607/evidenceflip/commit/11f52c4709b1dfdb240c83bc143d02145f3d40d9).

**Release safety:** Changes remain on `feature/labeled-retrieval-eval-20261119`, based on prior feature work. No main push or Pages deployment/configuration. Pages publishing source remains unverified disabled, so publishing-branch merges remain blocked. Public launch no earlier than November 30, 2026, after full development and explicit owner authorization.

**Next:** Verify branch CI and fix failures, then add a genuinely held-out, explicitly licensed human-labeled evaluation dataset and compare BM25 with actual dense inference under identical evaluation settings.


## 2026-11-18 · Versioned runtime metadata for BM25 replay records (prelaunch)

**Inspection:** Reviewed draft PRs #1–#8, `trace_record.py`, `retrieval_trace.py`, `tests/test_trace_record.py`, the 11-entry project-authored MIT-labeled synthetic source manifest and the existing tutorial. No open issues returned. PR #8 head `d87a0c3` has a successful [GitHub Actions run 44035214270](https://github.com/Adeen1607/evidenceflip/actions/runs/44035214270); this verifies the preceding branch only. Research context remains Lewis RAG, BEIR and RAGAs, which distinguish retrieval reproducibility from claim faithfulness.

**Acceptance criteria before implementation:** Add package/Python/retriever descriptors to the SHA-256-covered record without capturing sensitive host identifiers; preserve verification of old v1 records; reject malformed metadata and metadata tampering; report cross-environment mismatch without falsely rejecting successful replay; add regression tests and beginner documentation; keep main and Pages untouched.

**Implementation:** Version 2 records contain validated metadata under the content digest, while v1 remains readable. `environment_matches` is informational and never substitutes for source integrity and full replay. Expanded offline synthetic regression suite from eight to thirteen tests. Updated [tutorial](TRACE_RECORDS.md). No package version is claimed to identify a Git revision; no digital signature or historical attestation is implied.

**Verification:** Preceding branch CI succeeded as linked above. Today's new branch tests and GitHub CI must be checked independently before claiming success. No live Ollama, pretrained embeddings or external held-out benchmark was executed. No measured benchmark performance is claimed.

**Commits:** [implementation](https://github.com/Adeen1607/evidenceflip/commit/4bc012e17c1280c8d3a10540902cdd6ee33b4dfc), [tests](https://github.com/Adeen1607/evidenceflip/commit/12af78f40567bc575272a51d006f7cc0ef959345), [tutorial](https://github.com/Adeen1607/evidenceflip/commit/a86fd42923d2fbb91194cf163228235b5352dff8).

**Release safety:** Only `feature/trace-runtime-metadata-20261118`; no main push, Pages settings change or deployment. Pages branch publishing remains unverified, blocking main merges. Public launch after the full 20-day build, no earlier than November 30, 2026 and only with explicit owner authorization.

**Next:** Confirm today's CI, fix failures, add dependency/revision fingerprinting where reproducible, and prioritize licensed held-out retrieval evaluation and real local model runs.


## 2026-11-17 · Content-addressed portable retrieval records (prelaunch)

**Inspection:** Reviewed the current chained draft PRs, `retrieval_trace.py`, `rag.py`, synthetic source manifest, prior tests and CI. The November 16 head `eaedabf` has successful [GitHub Actions run 43821459713](https://github.com/Adeen1607/evidenceflip/actions/runs/43821459713); this does not establish today's branch status. No open issues were returned. Research framing follows Lewis RAG, BEIR and RAGAs: retrieval provenance and faithfulness are different questions.

**Acceptance criteria before implementation:** Portable canonical JSON and SHA-256 digest; reject altered records, fabricated scores even when rehashed, source changes, invalid schema and nonfinite JSON; preserve BM25 replay; add synthetic MIT-licensed tests, beginner documentation and honest limitations. No main push or Pages changes.

**Implementation:** Added `evidenceflip/trace_record.py` with `canonical_bytes`, `seal_trace` and `verify_trace_record`. Added eight offline regression tests and [trace record tutorial](TRACE_RECORDS.md). The SHA-256 digest is unkeyed and is not a signature or trusted historical attestation.

**Verification:** Prior branch CI succeeded as linked above. New branch CI requires independent confirmation; no local full-suite execution, real LLM inference, dense model execution, or external research benchmark is claimed. If today's CI fails, repair before merging.

**Release safety:** Work on `feature/content-addressed-traces-20261117` only. No main push, Pages configuration change, or deployment. Pages branch publishing remains unverified and blocks merging to main. Public launch no earlier than November 30, 2026 after full development and explicit owner authorization.

**Next:** Verify new CI, add package/retriever version identifiers to records, and develop licensed held-out retrieval evaluation.

## 2026-11-16 · Deterministic BM25 retrieval replay for annotated evidence (prelaunch)

**Inspection:** Reviewed draft PRs #1–#6, `rag.py` BM25 and chunking, source manifest (11 project-authored MIT-labeled synthetic examples), `chunk_support.py`, support-label evaluation, and existing CI. The preceding branch head `a3cedcc` has a successful [GitHub Actions run 43688189993](https://github.com/Adeen1607/evidenceflip/actions/runs/43688189993). No open issues were returned. Research framing remains Lewis RAG, BEIR and RAGAs: provenance, retrieval ranking and claim faithfulness are separate measurements.

**Acceptance criteria defined before implementation:** Re-run BM25 against SHA-256 verified registered sources; compare complete ordered top-k traces and scores; reject altered queries, fabricated ranks, wrong chunk settings, nonreturned annotated chunks, malformed traces and source tampering; retain existing human-label metrics; document limits; keep main and Pages untouched.

**Implementation:** Added `evidenceflip/retrieval_trace.py` with `capture_bm25_trace` and `evaluate_trace_bound_annotations`, eight offline regression tests, and [beginner tutorial](RETRIEVAL_TRACE.md). This advances from reconstructed chunk membership to *reproducible retrieval replay*, not historical run attestation. Fixtures are project-authored synthetic text with MIT declaration.

**Verification:** Preceding branch CI succeeded; new branch tests and CI must be independently checked. No actual Ollama, sentence-transformer weights, external benchmark or factual entailment evaluation is claimed. The deterministic replay does not prove a historical run occurred, and rankings may change with implementation versions.

**Commits:** [feature](https://github.com/Adeen1607/evidenceflip/commit/7ab68e7576fe96f82bde206c80a4814b48275149), [tests](https://github.com/Adeen1607/evidenceflip/commit/a1d47a7ea8274df7a6e487fdfe79381f8a3b79d6), [tutorial](https://github.com/Adeen1607/evidenceflip/commit/b262f5dc5f489278085aa0325eba7a4f9089cdee).

**Release safety:** Feature branch `feature/retrieval-trace-20261116` only. No main push, Pages configuration change or deployment. Pages branch publishing remains unverified and blocks merges. Public portfolio launch remains embargoed until after the full 20-day build, no earlier than November 30, 2026, with explicit owner authorization.

**Next:** Confirm CI and fix regressions, then add immutable/content-addressed retrieval run records and held-out licensed evaluation.

## 2026-11-15 · Deterministic chunk-bound annotation provenance (prelaunch)

**Inspection:** Reviewed the chained draft PRs #1–#5, existing SHA-256 source loader, word-window chunker, human-label scoring, six source-bound tests, and source-licensing conventions. No open issues were returned by the connected issue search. Research basis: Lewis RAG, BEIR and RAGAs. Previous source-bound branch CI remains to be independently checked.

**Acceptance criteria before changes:** Retain hash-verified source checks and human-label metrics; reconstruct chunks with explicit size/overlap; reject unknown chunk IDs, source/offset mismatch, excerpts outside the chunk, malformed mappings and tampered files; add offline regression tests and a beginner tutorial; leave main and Pages untouched.

**Implementation:** Added `evidenceflip/chunk_support.py` to validate exact excerpt membership in reconstructed chunks and match IDs and word offsets. Added seven offline regression tests in `tests/test_chunk_support.py` and [tutorial](CHUNK_BOUND_SUPPORT.md). Synthetic fixture is project-authored and declared MIT in its temporary manifest. This verifies deterministic chunk membership, **not** a logged retrieval event, semantic entailment, human-label quality or live model inference.

**Verification:** Code and tests committed; full GitHub CI for this new branch is pending independent confirmation. No synthetic accuracy, external benchmark, actual Ollama execution or sentence-transformer model execution is claimed. Any CI failure must be resolved before marking ready.

**Commits:** [implementation](https://github.com/Adeen1607/evidenceflip/commit/047e692941df09a692a23cc76c3f38f2e7277bfa), [tests](https://github.com/Adeen1607/evidenceflip/commit/483e4af2d30ab4e0162a13976f30efd25cc498de), [tutorial](https://github.com/Adeen1607/evidenceflip/commit/001aa721d8bd06b458d31d28192ddf836dac9c6e).

**Safety and next:** Feature branch `feature/retrieval-chunk-binding-20261115` only; no main push, Pages settings change or deployment. Pages branch publishing is still unverified and blocks merging. Next: verify CI, add saved retrieval-run trace attestation with immutable run metadata, then independently labeled held-out evaluation.


## 2026-11-14 · Source-bound human annotation provenance (prelaunch)

**Inspection:** Reviewed draft PRs #1–#4, active support evaluator, SHA-256-checked source loader, source licensing conventions, and the earlier CI. PR #4 head `575f4e3` has a successful [GitHub Actions run 43383419402](https://github.com/Adeen1607/evidenceflip/actions/runs/43383419402). That run covers the preceding branch, **not** today's changes. Literature context remains Lewis RAG, BEIR, and RAGAs.

**Acceptance criteria (before implementation):** Verify every annotated source against the registered manifest and its content hash; require a nonempty exact excerpt for each cited source; reject unknown IDs, mismatched passage keys, fabricated passages and tampered files; preserve scoring and abstention semantics; add offline tests and a beginner tutorial; do not touch main or Pages.

**Implementation:** Added `evaluate_bound_annotations` to the existing support evaluator, reusing `rag.load_sources` for source SHA-256 checks. Added six offline regression tests in `tests/test_bound_support.py` and [tutorial](PROVENANCE_BOUND_SUPPORT.md). Exact excerpt membership is an integrity check, **not** claim entailment, model faithfulness, retrieval-run attestation or independent validation of human labels. No pretrained weights or Ollama generation were executed.

**Verification status:** New tests were committed and require GitHub CI confirmation. Do not infer today's test success from the previous successful run. No new benchmark accuracy is claimed.

**Safety:** Changes remain on `feature/provenance-bound-support-20261114`, based on PR #4's branch. No main push, Pages settings change or deployment. Branch publishing is not verifiably disabled and therefore blocks main merges.

**Next:** Check CI for the new branch, resolve failures, bind annotations to retrieval-run chunk IDs/offsets, and design independent held-out human annotations with agreement measurement.

## 2026-11-13 · Human-labeled claim support scoring (prelaunch)

**Inspection and research:** Reviewed the active claim-audit branch and draft PR #3, source manifest (11 MIT-labeled project-authored synthetic fixtures), previous CI, and Lewis/BEIR/RAGAs methodology. Prior PR #3 commit `ff8479b` has successful [CI run 43172535522](https://github.com/Adeen1607/evidenceflip/actions/runs/43172535522). This confirms that earlier commit's CI result, not today's work.

**Acceptance criteria before implementation:** Offline scoring of human-labeled claim-to-evidence support; explicit TP/FP/FN/TN and precision/recall/F1; exclude and report unanswerable gold cases and predicted abstentions; reject malformed/duplicate records; add regression tests and a beginner tutorial; do not touch Pages or main.

**Implementation and decision:** Added `evidenceflip/support_eval.py` with `evaluate_annotations` and `evaluate_file`, five unit tests, and [human support tutorial](HUMAN_SUPPORT_EVAL.md). This is *manual label scoring*, not an entailment model. Undefined metrics are null and abstention counts are visible. Synthetic example labels do not constitute empirical model performance. The module currently does not verify source hashes or link annotations to exact passages, which is a next priority.

**Local test evidence:** Five new unit tests passed in an isolated Python 3 workspace using equivalent new module and test content, including confusion matrix, abstentions, malformed rows, no-positive-prediction metrics, and JSON file loading. Full repository and GitHub CI results for this branch must be checked independently; no real LLM or pretrained embedding inference was performed.

**Safety:** Created `feature/human-support-eval-20261113` from `feature/claim-citation-audit-20261112`. No pushes to main, Pages settings changes, or hosting deployment. GitHub Pages branch publishing remains unverified and blocks main merges.

**Next:** Verify this branch's CI, design a source-hash-bound annotation format and an independently labeled held-out set, and quantify inter-annotator agreement. Do not claim model faithfulness from these synthetic examples.


## 2026-11-12 · Claim-level citation coverage diagnostics (prelaunch)

**Research and acceptance criteria:** Reviewed the existing local RAG implementation, open PRs #1 and #2, the 11-source synthetic manifest, previous CI evidence, and Lewis/BEIR/RAGAs research context. Acceptance criteria: (1) identify uncited sentences and fabricated citation IDs, (2) count only retrieved citations as covered, (3) handle abstentions and empty-claim cases without claiming perfect faithfulness, (4) expose diagnostics in the real `ask` CLI, (5) provide offline regression tests and interpretation guidance, (6) keep all work off main and Pages undeployed.

**Implementation:** Added `evidenceflip/claim_audit.py`, eight offline unit tests, `citation_audit` JSON in the local Ollama `ask` response, and `docs/CLAIM_AUDIT.md`. This is **citation presence/coverage**, not claim entailment or RAGAs faithfulness. No LLM weights were executed and no new external corpus was acquired.

**Safety:** Pages branch publishing remains unverified. Changes are confined to `feature/claim-citation-audit-20261112`, based on the previous dense-retrieval feature branch. Do not push or merge to main. No Pages settings or deployment workflow were changed.

**Verification:** New tests and full CI require checking on the new PR; do not claim success until workflow completion. No benchmark accuracy or live LLM results are claimed.

**Next:** Validate the CI run, add claim/passage support annotation on a properly licensed held-out evaluation set, and consider precision/recall against human labels. Pages publishing safety gate remains unresolved.


## 2026-11-11 · Optional dense retriever with source traces (prelaunch)

**Research and plan before implementation:** Inspected the active `feature/local-rag-pipeline` code, manifest, open PR #1, CI workflow and recent run 42888644908 (all three Python matrix jobs successful), and prior RAG, BEIR and RAGAs research. Acceptance criteria: (1) real opt-in sentence-transformer encoder usable by retrieve/ask/benchmark, (2) deterministic injectable-vector tests with no model download, (3) reject malformed embeddings and keep stable rankings, (4) retain path/hash/license provenance on hits, (5) record reproducibility metadata in benchmark JSON, (6) preserve default BM25 and CI-only workflow.

**Implementation decision:** Introduce a lazy optional `sentence-transformers` adapter and an in-memory normalized cosine retriever. Keep the zero-dependency BM25 default. This is a pretrained embedding baseline, **not** new model training. Dense search returns nearest neighbors even when irrelevant; cosine scores are not evidence confidence. Add a tutorial covering licenses, synthetic data, held-out evaluation, and actual model reproducibility.

**Pre-push local trial:** Seven new offline acceptance tests passed in a local test workspace using the exact new dense/CLI blobs and a minimal compatibility stub for existing RAG interfaces. The test does **not** constitute a full repository test or a live sentence-transformer run. Full repository regression testing is delegated to GitHub CI and must be checked separately. No actual embedding checkpoint or Ollama model was executed.

**Safety:** The GitHub Pages branch-publishing configuration could not be verified through the available GitHub connector. Therefore, no push to `main` or publishing branch is authorized. Development is isolated on `feature/dense-retrieval-20261111` based on `feature/local-rag-pipeline`. The workflow remains CI-only and site files remain undeployed.

**Committed code:** [b6be11a](https://github.com/Adeen1607/evidenceflip/commit/b6be11ad9bffb505d42a31d6c260a23a8a160869). [Draft PR #2](https://github.com/Adeen1607/evidenceflip/pull/2) targets the existing feature branch only.

**GitHub CI evidence:** [run 42976498115](https://github.com/Adeen1607/evidenceflip/actions/runs/42976498115) completed **successfully** on 2026-11-11. Python 3.10, 3.12 and 3.13 each ran **44 tests** without failures; the source-hash audit, deterministic counterfactual demo, and author-labeled synthetic BM25 benchmark also passed. This confirms offline adapter behavior and existing regression checks, **not** execution of real sentence-transformer weights, an external scholarly benchmark, or Ollama inference. No detected regression in the executed suite. A subsequent documentation-only commit should be checked separately.

**Remaining work:** A licensed held-out corpus, actual dense-model measurements, claim-level support evaluation, PDF ingestion, and explicit owner approval before any site launch. Pages branch publishing remains unverified, so `main` is blocked.

## 2026-11-10 · Functional RAG research implementation (draft PR)

**Product decision:** EvidenceFlip must be a usable RAG workbench with a scientific evaluation path, not merely a data-integrity-themed demo website. Research utility, reproducibility, and accurate scope take priority over branding.

**Research consulted:** Lewis et al. (2020) on retrieval-augmented generation; Thakur et al. (2021) on heterogeneous retrieval and BM25; Es et al. (2024) on separate RAG evaluation dimensions; current Ollama \`/api/chat\` request contract. The methodology and links are recorded in [RAG_RESEARCH.md](RAG_RESEARCH.md).

**Hypothesis:** A real retrieved-evidence pipeline can be implemented with a transparent BM25 baseline and local LLM interface, while source removal and replacement still reach the generator when each intervention rebuilds retrieval.

**Implemented (feature branch, not main):**
- Registered 9 new project-authored synthetic documents and 11 author-labeled retrieval questions; 11 total registered documents.
- Verified source loading with SHA-256, manifest-path checks, duplicate-ID rejection, and UTF-8 limits.
- Added chunking, BM25 ranking, top-k passage traces, and source/offset metadata.
- Implemented local Ollama generation through the documented nonstreaming chat endpoint.
- Preserved model-generated citation IDs, including invented citations for detection.
- Built a counterfactual adapter that reindexes from the scenario's supplied context.
- Added document import from researcher-owned Markdown/text, with explicit license and provenance metadata.
- Added retrieval, ask, register, and benchmark CLI commands, and optional live Ollama mode to the counterfactual evaluator.
- Wrote regression tests and a detailed research methodology, replacing the hype-first README.
- Extended prelaunch CI to record a synthetic retrieval audit. No Pages deployment job was added.

**Local trials:** 23 tests passed (17 RAG-core tests, 2 counterfactual adapter tests, 4 source registration tests). Verified exact Git blob SHA parity for the tested \`rag.py\`, \`rag_cli.py\` (before later register addition), \`test_rag.py\`, manifest, and sample source files. Local \`retrieve\` and \`benchmark\` commands ran. The 11-query synthetic benchmark is **not** a research accuracy claim.

**GitHub CI:** PR checks on the feature branch completed successfully on Python 3.10, 3.12, and 3.13 after core RAG and registration changes: [workflow 42888351346](https://github.com/Adeen1607/evidenceflip/actions/runs/42888351346). Later documentation-only commits require checking their own status.

**Not performed:** Actual generation by installed Ollama weights, evaluations on external scholarly datasets, head-to-head retriever comparisons, claim-level entailment assessments, calibrated uncertainty intervals, or any site deployment.

**Review:** [Draft PR #1](https://github.com/Adeen1607/evidenceflip/pull/1). **Do not merge or deploy** until GitHub Pages branch publishing is disabled and the owner confirms the release process.

**Next engineering checkpoints:** Make a locally repeatable live-model benchmark; add a documented dense or hybrid retrieval baseline; create a permission-aware PDF ingestion path; use held-out domain-specific relevance labels; implement claim-level support evaluations and repeated statistical trials; quantify speed and memory use.


The purpose of this log is **auditability**: separate implemented work, tested behavior, and remaining blockers. Commit history is the source of truth for actual changes.

## 2026-11-10 · Launch embargo and CI-only change

**Decision:** The owner explicitly requested a private development period with no final GitHub Pages publication before the 20-day build is complete.

**Change:** Removed the `pages` deployment job and deploy-pages permissions from the GitHub Actions workflow, retaining tests, source-integrity verification, the audit artifact, and daily 02:00 America/Toronto CI. Commit: [4687d99](https://github.com/Adeen1607/evidenceflip/commit/4687d9969fc5f2a85c0da60176316a1249dbea6f).

**Automation:** Updated the 20-day build task to focus on real product usability, acceptance tests, licensing, and evidence-backed commits. Final launch remains gated behind development completion and explicit owner authorization.

**Previously deployed site:** An earlier deployment succeeded before this release freeze. Removing the deployment job prevents subsequent deployments from that workflow but does not retroactively unpublish the existing GitHub Pages site. Unpublishing the already-live site, if desired, requires changing repository Pages settings with an account that has admin access.

**Verification:** Awaiting a completed GitHub Actions run on the new CI-only workflow. Do not claim the existing Pages site is offline until its status is independently confirmed.

## 2026-11-10 · Engineering baseline and CI/CD setup

**Research:** Checked the existing connected GitHub repository, the prior local implementation, official GitHub Pages/Actions deployment guidance, the current source manifest, and the API's behavior for invalid citation IDs.

**Trials:** The previous full local framework passed 16 unit tests. On the live GitHub repository, the first Python CI matrix completed successfully on Python 3.10, 3.12, and 3.13. The Pages job failed in the \`configure-pages\` step because the repository had no Pages site enabled. This is a repository settings requirement, not a successful deployment.

**Implemented and committed:**
- Introduced a four-scenario JSON suite covering baseline evidence, removal, controlled replacement, and a negative control.
- Added Python regression tests for file hashes, tampering, path traversal, fabricated citations, controlled interventions, and CLI JSON output.
- Added a daily timezone-aware GitHub Actions CI/CD workflow (02:00 America/Toronto) with multi-Python tests and deterministic result artifacts.
- Corrected GitHub Actions interpolation syntax after inspecting the committed workflow.
- Fixed the OpenAI-compatible adapter to preserve fabricated citation IDs so integrity checks can detect them.
- Added license, citation metadata, contribution expectations, and repository hygiene files.
- Documented the research-first engineering gates and 20-day iteration plan.

**Verified:** GitHub Actions run [42882876400](https://github.com/Adeen1607/evidenceflip/actions/runs/42882876400) had three successful Python quality jobs. The overall run was **not successful** because Pages was not enabled. Follow-up runs must be checked separately.

**Manual action needed:** In repository **Settings → Pages**, select **GitHub Actions** as deployment source. Re-run the workflow after changing the setting, or push a subsequent commit. GitHub App tools available to this project cannot enable Pages administration settings.

**Limitations:** The site currently replays a deterministic demonstration; no hosted LLM or real training corpus is being verified. Existing tests are synthetic. Source fingerprints check file identity, not claim-level truthfulness.

## Future runs

Add a dated entry with a summary, commit links, verification evidence, failures, and next prioritized change. Do not claim an expected scheduled run happened unless its actual history is visible.
