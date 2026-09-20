# Requirements

Revision: `R2`
Status: `approved`
Updated: `2026-09-20`

## Goal / target state

Evolve `elmakus/codex_workflow` as a two-profile orchestration system that preserves the accepted six-role topology, selectively adopted upstream hardening and project-specific lifecycle guarantees, while making `muse-max` materially more efficient during long-running worker execution.

The accepted architecture retains six worker roles (Explorer, Investigator, Default Executor, Senior Executor, Tester, Archivist), two compute profiles (`plus`, `muse-max`), direct worker-to-Main communication, proportionate documentation intake and the existing safe update path. The R2 extension requires `muse-max` to wait on healthy Muse work without periodic Main-model sampling and to use a quieter, milestone-oriented user communication policy rather than either current routine orchestration chatter or the historical hard-silent mode.

## Product / system requirements

| ID | Requirement | Priority | Source / decision | Status |
|---|---|---|---|---|
| REQ-001 | Historical `.source_backup/<version>` project-source resolution and existing multi-project catch-up behavior MUST remain supported. | MUST | DEC-004 | accepted |
| REQ-002 | When the installed user-level workflow version already matches the selected release, update MUST use a project-only path that does not replace shared runtime/worker state. | MUST | DEC-004 | accepted |
| REQ-003 | Project-only update MUST avoid redundant current-release download, back up only existing target-project files that will change, and produce a true no-op with no new backup when the project is already current. | MUST | DEC-004 | accepted |
| REQ-004 | Existing explicit downgrade protection MUST remain effective, including when using the project-only path. | MUST | DEC-004 | accepted |
| REQ-005 | The supported worker set MUST be Explorer, Investigator, Default Executor, Senior Executor, Tester and Archivist. Companion and Micro Executor MUST be removed. | MUST | DEC-001 | accepted |
| REQ-006 | Explorer MUST own bounded read-only project-context discovery/mapping/evidence retrieval; Investigator MUST own bounded fault hypotheses, solution alternatives, feasibility and prior-art research. | MUST | DEC-001 | accepted |
| REQ-007 | Every bounded problem that requires Investigator MUST use exactly three independent Investigator lanes with one shared Problem ID, distinct Task IDs and complementary search angles; Main MUST compare evidence/disagreement rather than use voting. | MUST | DEC-001 | accepted |
| REQ-008 | Worker results MUST return directly to Main; direct sibling worker messaging MUST not be part of the workflow contract. | MUST | DEC-001, DEC-003 | accepted |
| REQ-009 | Worker report contracts MUST not impose fixed word-count ceilings; reports MUST be the smallest complete, evidence-linked, decision-ready result and reference bulky logs/diffs instead of reproducing them. | MUST | DEC-001 | accepted |
| REQ-010 | Senior Executor, Tester and Archivist responsibilities MUST remain available after topology simplification. | MUST | DEC-001 | accepted |
| REQ-011 | The only supported compute profiles MUST be `plus` and `muse-max`. `luna-xhigh` and `pro-x5` MUST be removed with their profile-specific code, tests, commands and documentation. | MUST | DEC-002 | accepted |
| REQ-012 | Under `plus`, workflow workers MUST use the internal Codex worker lifecycle. | MUST | DEC-002 | accepted |
| REQ-013 | Under `muse-max`, all supported worker roles MUST use the retained Muse process/session lifecycle; there MUST be no internal Companion exception. | MUST | DEC-002 | accepted |
| REQ-014 | Material Event Push MAY exist only for internal Codex workers under `plus`, using the existing bounded BLOCKER / COURSE_CHANGE / CRITICAL_PARTIAL semantics; it MUST NOT be specified or emulated for `muse-max`. | MUST | DEC-003 | accepted |
| REQ-015 | Documentation intake MUST remain proportionate to the current task. Mandatory complete session-level `agent_docs/` intake MUST NOT be introduced. Explorer SHOULD be used for bounded broader context discovery when that reduces Main context load. | MUST | DEC-003 | accepted |
| REQ-016 | Stale protected/project-local instructions that reference removed legacy workflow route files MUST fail closed and require explicitly reviewed local instructions rather than inferred migration. Reviewed `--legacy-local-instructions` support MUST apply consistently to bootstrap, install and update. | MUST | DEC-004 | accepted |
| REQ-017 | The repository MUST rename `workflow_break_down.md` to `workflow_breakdown.md` and reconcile references. | SHOULD | DEC-004 | accepted |
| REQ-018 | Relevant upstream benchmark/deep-dive documentation MUST be brought into the fork only after adaptation to the resulting fork architecture; it MUST NOT describe removed roles/profiles/routes as active. | SHOULD | DEC-004 | accepted |
| REQ-019 | This change MUST NOT adopt upstream's `multi_agent_v2` timeout values or otherwise change the fork's multi-agent version/timeout ownership. Existing `multi_agent = true` behavior remains the accepted baseline for this scope. | MUST | DEC-002 | accepted |
| REQ-020 | Medium route and Deployment Token Report MUST remain absent and MUST NOT be reintroduced by upstream alignment. | MUST | DEC-004 | accepted |
| REQ-021 | Upstream 1.1.18 MUST be adopted selectively by behavior; implementation MUST NOT depend on a wholesale upstream merge/cherry-pick. | MUST | DEC-004 | accepted |
| REQ-022 | Under `muse-max`, a healthy running Muse worker MUST NOT cause periodic Main/model sampling solely to determine whether the worker is still running. | MUST | DEC-006 | accepted |
| REQ-023 | Muse execution MUST expose a managed runtime-owned terminal/material-event wait boundary to Main; repeated Main-driven terminal/session status polling MUST NOT be the steady-state wait mechanism. | MUST | DEC-006 | accepted |
| REQ-024 | The efficient Muse wait path MUST preserve existing timeout/cancellation cleanup, logical-session binding, fail-closed resume/replacement semantics, Executor/Tester independence and private raw-artifact isolation. | MUST | DEC-006 | accepted |
| REQ-025 | `muse-max` user-visible orchestration MUST use a quiet milestone policy that suppresses routine worker-start/wait/status/session/Git bookkeeping and other operational narration that does not change user understanding or require action. | MUST | DEC-006 | accepted |
| REQ-026 | The quiet milestone policy MUST still surface blockers requiring user input, immediate risk/authorization needs and material scope/architecture changes, MAY surface concise user-meaningful phase transitions, and MUST preserve a normal final result. | MUST | DEC-006 | accepted |
| REQ-027 | A timer, heartbeat or liveness-only progress update MUST NOT by itself wake Main or create a model turn. | MUST | DEC-006 | accepted |
| REQ-028 | Acceptance MUST include a live multi-minute Muse run whose Codex-LB and Codex rollout evidence demonstrate no periodic Main inference during the healthy wait interval, excluding explicit user input or genuinely material runtime events. | MUST | DEC-006 | accepted |
| REQ-029 | The `plus` profile and its existing internal-worker wait/Material Event Push semantics MUST remain unchanged by this feature. | MUST | DEC-006 | accepted |

