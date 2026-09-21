# Requirements

Revision: `R3`
Status: `approved`
Updated: `2026-09-21`

## Goal / target state

Evolve `elmakus/codex_workflow` as a three-profile orchestration system that preserves the accepted six-role topology, selectively adopted upstream hardening and project-specific lifecycle guarantees, while adding a native-Codex Muse execution path without regressing the established `muse-max` orchestration semantics.

The accepted architecture retains six worker roles (Explorer, Investigator, Default Executor, Senior Executor, Tester, Archivist) and supports exactly three compute profiles: `plus`, external-CLI `muse-max`, and native-Codex `muse-native`. `muse-native` uses the native Codex worker lifecycle while targeting Muse Spark 1.3 Contributor at `max` reasoning through CLIProxyAPI backed by Muse/Meta OAuth. The new profile must preserve the higher-level quiet-orchestration, no-polling, freshness, independence, repair, bounded-package and direct-to-Main semantics of the current workflow while replacing only transport-specific `muse exec` machinery.

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
| REQ-011 | Historical R1 requirement: only `plus` and `muse-max` were supported after removing `luna-xhigh` and `pro-x5`. The legacy-profile removal remains valid, but the two-profile limit is superseded by REQ-030 / DEC-007. | MUST | DEC-002 | superseded |
| REQ-012 | Under `plus`, workflow workers MUST use the internal Codex worker lifecycle. | MUST | DEC-002 | accepted |
| REQ-013 | Under `muse-max`, all supported worker roles MUST use the retained Muse process/session lifecycle; there MUST be no internal Companion exception. | MUST | DEC-002 | accepted |
| REQ-014 | Historical R1 requirement: bounded Material Event Push was available only under `plus` and not under external `muse-max`. The `muse-max` prohibition remains valid; the `plus`-only limitation is superseded for native `muse-native` by REQ-039 / DEC-007. | MUST | DEC-003 | superseded |
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
| REQ-029 | The `plus` profile and its existing internal-worker wait/Material Event Push semantics MUST remain unchanged by the Muse Main orchestration-efficiency feature. | MUST | DEC-006 | accepted |
| REQ-030 | The only supported compute profiles MUST be `plus`, external-CLI `muse-max`, and native-Codex `muse-native`. `luna-xhigh` and `pro-x5` remain unsupported/removed. | MUST | DEC-007 | accepted |
| REQ-031 | Under `muse-native`, all six supported worker roles MUST use the native Codex worker lifecycle while Main remains the user-selected Codex model. Each role MUST target `muse-spark-1.3-contributor` with `max` reasoning through the configured CLIProxyAPI Muse/Meta OAuth route, and MUST fail closed rather than silently falling back to another model, effort, provider or direct billing route. | MUST | DEC-007 | accepted |
| REQ-032 | `muse-native` MUST preserve the existing higher-level role, Task ID, bounded capsule, direct-to-Main report, Explorer, Senior Executor, Tester and Archivist contracts; changing worker transport MUST NOT collapse or weaken those ownership boundaries. | MUST | DEC-001, DEC-007 | accepted |
| REQ-033 | `muse-native` MUST use the same quiet milestone orchestration semantics as `muse-max`: routine worker-start/wait/status/session/Git/liveness narration remains silent, while material phase changes, blockers, immediate risks/authorization needs, material scope/architecture changes and final results remain available under the existing communication contract. | MUST | DEC-006, DEC-007 | accepted |
| REQ-034 | Healthy `muse-native` worker execution MUST be awaited through native Codex worker wait/continuation semantics without Main-driven status/list/progress polling. A wait timeout or no-new-state result MUST NOT by itself justify polling, worker replacement, Main takeover or user-visible liveness commentary. | MUST | DEC-007 | accepted |
| REQ-035 | Ordinary `muse-native` follow-up and repair MUST resume the same owning native worker/thread when safe. A controlling freshness/independence requirement MUST create a genuinely fresh worker context, normally without inherited turns, and a failed resume MUST surface explicitly rather than silently relabeling a replacement as the prior worker. | MUST | DEC-007 | accepted |
| REQ-036 | `muse-native` MUST preserve independent verification: Tester MUST be distinct from the implementing Executor; an ordinary RED cycle MUST route focused findings to the same owning Executor for repair and then return the changed subject to the same independent Tester for a full recheck when that Tester remains safe/available. | MUST | DEC-001, DEC-007 | accepted |
| REQ-037 | Qualifying `muse-native` Investigator work MUST preserve the exact-three independent-lane contract. Native Codex concurrency MAY replace the external Muse batch helper, but parallel execution is allowed only for already-authorized independent lanes with safe ownership/workspace boundaries; the external helper's transport-specific max-8 cap MUST NOT become a native-profile product constraint. | MUST | DEC-001, DEC-007 | accepted |
| REQ-038 | Required MCP/tool and skill capabilities for `muse-native` MUST be exercised through the native Codex capability/configuration plane where available. Required capability absence MUST fail visibly. The feature MUST include live acceptance for the exact installed Codex MCP and skill behavior rather than assuming documented inheritance is sufficient. | MUST | DEC-007 | accepted |
| REQ-039 | `muse-native` MAY use the native Codex bounded Material Event Push path for BLOCKER / COURSE_CHANGE / CRITICAL_PARTIAL events, with the same no-routine-progress and no-sibling-messaging constraints as `plus`. External `muse-max` MUST remain outside that contract. | MUST | DEC-003, DEC-007 | accepted |
| REQ-040 | External-Muse transport mechanisms such as `runtime/muse_worker.py` subprocess invocation, Muse JSONL normalization, Muse session registry/lease, one-cell terminal-wait workaround, Muse-specific prompt/schema artifacts, raw-run retention and `--disable-sandbox` MUST NOT be required by `muse-native` solely for parity. Native Codex lifecycle, sandbox and worker identity replace those mechanisms unless live evidence proves a narrower compatibility shim is necessary. | MUST | DEC-007 | accepted |
| REQ-041 | `muse-native` cancellation, timeout, failure and recovery MUST be live-validated as safe: no silent worker/provider substitution, no incorrect continuation identity, and no relevant orphaned execution left by the workflow. | MUST | DEC-007 | accepted |
| REQ-042 | Muse/Meta OAuth credentials and subscription-account secrets used by `muse-native` MUST remain owned by CLIProxyAPI/its credential store and MUST NOT be copied into repository state, worker task capsules, generated documentation or normal Main-visible evidence. | MUST | DEC-007 | accepted |
| REQ-043 | Acceptance for `muse-native` MUST include live evidence for exact provider/model/effort identity, all six roles, quiet orchestration, multi-minute no-poll waiting, same-worker continuation, fresh-context creation, Executor/Tester independence and RED-repair-recheck, exact-three Investigator lanes, required MCP, required skill behavior, timeout/cancel/recovery, and an A/B task against external `muse-max`. | MUST | DEC-007 | accepted |
| REQ-044 | The `plus` and external `muse-max` profiles MUST remain behaviorally unchanged by introduction of `muse-native`; retirement or replacement of external `muse-max` requires a separate later accepted decision. | MUST | DEC-007 | accepted |

