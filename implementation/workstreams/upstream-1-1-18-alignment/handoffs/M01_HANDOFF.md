# M01 cumulative handoff

Milestone: `M01 — project-only update and legacy-migration hardening`
Status: GREEN
Implementation checkpoint: `3f7aa3c67a564216a6095b5ad92a3db2589ef8a1`

## Achieved state

- Equal-version update can catch up an older project from installed verified target source without reacquiring the same release or replacing shared runtime state.
- Historical project-source resolution, multi-project catch-up and explicit downgrade protection remain intact.
- Project-only mutation/backup behavior is scoped to changed target-project files; already-current/no-entry cases avoid unnecessary mutation/backup.
- Legacy project-local instructions referencing removed Medium/Heavy route files fail closed unless explicitly reviewed replacement instructions are supplied.
- Reviewed local-instruction input is supported by bootstrap, install and update while managed/personalization/reserved-marker protections remain enforced.
- VERSION remains `1.1.17-private.12`; no release/publication action occurred.

## Authority now satisfied

- `planning/MASTER_PLAN.md#M01--project-only-update-and-legacy-migration-hardening`
- REQ-001, REQ-002, REQ-003, REQ-004, REQ-016, REQ-021
- `decisions/DEC-004-selective-upstream-adoption.md`
- `openspec/changes/m01-project-only-update/`
- `openspec/changes/m01-legacy-local-instructions/`

## Verification

- `M01-T01`: terminal GREEN with required independent review.
- `M01-T02`: terminal GREEN with required independent review.
- Integrated M01 acceptance: GREEN at `implementation/workstreams/upstream-1-1-18-alignment/evidence/M01-acceptance.md`.
- Final integrated runtime tree was verified by PR #7 run #67: runtime 97/97, Muse 33/33, Muse Max 7/7, compile/package/build/archive checks GREEN.

## Material exceptions / deferred work

None for M01. Workstream final-integration review and merge to `main` remain later workstream-level gates; M01 closes only as an internal workstream checkpoint.

## Next durable starting point

Proceed to JIT Execution Prep for approved M02 in `planning/MASTER_PLAN.md`, using this checkpoint as the predecessor. M02 owns worker-topology and role-contract reconciliation; it must not reopen M01 runtime/update semantics without new evidence requiring strategic reconciliation.
