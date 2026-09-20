# M01 project-only same-version update

## Why

An already-current user-level runtime must be able to catch up an older project without reinstalling shared runtime state, downloading the same release again, or producing broad backups.

## Authority

- `REQ-001`–`REQ-004`, `REQ-021`
- `DEC-004`
- `planning/MASTER_PLAN.md` R2 / M01
- `implementation/workstreams/upstream-1-1-18-alignment/cards/M01-T01.md`

## Change

Add a distinct same-version project-only update plan and route the CLI to it when the selected/incoming release version equals the installed user-level runtime version.

The installed verified package is the target template authority for release-selected equal-version updates. Historical project source remains the comparison authority for projects that record an older workflow version.

## Non-goals

No legacy stale-route migration changes, worker/profile changes, release metadata changes, publishing, or wholesale upstream source adoption.