## Constraints

- Existing Muse logical-session/process safety guarantees remain in force.
- Existing owner-release update channel and fork-specific release packaging remain authoritative unless a later accepted change explicitly modifies them.
- Upstream source is evidence/reference, not direct authority over fork behavior.
- Current source compatibility and regression evidence must constrain implementation detail during Planning/Execution.
- Current Codex terminal execution has an initial shell-yield ceiling of roughly 30 seconds; the implementation must not assume that increasing `exec_command` yield alone can provide a model-free multi-minute wait.
- The first implementation candidate is a long-lived Code Mode cell that owns internal terminal waits; if live feasibility disproves that path, a dedicated managed wait surface is allowed only if it preserves the same accepted behavior and existing Muse safety semantics.

## Non-goals

- Migrating to or owning upstream `[features.multi_agent_v2]` timeout settings.
- Reintroducing Medium route.
- Reintroducing Deployment Token Report.
- Preserving Companion or Micro Executor compatibility.
- Preserving `luna-xhigh` or `pro-x5` compatibility as supported profiles.
- Whole-repository synchronization with upstream 1.1.18.
- Restoring the historical `luna-xhigh` hard-silent communication policy.
- Eliminating all Main turns around Muse work; dispatch, terminal integration and genuinely material decision turns remain valid.
- Changing `plus` orchestration semantics as part of this feature.
- Redesigning Muse logical-session identity, Executor/Tester independence or raw-artifact isolation unless separate evidence later reopens Definition.

## Global invariants

