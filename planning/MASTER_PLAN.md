# Master Plan — Muse Main orchestration efficiency

Revision: `R3`
Status: `draft`
Updated: `2026-09-20`
Independent plan review: `RECOMMENDED`

> Planning organizes the approved Project Definition in `requirements/REQUIREMENTS.md` Revision R2. Accepted requirements and decisions remain authoritative.

## 1. Accepted target / canonical inputs

- Requirements: `requirements/REQUIREMENTS.md` — Revision R2, `approved`
- Accepted current-scope decision:
  - `decisions/DEC-006-muse-event-driven-waiting.md`
- Inherited accepted decisions:
  - `decisions/DEC-001-worker-topology.md`
  - `decisions/DEC-002-compute-profiles.md`
  - `decisions/DEC-003-communication-context.md`
  - `decisions/DEC-004-selective-upstream-adoption.md`
  - `decisions/DEC-005-fork-release-version-generation.md`
- Current-scope research: `research/muse-main-orchestration-efficiency.md` / `R-MUSE-MAIN-ORCH-01`
- Promotion provenance: `brainstorming/muse-main-orchestration-efficiency.md` — `muse-main-orchestration-efficiency@R1`
- Workstream: `feature-muse-main-orchestration-efficiency`
- Baseline: integrated/released `1.1.18-private.1` architecture with six supported worker roles and two supported compute profiles.

Historical requirements REQ-001 through REQ-021 and their R2 milestone history remain accepted and are not reopened by this plan. R3 adds execution strategy for REQ-022 through REQ-029.

## 2. Verified execution baseline

Research established:

- `muse_worker.py` already waits synchronously for Muse and is not itself responsible for Sol polling.
- The repeated Main cost occurs above the adapter in the current Code Mode command/session wait path.
- In one healthy roughly fourteen-minute Muse Executor run, the observed wait interval produced 24 additional GPT-5.6 Sol Medium requests costing about USD 1.934, with 99.82% aggregate cached input and minimal reasoning.
- Current unified `exec_command` initial yield is effectively capped around 30 seconds.
- Code Mode provides an outer long-lived cell abstraction, per-cell yield control and separate waits for running nested tools.
- Public prior art in Codex, Claude Code and MCP Tasks confirms that long-running tool waits should be owned by the harness/runtime rather than by repeated model polling.

## 3. Inherited non-goals / invariants / constraints

- Preserve all accepted REQ-001 through REQ-021 behavior.
- Preserve six-role topology and two-profile model.
- Preserve Muse timeout/cancel, logical-session binding, fail-closed resume/replacement, Executor/Tester independence and private raw-artifact isolation.
- Do not change `plus` semantics.
- Do not restore the historical hard-silent `luna-xhigh` communication policy.
- Do not treat hidden user-visible text as proof of inference suppression.
- Do not use an unmanaged background process plus Main polling as a substitute for event-driven waiting.
- Do not change release-triggering VERSION metadata or publish/release as part of this work without separate explicit authorization.

## 4. Milestones

### M05 — event-driven Muse wait boundary

- Outcome: one healthy `muse-max` worker invocation can remain runtime-owned for a multi-minute execution interval without periodic Main-model sampling.
- Requirement coverage: REQ-022, REQ-023, REQ-024, REQ-027, REQ-028.
- Dependencies: approved Definition R2 / DEC-006.
- Planned work packages:
  - build an isolated live probe for one long-lived Code Mode `exec` cell that launches and awaits a controlled long-running command;
  - prove that nested terminal-session waits can repeat inside that same cell without returning control to Main;
  - prove cancellation/interrupt teardown remains safe;
  - if the native probe is GREEN, implement the smallest `codex_workflow` orchestration surface that keeps the whole Muse launch/await lifecycle inside one Code Mode cell;
  - if the native probe is RED for a host/runtime limitation, activate the DEC-006 fallback: the smallest dedicated managed wait/tool/broker surface that exposes only terminal/material events to Main;
  - preserve existing Muse adapter/session/recovery behavior and add regressions for the chosen path.
