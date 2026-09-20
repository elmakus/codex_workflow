# Release and live deployment evidence — 1.1.18-private.1

Status: GREEN
Workstream: `upstream-1-1-18-alignment`
Release: `v1.1.18-private.1`
Release source commit: `bdea9f2f457d7f91e43cfc06e9a6e58b903a7737`
Release PR: #9
Release workflow: run #11, id `35502669738`
Versioning authority: `decisions/DEC-005-fork-release-version-generation.md`

## Correction rationale

The completed workstream deliberately aligned the fork to the upstream 1.1.18 generation while preserving fork-specific divergence and selectively adopting upstream behavior. DEC-005 therefore defines the release SemVer core as the deliberately aligned upstream generation rather than the historical common source baseline.

The previously published `v1.1.17-private.13` remains immutable historical provenance. It is superseded by `v1.1.18-private.1`; its tag/release was not rewritten or deleted.

## Publication

- PR #9 changed current release metadata from `1.1.17-private.13` to `1.1.18-private.1`, updated release-version regression expectations, corrected provenance wording, and recorded DEC-005.
- PR #9 Tests run #215 completed GREEN before merge.
- Merge to `main` produced `bdea9f2f457d7f91e43cfc06e9a6e58b903a7737`.
- Release workflow run #11 completed GREEN on that exact commit.
- The published prerelease tag is `v1.1.18-private.1`.
- Published assets are exactly:
  - `codex_workflow-1.1.18-private.1.zip`
  - `SHA256SUMS`
- Release workflow runtime regression, package validation/build/archive verification and published-release readback all passed.

## Live deployment

Target: `chatgpt-ce-workstation`
Selected project wrapper: `/home/codex/Documents/ChatGPT/ogolny`

- Installed shared runtime before correction: `1.1.17-private.13`.
- Installed shared runtime after correction: `1.1.18-private.1`.
- Project wrapper state after update: `1.1.18-private.1`.
- Selected compute profile remained `muse-max`.
- Installed worker set readback: Archivist, Default Executor, Explorer, Investigator, Senior Executor, Tester.
- Installed package validator returned `valid: true` for version `1.1.18-private.1`.
- Transactional backup was created at `/home/codex/.codex/codex_workflow/.backups/1.1.17-private.13-20260920T093528716664Z`.
- Updater reported no warnings.

## Result

The release-generation numbering correction is complete. `1.1.18-private.1` is the current release and deployment for the completed upstream-1.1.18 alignment scope.
