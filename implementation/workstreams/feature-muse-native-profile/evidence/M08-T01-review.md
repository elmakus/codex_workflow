# Independent review — M08-T01

Card: `M08-T01 — Native orchestration contract materialization`
Review subject: `40283481eba7555a288f89b927c8aac51ba578ec`
Verdict: `GREEN`

## Reviewed authority

- `implementation/workstreams/feature-muse-native-profile/cards/M08-T01.md`
- `planning/MASTER_PLAN.md` R4 — M08
- `requirements/REQUIREMENTS.md` — REQ-032 through REQ-041 and REQ-044
- `decisions/DEC-007-muse-native-profile.md` with applicable inherited DEC-001/003/006 constraints
- `openspec/changes/muse-native-profile/specs/muse-native-profile/spec.md`
- accepted M07 checkpoint evidence and handoff
- `implementation/workstreams/feature-muse-native-profile/evidence/M08-T01.md`
- exact M08-T01 start subject `5befa4aa4ab80c4332b9fb73ecdfed0765fbb43c` and frozen subject `40283481eba7555a288f89b927c8aac51ba578ec`

## Verdict evidence

- The frozen subject is 11 commits ahead of the exact M08-T01 start state. Its functional surface is bounded to the five orchestration/installed-guidance documents plus focused profile/runtime regressions; no scheduler, provider, session, adapter or other production runtime implementation changed.
- The functional implementation is complete by `92975fedd29e198c292f6da072eebab546e2bc89`. The two commits from that implementation subject to the frozen review subject add only `evidence/M08-T01.md` and the M08-T01 OpenSpec task reconciliation, so no post-test functional-source drift is present.
- Heavy/delegation/project guidance binds all six `muse-native` roles to the normal native Codex lifecycle and retains the M07 Muse allocation/provider identity. External `muse-max` remains explicitly scoped to its separate adapter/session/one-cell-wait/capability-hint path.
- Native waiting is explicit: `wait_agent` timeout/no-new-state alone does not justify status/list/progress polling, replacement or Main takeover for `plus` or `muse-native`.
- Ordinary native continuation/repair stays on the owning worker/thread; freshness uses a new internal worker with `fork_turns="none"`; Tester remains distinct and the ordinary RED path returns to the owning Executor and then to the same independent Tester for full recheck.
- The existing exact-three Investigator contract remains profile-independent and applies to the native lifecycle used by `muse-native`: three independent lanes, distinct Task IDs, no sibling coordination/voting, direct evidence to Main, and concurrency only when ownership/workspace boundaries are safe.
- Material Event Push is generalized only to internal `plus | muse-native` workers for BLOCKER / COURSE_CHANGE / CRITICAL_PARTIAL under the existing no-routine-progress/no-sibling rules. External `muse-max` remains outside the internal `send_message` channel, matching DEC-007's explicit supersession of DEC-003's prior plus-only applicability clause.
- Native MCP/tool/skill guidance is explicit and fail-visible. `muse-native` is not routed through `MuseCapabilityHints`, `runtime/muse_worker.py`, copied capability bodies or silent provider/model/harness substitution; live installed-capability proof remains correctly deferred to the downstream M08 live Card.
- Installed dispatch/profile guidance exposes `muse-native`, keeps internal agents enabled for `plus` and `muse-native`, and explicitly forbids routing `muse-native` through the external Muse worker lifecycle.
- Independent source-level replay of the new focused text assertions against the immutable GitHub contents passes on the frozen subject and fails on the M08-T01 start state for the newly materialized lifecycle/no-poll/capability/material-event/installed-dispatch/profile contracts, establishing the intended pre-Card regression boundary.
- Durable implementation evidence records exact-subject verification on `92975fedd29e198c292f6da072eebab546e2bc89`: profile 15/15, runtime 101/101, Muse adapter 39/39, compile, validate, package build and archive verification GREEN. No PR-triggered GitHub Actions run is attached to the implementation/frozen subject, and the reviewer sandbox could not obtain a network checkout; therefore the full-suite execution result is accepted from the immutable implementation evidence rather than claimed as independently rerun here.
- No live OAuth/provider/account mutation or live lifecycle/MCP/skill success is claimed. The exact downstream live-acceptance boundary remains intact.

No review finding requires correction to the reviewed subject.

Verdict: `GREEN`.
