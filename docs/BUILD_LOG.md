# EvidenceFlip build log

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
