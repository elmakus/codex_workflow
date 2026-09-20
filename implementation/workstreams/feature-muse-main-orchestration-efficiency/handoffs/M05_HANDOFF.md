# M05 Handoff — event-driven Muse wait boundary

Date: 2026-09-20
Workstream: `feature-muse-main-orchestration-efficiency`
Milestone: `M05`
Status: `GREEN / checkpoint complete`

## Completed checkpoint

- Accepted behavior subject: `commit:1c0c0bf073308b8e87c009652e1192422445862c`.
- M05-T01: done, independently reviewed GREEN.
- M05-T02: done, independently reviewed GREEN.
- Integrated acceptance: `implementation/workstreams/feature-muse-main-orchestration-efficiency/evidence/M05-acceptance.md`.

## Achieved state

`muse-max` now has an active Main-facing contract requiring each bounded Muse turn to remain inside one outer Code Mode `exec` cell, with initial `tools.exec_command` and subsequent same-session `tools.write_stdin` waits retained inside that cell. Healthy liveness alone does not re-enter Main; top-level polling, liveness timers/heartbeats and unmanaged background polling are explicitly rejected.

Live M05 evidence demonstrates a multi-minute real Muse run with zero periodic Main requests for the exact conversation during the healthy wait. Existing Muse session/recovery/cancellation regressions and unchanged-`plus` profile behavior remain GREEN.

## Authority now in force

- `requirements/REQUIREMENTS.md` R2.
- `decisions/DEC-006-muse-event-driven-waiting.md`.
- `planning/MASTER_PLAN.md` R3.
- M05 independent review evidence for both Cards.

## Exceptions / deferred scope

M06 still owns REQ-025/REQ-026 quiet milestone communication plus final integrated acceptance under that communication policy. Release-triggering VERSION changes, tag/GitHub Release and external deployment remain outside current repository-local authority and require separate authorization.

## Next durable start

Proceed to M06 Execution Prep from Master Plan R3. The JIT trigger is satisfied by M05 GREEN: contract the quiet-milestone communication/profile/docs work around the selected native one-cell wait path, preserving all M05 wait guarantees and unchanged-`plus` behavior.
