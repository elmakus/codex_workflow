# M03 cumulative handoff

Milestone: `M03 — two-profile execution and communication semantics`
Status: GREEN
Implementation checkpoint: `3e6f86cb78b54c8690b386d8575fc2647465eed3`

## Achieved state

- Supported compute profiles are exactly `plus` and `muse-max`.
- Under `plus`, all six supported workers use internal Codex lifecycle; under `muse-max`, all six use retained Muse logical-session/process lifecycle.
- Material Event Push is a plus-only internal-worker contract for `BLOCKER`, `COURSE_CHANGE`, and `CRITICAL_PARTIAL`, routed only worker -> Main.
- Active `muse-max` policy contains no unavailable-push/emulation pseudo-contract.
- Direct sibling messaging remains excluded; final/normal reports return to Main.
- Proportionate documentation intake and bounded Explorer discovery remain authoritative.
- Installed operator command dispatch exposes only the two supported profile forms.
- Workflow-owned `multi_agent_v2` timeout ownership remains absent.
- VERSION remains `1.1.17-private.12`; no release/publication action occurred.

## Authority now satisfied

- `planning/MASTER_PLAN.md#M03--two-profile-execution-and-communication-semantics`
- REQ-008, REQ-011, REQ-012, REQ-013, REQ-014, REQ-015, REQ-019, REQ-021
- `decisions/DEC-002-compute-profiles.md`
- `decisions/DEC-003-communication-context.md`
- `decisions/DEC-004-selective-upstream-adoption.md`

## Verification

- `M03-T01`: terminal GREEN with REQUIRED independent review.
- `M03-T02`: terminal GREEN with REQUIRED independent re-review of corrected subject.
- Integrated M03 acceptance: GREEN at `implementation/workstreams/upstream-1-1-18-alignment/evidence/M03-acceptance.md`.
- Final M03 subject is covered by GitHub Actions Tests run #155 plus exact-subject source/contract readback.

## Material exceptions / deferred work

- M04 owns the `workflow_break_down.md` -> `workflow_breakdown.md` rename, adapted benchmark/deep-dive documentation, residual documentation/reference cleanup, and integrated full-suite closure.
- Workstream final-integration review and merge to `main` remain later workstream-level gates.

## Next durable starting point

Proceed to JIT Execution Prep for approved M04 in `planning/MASTER_PLAN.md`, using this checkpoint as the predecessor. Release-triggering VERSION changes and publication remain explicitly gated and outside automatic authority.
