# Intake — release 1.1.18-private.3

Status: complete
Workstream: `change-release-1-1-18-private-3`
Kind: `change`
Branch: `work/release-1-1-18-private-3`

## Authorized scope

The user explicitly authorized publishing the latest `elmakus/codex_workflow` `main` as the next owner release.

Under accepted version policy, the next private-only release on the aligned 1.1.18 generation is `1.1.18-private.3`.

This release packages the already-reviewed and merged current `main` source at branch base `6ce308a6dd7c92136ed01037800b61ba974d22b3`. This authorization does not include updating the production Workstation; that remains a separate live-write gate.

## Baseline and dependency classification

- Integration target: `main`.
- Exact branch base: `6ce308a6dd7c92136ed01037800b61ba974d22b3`.
- Current `main` Tests run #264 is GREEN on the exact branch base.
- All source/runtime changes being packaged are already merged to `main`; no unmerged parent-only state is required.
- Classification: independent workstream.

## Existing authority

- `requirements/REQUIREMENTS.md` preserves the owner GitHub Release update channel.
- `planning/MASTER_PLAN.md` gates release-triggering VERSION changes behind explicit user authorization; that authorization is satisfied by the current request.
- `decisions/DEC-005-fork-release-version-generation.md` requires later private-only changes on aligned generation 1.1.18 to increment the private suffix.
- `RELEASING.md` defines synchronized metadata, verification, GitHub Actions publication, and installed-update boundaries.

## Classification and continuation

- No new Product Definition, Research, or strategic replanning is required.
- Existing approved authority is sufficient for bounded release preparation.
- The exact execution contract is `implementation/workstreams/change-release-1-1-18-private-3/cards/M04-T01.md`.
- The canonical execution state is `implementation/workstreams/change-release-1-1-18-private-3/TASK_BOARD.yaml`.
- `M04-T01` is ready for execution.
- Independent Card review is RECOMMENDED before merge because merge triggers the externally visible tag/release.
- Workstream final-integration review is also RECOMMENDED and may reuse exact independent Card coverage only if the refreshed final subject remains identical.

Next route: `execution:M04-T01`.