- Main retains architecture, routing, integration and final acceptance authority.
- Tester remains independent from the implementing worker for the bounded acceptance scope.
- Worker-to-worker communication is not required for correctness.
- A missing/unsupported Muse mid-turn message channel must not be emulated through polling or unmanaged background processes.
- Update operations must preserve unrelated user/project state and must not silently downgrade a project.
- Accepted project-local instructions are never inferred from stale workflow-owned route text.
- Healthy Muse liveness is runtime state, not a reason for Main-model inference.
- Waiting must remain event/terminal-driven from Main's perspective; an unmanaged background process plus Main polling is not an acceptable substitute.
- Quiet communication and inference suppression are distinct requirements: hiding user-visible text does not satisfy REQ-022/REQ-023 if Main continues to sample periodically.

## External contracts / dependencies

- Codex internal worker lifecycle is used by `plus`.
- Muse Code process/session adapter remains the worker runtime for `muse-max`.
- GitHub owner-release update mechanism remains the source channel for normal workflow updates.
- Python 3.11+ runtime expectations remain unchanged unless separately redefined.
- Current upstream Codex Code Mode provides per-cell yield control and long background terminal waits; these are implementation evidence, not authority to weaken the no-periodic-Main-sampling acceptance invariant.
- MCP Tasks/notification-style long-running-operation patterns are relevant architectural prior art but are not a required protocol dependency for this feature.

## Data integrity / idempotency / security constraints

- Equal-version current-project update must be idempotent and create no unnecessary backup/mutation.
- Project-only catch-up must preserve the installed shared runtime state.
- Legacy local-instruction migration must fail closed on ambiguous/stale workflow-owned route references.
- Historical-source validation must continue to reject missing/mismatched source backups.
- Removal of profiles/workers must preserve unrelated user-owned settings/workers/files.

## Acceptance-level requirements

Definition-level success requires that the implemented result can demonstrate:

1. Only `plus` and `muse-max` are selectable/supported profiles and no active code/docs/tests retain supported-path assumptions for `luna-xhigh` or `pro-x5`.
2. Companion and Micro Executor are absent from active worker/package/route contracts; Explorer is present with its accepted responsibility.
3. Investigator dispatch contract enforces three independent lanes for a qualifying bounded problem and direct reports to Main.
4. `plus` retains internal Material Event Push semantics while `muse-max` has no such contract.
5. No sibling worker messaging remains in active workflow contracts.
6. Project-only same-version update changes only the target project's required files/state, avoids redundant download/shared-runtime replacement, preserves downgrade protection and is a no-op when already current.
7. Stale legacy route imports fail closed across bootstrap/install/update unless reviewed local instructions are supplied.
8. Existing historical-source/multi-project update regressions remain GREEN.
9. `multi_agent_v2` timeout ownership is not introduced.
10. Documentation intake remains proportionate rather than mandatory-full-framework.
11. `workflow_breakdown.md` is canonical and documentation/benchmarks accurately reflect the resulting fork architecture.
12. Medium route and Deployment Token Report remain absent.
13. During a healthy multi-minute `muse-max` worker run, Codex-LB shows no periodic Main requests between dispatch and the terminal/material event, apart from explicit user input or another genuinely material wake event.
14. Codex rollout evidence for that run contains no Main-driven recurring `write_stdin` / Code Mode `wait` loop used only to observe worker liveness.
15. Muse timeout, cancellation, session-busy/fail-closed recovery, logical-session binding, Executor/Tester independence and private raw-artifact guarantees remain GREEN.
16. Routine `muse-max` operational narration is suppressed, while meaningful phase transitions remain available and blocker/risk/authorization/final communication remains visible.
17. No timer-based progress message wakes Main solely to say that work is still running.
18. `plus` behavior remains unchanged.

## Definition completeness

- Target state and material MUST requirements are explicit.
- Constraints/non-goals/invariants are captured.
- Acceptance-level outcomes are defined enough to plan.
- Strategic choices needed before planning are accepted in `decisions/`.
- No unresolved user/product choice is known that can materially alter the target definition.

## Downstream coverage

Planning must map every requirement above to one or more milestones/work packages or a justified JIT trigger before execution begins. Requirements REQ-001 through REQ-021 retain their already-completed R1/R2 execution history; the current feature plan must preserve them as inherited authority while directly planning REQ-022 through REQ-029.
