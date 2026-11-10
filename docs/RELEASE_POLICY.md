# EvidenceFlip release policy

## DATA INTEGRITY first, public launch last

**Current status: development-only.** The owner has requested a 20-day engineering cycle from November 11 through November 30, 2026, followed by a deliberate final portfolio launch. No GitHub Pages publishing or redeployment is authorized during this cycle.

### Allowed before launch

- Implement and test core Python evaluation features, adapters, examples, and source-provenance checks.
- Improve documentation, onboarding, issue templates, tests, benchmark methodology, and reproducibility.
- Develop website code under `site/` and review it locally without publishing.
- Run scheduled or push-triggered CI that installs, tests, verifies hashes, and records audit artifacts.
- Record meaningful commits and dated verification notes in `BUILD_LOG.md`.

### Not allowed before launch

- Enable a new GitHub Pages deployment job or invoke `actions/deploy-pages`.
- Publish a production website or publicly announce the project as production-ready.
- Treat synthetic demonstration outputs as production model accuracy metrics.
- Generate filler changes to satisfy an arbitrary daily commit count.

### Final launch gate

After the full development period has ended, request the repository owner's **explicit final approval**. Prior to publishing, confirm:

1. Supported installation instructions are proven on a clean environment.
2. CI and source-integrity checks pass on the launch commit.
3. API examples and adapters have runnable tests, including failure cases.
4. Source attribution, licensing, security guidance, and evaluation limitations are accurate.
5. Portfolio claims match reproducible output, not mock metrics.
6. GitHub Pages is then configured to deploy only after successful CI on the approved release.
7. A versioned release summary and known limitations have been prepared.

**Important historical note:** A Pages deployment succeeded before this embargo was introduced. Removing the Pages deployment workflow does not automatically unpublish that older site. The account owner may unpublish it from Settings → Pages if it should be inaccessible until launch.