- Stable acceptance:
  - an isolated healthy wait lasts at least two minutes with no Main request increase during the wait interval;
  - a real Muse worker run lasting at least several minutes shows flat Codex-LB Main request count from dispatch until terminal/material event, excluding explicit user input;
  - rollout evidence contains no recurring Main-driven terminal/session liveness loop;
  - the worker completes normally through the same logical Muse runtime contract;
  - timeout, cancellation and session-busy/fail-closed recovery remain GREEN;
  - no unrelated `plus` path changes.
- JIT trigger: if the native one-cell feasibility gate is RED, Execution Prep may materialize the accepted managed-wait fallback Cards from the exact failure evidence without returning to Definition, provided external behavior/invariants remain unchanged.
- Planning re-evaluation trigger: fallback requires materially different milestone ordering, a new cross-repository delivery dependency or a broader deployment strategy.
- Definition re-open trigger: eliminating periodic Main sampling would require changing accepted Muse safety semantics, `plus` behavior or the user-visible orchestration contract.
- Boundary gate: none for repository-local implementation/testing; external deployment or release remains separately gated.

### M06 — quiet milestone communication and integrated acceptance

- Outcome: `muse-max` becomes materially quieter for users while preserving useful phase visibility and proving the wait-cost invariant end to end.
- Requirement coverage: REQ-025, REQ-026, REQ-027, REQ-029 plus integrated acceptance for REQ-022 through REQ-028.
- Dependencies: M05 GREEN event-driven wait path.
- Planned work packages:
  - replace current normal-concise `muse-max` commentary with quiet milestone semantics;
  - suppress worker-start, waiting, session/recovery bookkeeping, Git bookkeeping, liveness-only and other routine operational narration;
  - retain concise user-meaningful phase transitions such as implementation-complete → independent-review and RED-review → repair;
  - retain mandatory blocker/risk/authorization/material-scope communication and normal final results;
  - ensure no timer-based progress message wakes Main solely for liveness;
  - reconcile README/profile/delegation/heavy-route/runtime guidance and focused tests;
  - run integrated Muse runtime/profile/regression coverage and the live Codex-LB/rollout acceptance run.
- Stable acceptance:
  - communication tests distinguish quiet milestone behavior from both current routine commentary and historical hard silence;
  - routine waiting/status/session/Git narration is absent;
  - meaningful phase-boundary, blocker/risk/authorization and final communication remain available;
  - no liveness timer creates a Main turn;
  - M05 live no-periodic-sampling gate remains GREEN under the final communication policy;
  - full affected `muse-max` runtime/profile tests and unchanged-`plus` regressions are GREEN.
- JIT trigger: exact Card split follows M05 result so documentation/profile changes target the actual selected wait surface.
- Planning re-evaluation trigger: integrated evidence shows the communication policy and runtime wait implementation must be sequenced differently while Definition remains valid.
- Definition re-open trigger: useful user visibility requires a materially different communication contract than DEC-006.
- Boundary gate: none for repository-local implementation/testing; external deployment or release remains separately gated.

## 5. Requirement coverage matrix

| Requirement | Coverage |
|---|---|
| REQ-001–REQ-021 | Historical accepted R2 milestones M01–M04; preserve as inherited regression authority, not reopened |
| REQ-022 | M05 — eliminate periodic Main sampling during healthy Muse wait |
| REQ-023 | M05 — managed terminal/material-event boundary |
| REQ-024 | M05 — preserve Muse safety/session/recovery invariants |
| REQ-025 | M06 — quiet milestone communication |
| REQ-026 | M06 — preserve meaningful phase/blocker/risk/final visibility |
| REQ-027 | M05/M06 — no timer/liveness-only Main wake |
| REQ-028 | M05/M06 — live Codex-LB + rollout acceptance |
| REQ-029 | M05/M06 — unchanged `plus` behavior |

## 6. Dependency / execution order

`M05 → M06`.

M05 establishes the actual wait transport before M06 rewrites communication and final integrated documentation/tests around it. The conditional native-first/fallback branch is already accepted by DEC-006 and therefore does not require a new product decision when triggered by exact feasibility evidence.

