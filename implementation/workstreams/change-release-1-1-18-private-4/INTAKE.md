# Intake — release 1.1.18-private.4

Status: complete
Workstream: `change-release-1-1-18-private-4`
Kind: `change`
Branch: `work/release-1-1-18-private-4`

## Authorized scope

The user explicitly authorized publishing the latest `elmakus/codex_workflow` `main` as the next owner release.

Under the accepted downstream-fork release policy and DEC-005, the next private-only release on the aligned upstream 1.1.18 generation is `1.1.18-private.4`.

This release packages the already-integrated current `main` source at exact branch base `016a42ba0cf0d274bf12d718db6d7580abe54658`, including the completed Muse event-driven wait and quiet milestone orchestration work. The authorization covers release publication only; production Workstation update/deployment is excluded.

## Baseline and dependency classification

- Integration target: `main`.
- Exact branch base: `016a42ba0cf0d274bf12d718db6d7580abe54658`.
- Current package version before this workstream: `1.1.18-private.3`.
- Accepted Muse feature integration result: `916900f3e3536c896596b0618594e0b91aebefcc`.
- All source/runtime behavior being packaged is already merged to `main`.
- No unmerged parent-only state is required.
- Classification: independent workstream.

## Existing authority

- `requirements/REQUIREMENTS.md` preserves the GitHub owner-release channel and accepted Muse behavior.
- `planning/MASTER_PLAN.md` M06 boundary gate and §9 require separate explicit authorization before release-triggering VERSION/tag/Release writes; the current request satisfies that gate.
- `decisions/DEC-005-fork-release-version-generation.md` keeps this release on the 1.1.18 private lane and increments the private suffix.
- `decisions/DEC-006-muse-event-driven-waiting.md` is part of the behavior being packaged.
- `RELEASING.md` defines synchronized metadata, verification, GitHub Actions publication and the installation boundary.

## Classification and continuation

- No new Product Definition, Research or strategic replanning is required.
- Existing approved authority is sufficient for bounded release preparation.
- Exact execution contract: `implementation/workstreams/change-release-1-1-18-private-4/cards/M06-R01.md`.
- Canonical execution state: `implementation/workstreams/change-release-1-1-18-private-4/TASK_BOARD.yaml`.
- `M06-R01` is READY.
- Independent Card review is RECOMMENDED before merge because merge triggers the externally visible tag/release.
- Workstream final-integration review is RECOMMENDED; Close may reuse exact independent Card coverage only if the refreshed integrated subject and whole acceptance surface are unchanged.

Next route: `execution:M06-R01`.
