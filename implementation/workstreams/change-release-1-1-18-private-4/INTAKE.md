# Intake — release 1.1.18-private.4

Status: active
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
- All source/runtime behavior being packaged is already merged to `main`.
- No unmerged parent-only state is required.
- Classification: independent workstream.

## Existing authority

- `requirements/REQUIREMENTS.md` preserves the GitHub owner-release channel and accepted Muse behavior.
- `planning/MASTER_PLAN.md` requires separate explicit authorization before release-triggering VERSION changes; the current user request satisfies that gate.
- `decisions/DEC-005-fork-release-version-generation.md` keeps this release on the 1.1.18 private lane and increments the private suffix.
- `decisions/DEC-006-muse-event-driven-waiting.md` is part of the behavior being packaged.
- `RELEASING.md` defines synchronized metadata, verification, GitHub Actions publication and the installation boundary.

## Intake continuation

The bounded release preparation does not require new Project Definition, Research or strategic replanning. Existing accepted authority is sufficient for direct Execution Prep.

Next route: `execution_prep:release-1.1.18-private.4`.
