# M07 Handoff — native profile and provider foundation

Date: 2026-09-21
Workstream: `feature-muse-native-profile`
Milestone: `M07`
Status: `GREEN / checkpoint complete`

## Completed checkpoint

- M07-T01: done, independently reviewed GREEN.
- M07-T02: done, independently reviewed GREEN.
- Final functional implementation is present by `commit:b2291cc64210a15fb63cc1f05fccf08395e3193d`.
- Integrated acceptance: `implementation/workstreams/feature-muse-native-profile/evidence/M07-acceptance.md`.

## Achieved state

The fork now has exactly three compute profiles. `muse-native` renders all six workflow roles as native Codex workers using `muse-spark-1.3-contributor`, reasoning `max`, and the configured user-owned `cliproxyapi` provider route. Profile switching and update preserve unrelated user configuration, keep internal agents enabled for `plus` and `muse-native`, and keep external `muse-max` on its existing external transport with native agents disabled.

Provider validation fails closed before mutation when the required route is missing or incompatible. Provider/account setup remains external to repository ownership.

## Authority now in force

- `requirements/REQUIREMENTS.md` R3.
- `decisions/DEC-007-muse-native-profile.md` plus applicable DEC-001/002/003/006 constraints.
- `planning/MASTER_PLAN.md` R4.
- M07 Card implementation/review evidence and `implementation/workstreams/feature-muse-native-profile/evidence/M07-acceptance.md`.

## Downstream prerequisite

The installed workstation does not currently have the required authenticated `cliproxyapi` Codex provider route configured. M07 explicitly permits this precise environment blocker. OAuth-backed M08/M09 live acceptance remains gated on user-owned provider/account setup.

## Next durable start

Proceed to M08 Execution Prep from Master Plan R4. Use M07 GREEN as predecessor authority and split repository-local/static orchestration work from live OAuth-backed acceptance so executable work can proceed without weakening the later live gate. Do not pre-create transport interfaces that current native Codex behavior has not proven necessary.
