# Intake — release 1.1.18-private.2

Status: active
Workstream: `change-release-1-1-18-private-2`
Kind: `change`
Branch: `work/release-1-1-18-private-2`

## Authorized scope

The user explicitly authorized publishing the next owner release of `elmakus/codex_workflow` as `1.1.18-private.2`.

The release must package the already-reviewed and merged structured Muse capability-hint implementation currently on `main`. This intake does not authorize production Workstation deployment; that remains a separate live-write authorization boundary.

## Baseline and dependency classification

- Integration target: `main`.
- Exact branch base: `760a595125335411288cf3a673356ccdd8ea47af`.
- The structured Muse capability-hint implementation is already merged and terminal in its own workstream.
- No unmerged parent-only state is required.
- Classification: independent workstream.

## Existing authority

- `requirements/REQUIREMENTS.md` preserves the owner GitHub Release update channel.
- `planning/MASTER_PLAN.md` explicitly gates release-triggering VERSION changes behind user authorization; that authorization is now present.
- `decisions/DEC-005-fork-release-version-generation.md` requires later private-only changes on the aligned 1.1.18 generation to increment the suffix from `1.1.18-private.1` to `1.1.18-private.2`.
- `RELEASING.md` defines synchronized release metadata, verification, GitHub Actions publication, and installed-update boundaries.

## Intake classification

Pending post-creation route materialization. The expected smallest legal route is Execution Prep against the existing approved release authority; no new product Definition or strategic replanning is indicated by current evidence.
