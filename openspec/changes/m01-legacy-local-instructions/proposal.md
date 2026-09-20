# M01 fail-closed legacy local-instruction migration

## Why

Legacy project instructions can retain workflow-owned route references that no longer exist. Importing those references as user-owned local policy would silently convert stale workflow text into accepted project instructions.

## Authority

- `REQ-016`, `REQ-021`
- `DEC-004`
- `planning/MASTER_PLAN.md` R2 / M01
- `implementation/workstreams/upstream-1-1-18-alignment/cards/M01-T02.md`

## Change

Use one central local-instruction resolver for bootstrap/install/update. It rejects missing legacy workflow-route references unless the operator supplies explicitly reviewed replacement instructions, and it validates the replacement before import.

Expose the existing reviewed-input mechanism consistently as `--legacy-local-instructions <file>` on bootstrap, install and update.

## Non-goals

No same-version project-only update redesign, worker/profile changes, release metadata changes, publication, or wholesale upstream source adoption.
