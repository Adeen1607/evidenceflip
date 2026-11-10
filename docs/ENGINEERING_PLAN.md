# EvidenceFlip engineering plan

**Objective:** Earn open-source trust by shipping a reproducible **DATA INTEGRITY** evaluation toolkit and an impressive but accurate public demonstration.

**Delivery window:** 20 scheduled development runs, November 11–30, 2026, at 02:00 America/Toronto. The repository CI is intentionally scheduled daily beyond this 20-day development window so regressions can still be detected.

**Prelaunch release freeze:** Throughout the full development window, GitHub Pages deployment and public site publication are out of scope. Site assets can be developed and tested locally, but they must not be deployed. Final public launch may happen after the 20-day development period, only with the owner's explicit go-ahead. See [RELEASE_POLICY.md](RELEASE_POLICY.md).

## Research and engineering gates

Every code change should pass this sequence before being described as complete:

1. **Research:** inspect existing code, current workflow and issue status, user need, relevant official documentation, and comparable evaluation tooling.
2. **Hypothesis:** articulate the failure mode, intended metric, acceptance test, and what the test cannot establish.
3. **Trial:** write or run a controlled fixture, regression test, or prototype; review invalid assumptions.
4. **Implementation:** make a scoped change with no secret data, no copied copyrighted corpora, and no unnecessary dependencies.
5. **Verification:** run local tests where possible, confirm GitHub Actions status, and record failure diagnostics honestly.
6. **Publication:** update README/docs/site, commit the result with a clear message, and log what was actually verified.

**Do not merge or claim release-readiness solely because a demonstration looks good.**

## 20-day progression

| Day | Date | Work focus | Acceptance gate |
| --- | --- | --- | --- |
| 1 | Nov 11 | CI status, Pages enablement, baseline cleanup | Source check and tests pass |
| 2 | Nov 12 | Make README and first-run tutorial beginner friendly | Fresh-clone instructions executable |
| 3 | Nov 13 | Implement source registry CLI diagnostics | Tampered fixture fails clearly |
| 4 | Nov 14 | Expand licensed synthetic sources and provenance | Manifest hashes independently verified |
| 5 | Nov 15 | Add multi-domain grounded fixtures | At least two distinct task domains tested |
| 6 | Nov 16 | Improve invalid-citation detection and tests | Fabricated citations not silently filtered |
| 7 | Nov 17 | Add structured JSON and exit-code contracts | Negative tests cover failures |
| 8 | Nov 18 | Build real adapter example with mock HTTP endpoint | Contract test has no paid API requirement |
| 9 | Nov 19 | Add local retrieval adapter example | Evidence intervention reaches agent |
| 10 | Nov 20 | Evaluate instability across repeated trials | Variability disclosed in reports |
| 11 | Nov 21 | Add HTML evaluation report from actual run output | Report reflects machine-generated results |
| 12 | Nov 22 | Improve interactive Pages accessibility | Keyboard and mobile checks |
| 13 | Nov 23 | Add CI badge and demo visuals | No fabricated deployment claims |
| 14 | Nov 24 | Add issue templates and maintainers' guide | Reproducible bug reports |
| 15 | Nov 25 | Add security, privacy, and unsafe input guidance | Adapters don't leak secrets in tests |
| 16 | Nov 26 | Cover malformed data and performance edges | Tests catch malformed inputs |
| 17 | Nov 27 | Validate compatibility matrix and installation | Python 3.10, 3.12, 3.13 pass |
| 18 | Nov 28 | Publish a reproducible benchmark with caveats | Synthetic data clearly labeled |
| 19 | Nov 29 | Polish interview/demo script, changelog, and FAQ | All demo claims supported |
| 20 | Nov 30 | Release review, backlog, documentation audit | Publish verified release notes or blockers |

Dates are **targets**, not claims of completed work. A critical bug takes priority over cosmetic tasks and may shift the plan.

## Definition of done

A feature is only complete when its code is committed, its expected behavior has an explicit test or manual reproduction, applicable CI results are recorded, and public-facing claims describe observed behavior.

## Key risks

- **False grounding claims:** source-ID checks cannot prove that a quoted claim is supported; use human review or clearly documented entailment tests.
- **Fixture quality:** synthetic cases may overstate performance on real LLMs; do not market them as real-world benchmarks.
- **Source provenance:** a fingerprint verifies consistency, not authorship, permission, or factual truth.
- **Evaluation leakage:** adapters must consume provided documents, not retrieve from a hidden original corpus.
- **Model nondeterminism:** single-trial changes can be caused by randomness; repeated trials and thresholds are planned.
- **GitHub Pages:** a workflow file is not an active site until the repository owner enables Pages and GitHub confirms a deployment.

## Ownership and auditability

Each daily run should document exact commit links, tests attempted, passing/failing checks, Pages state, and next-step decisions in [BUILD_LOG.md](BUILD_LOG.md). Avoid placeholder commits and inflated metrics.