## 7. Verification strategy

Verification is layered:

1. isolated Code Mode long-cell probe;
2. cancellation/interrupt probe;
3. focused runtime/unit regressions for the selected wait path;
4. Muse session/recovery regressions;
5. profile/rendering/communication tests;
6. live multi-minute Muse invocation with Codex-LB request-count evidence;
7. matching Codex rollout/tool evidence proving absence of model-driven liveness polling;
8. unchanged-`plus` regression;
9. integrated repository test suite materially affected by the change.

Absolute USD cost is diagnostic evidence, not the pass/fail criterion. The pass/fail invariant is absence of periodic Main inference while healthy Muse work is merely still running.

## 8. Data integrity / idempotency / cancellation strategy

- One logical Muse worker invocation remains bound to one accepted session identity according to the existing registry contract.
- Repeated execution/recovery must not create duplicate workers merely to repair a wait transport.
- Cancellation must tear down the active runtime-owned wait and preserve existing process-tree cleanup.
- Session-busy and interrupted-worker reconciliation remain fail-closed.
- Raw Muse trajectory/log artifacts remain private and out of Main context.
- Communication suppression must not suppress a blocker/risk/authorization event that requires user action.

## 9. Explicit authorization boundaries

Current feature authority covers repository-local design, implementation, tests, live local workstation verification and PR preparation.

Separate explicit user authorization remains required before:

- changing release-triggering VERSION metadata for main integration;
- creating/publishing a tag or GitHub Release;
- any external/live deployment not already part of local verification.

## 10. OpenSpec / contract candidates

Execution Prep should consider one bounded behavior contract for the Main-facing Muse wait semantics if implementation spans multiple runtime surfaces or if the native/fallback mechanism creates a stable interface worth preserving.

Do not create a contract merely for documentation wording.

## 11. JIT / deferred decomposition

- M05 first Cards: isolated long-cell feasibility probe + cancellation proof.
- M05 later Cards: chosen wait-path implementation/regression, materialized only after the feasibility result.
- M06 Cards: communication/profile/docs + integrated live acceptance after M05 result is durable.
- No speculative fallback implementation Card is created before the native-path gate is known.

## 12. Fresh-context / review boundaries

This R3 plan materially changes execution strategy and adds new runtime behavior, so independent plan review is RECOMMENDED and practical.

The authoring chat must stop after freezing the exact R3 draft and pending review record. A fresh normal ChatGPT chat performs the independent plan review. GREEN returns to Planning for deterministic approval, then Execution Prep proceeds automatically because implementation is already authorized by the active feature workstream.

## 13. Pre-implementation planning audit

- Definition Complete: GREEN — requirements R2 approved; DEC-006 accepted.
- User/product blockers: none.
- Research uncertainty: native one-cell feasibility remains implementation evidence, but DEC-006 provides an accepted fallback so it does not block milestone architecture.
- Milestone structure: M05 establishes transport first; M06 layers communication and integrated acceptance.
- Requirement coverage: all REQ-022 through REQ-029 directly mapped; REQ-001 through REQ-021 retained as inherited regression authority.
- Safety: Muse session/cancel/recovery invariants are explicit acceptance gates.
- Cost metric: request-count flatness is authoritative; dollar cost is not.
- Overengineering: new broker/MCP infrastructure is not planned unless the smaller native path fails live.
- Authorization gates: repository-local work authorized; release/deployment remains gated.
- OpenSpec: deferred to Execution Prep based on actual selected surface.
- Remaining planning blocker: independent R3 plan review only.

## 14. Workflow references

- Workflow repository: `elmakus/chatgpt-codex-project-workflow`
- Workflow ref: `main`
- Policy: `chatgpt_only`
- Project Definition authority: `requirements/REQUIREMENTS.md` R2 + `decisions/DEC-006-muse-event-driven-waiting.md`
- Plan review lifecycle: `workflow/chatgpt_only/PLAN_REVIEW.md`

The Master Plan is not the live task tracker. Mutable execution state begins only after plan approval through Execution Prep.