## Constraints

- Existing Muse logical-session/process safety guarantees remain in force for external `muse-max`.
- `muse-native` must preserve the behavioral guarantees in REQ-032 through REQ-044 without mechanically inheriting external Muse transport internals.
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
- Removing or retiring external `muse-max` in this feature.
- Reusing `muse_worker.py`, Muse session registry, Muse raw-run retention or the Code Mode one-cell workaround in `muse-native` merely for implementation symmetry.
- Treating documented Codex MCP/skills inheritance as sufficient proof without live acceptance.
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
- Quiet communication and inference suppression are distinct requirements: hiding user-visible text does not satisfy REQ-022/REQ-023 or REQ-033/REQ-034 if Main continues to sample/poll periodically.
- Transport mechanisms may differ by profile, but role authority, independence, freshness and decision-ready reporting semantics remain profile-independent unless an accepted decision says otherwise.
- No supported profile may silently substitute a different provider/model/reasoning allocation when its configured worker allocation is unavailable.

## External contracts / dependencies

- Codex internal worker lifecycle is used by `plus`.
- Muse Code process/session adapter remains the worker runtime for `muse-max`.
- Native Codex worker lifecycle is the worker runtime for `muse-native`.
- CLIProxyAPI is the required provider bridge for `muse-native` Muse access, using Muse/Meta OAuth-backed credentials; exact workstation endpoint/configuration is deployment/runtime configuration, not a repository secret.
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

1. Exactly `plus`, `muse-max`, and `muse-native` are selectable/supported profiles and no active code/docs/tests restore `luna-xhigh` or `pro-x5` as supported paths.
2. Companion and Micro Executor are absent from active worker/package/route contracts; Explorer is present with its accepted responsibility.
3. Investigator dispatch contract enforces three independent lanes for a qualifying bounded problem and direct reports to Main.
4. `plus` retains internal Material Event Push semantics; `muse-native` may use the same bounded native event classes; external `muse-max` has no such contract.
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
19. `muse-native` resolves all six worker roles to `muse-spark-1.3-contributor / max` through the configured CLIProxyAPI OAuth-backed provider with no silent fallback.
20. A healthy multi-minute `muse-native` worker run produces no Main-driven status/list/progress polling and no liveness-only commentary.
21. Same-worker continuation, fresh-worker isolation, independent Tester, RED → same Executor repair → same Tester recheck and exact-three Investigator behavior are demonstrated under the native lifecycle.
22. Required MCP and skill functionality is demonstrated live in the installed Codex environment or fails visibly without silent degradation.
23. Native timeout/cancel/recovery behavior is safe and preserves identity/provider correctness.
24. External `muse-max` remains available and unchanged, and at least one comparable A/B task can run through both Muse harness paths under the same higher-level acceptance contract.

## Definition completeness

- Target state and material MUST requirements are explicit.
- Constraints/non-goals/invariants are captured.
- Acceptance-level outcomes are defined enough to plan.
- Strategic choices needed before planning are accepted in `decisions/`.
- No unresolved user/product choice is known that can materially alter the target definition.

## Downstream coverage

Planning must map every requirement above to one or more milestones/work packages or a justified JIT trigger before execution begins. Historical requirements REQ-001 through REQ-029 retain their completed execution history except where REQ-011 and REQ-014 are explicitly superseded by this R3 definition. The current feature plan must directly cover REQ-030 through REQ-044 and preserve all non-superseded inherited authority.
