# Release and live deployment evidence — 1.1.17-private.13

Status: GREEN
Workstream: `upstream-1-1-18-alignment`
Release: `v1.1.17-private.13`
Release source commit: `b416b32a2cbd3ac1d47a9f9ea3ff9fd4ca62cbdd`
Release PR: #8
Release workflow: run #10, id `35501549265`

## Publication

- The user explicitly authorized the release/version bump, tag/GitHub Release publication, and live deployment.
- PR #8 prepared synchronized release metadata for `1.1.17-private.13` and advanced release-version regression expectations.
- PR #8 CI completed GREEN before merge.
- Merge to `main` produced `b416b32a2cbd3ac1d47a9f9ea3ff9fd4ca62cbdd`.
- The repository Release workflow completed GREEN on that exact commit.
- The published prerelease tag is `v1.1.17-private.13`.
- Published assets are exactly:
  - `codex_workflow-1.1.17-private.13.zip`
  - `SHA256SUMS`
- Release workflow verification passed runtime regression, package validation/build/archive verification and published-release readback.

## Live deployment

Target: `chatgpt-ce-workstation`
Selected project wrapper: `/home/codex/Documents/ChatGPT/ogolny`

- Installed shared runtime before update: `1.1.17-private.12`.
- Installed shared runtime after update: `1.1.17-private.13`.
- Project wrapper state after update: `1.1.17-private.13`.
- Selected compute profile remained `muse-max`.
- Installed worker set readback: Archivist, Default Executor, Explorer, Investigator, Senior Executor, Tester.
- Retired Companion and Micro Executor worker definitions were removed by the ownership-aware updater.
- Installed package validator returned `valid: true` for version `1.1.17-private.13`.
- Transactional backup was created at `/home/codex/.codex/codex_workflow/.backups/1.1.17-private.12-20260920T091133754806Z`.
- Updater reported no warnings.

## Result

Release publication and the authorized live deployment are complete. No further release/integration/deployment obligation remains for this scope.
