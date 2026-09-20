# Requirements

Revision: `R1`
Status: `approved`
Updated: `2026-09-20`

## Goal / target state

Evolve `elmakus/codex_workflow` from `1.1.17-private.12` into a simpler two-profile orchestration system that selectively adopts verified upstream 1.1.18 hardening while preserving the fork's Muse runtime and project-specific lifecycle guarantees.

The target architecture has six worker roles (Explorer, Investigator, Default Executor, Senior Executor, Tester, Archivist), two compute profiles (`plus`, `muse-max`), direct worker-to-Main communication, proportionate documentation intake, and a safer project-only update path.

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

## Constraints

- Existing Muse logical-session/process safety guarantees remain in force.
- Existing owner-release update channel and fork-specific release packaging remain authoritative unless a later accepted change explicitly modifies them.
- Upstream source is evidence/reference, not direct authority over fork behavior.
- Current source compatibility and regression evidence must constrain implementation detail during Planning/Execution.

## Non-goals

- Migrating to or owning upstream `[features.multi_agent_v2]` timeout settings.
- Reintroducing Medium route.
- Reintroducing Deployment Token Report.
- Preserving Companion or Micro Executor compatibility.
- Preserving `luna-xhigh` or `pro-x5` compatibility as supported profiles.
- Whole-repository synchronization with upstream 1.1.18.

## Global invariants

- Main retains architecture, routing, integration and final acceptance authority.
- Tester remains independent from the implementing worker for the bounded acceptance scope.
- Worker-to-worker communication is not required for correctness.
- A missing/unsupported Muse mid-turn message channel must not be emulated through polling or unmanaged background processes.
- Update operations must preserve unrelated user/project state and must not silently downgrade a project.
- Accepted project-local instructions are never inferred from stale workflow-owned route text.

## External contracts / dependencies

- Codex internal worker lifecycle is used by `plus`.
- Muse Code process/session adapter remains the worker runtime for `muse-max`.
- GitHub owner-release update mechanism remains the source channel for normal workflow updates.
- Python 3.11+ runtime expectations remain unchanged unless separately redefined.

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

## Definition completeness

- Target state and material MUST requirements are explicit.
- Constraints/non-goals/invariants are captured.
- Acceptance-level outcomes are defined enough to plan.
- Strategic choices needed before planning are accepted in `decisions/`.
- No unresolved user/product choice is known that can materially alter the target definition.

## Downstream coverage

Planning must map every requirement above to one or more milestones/work packages or a justified JIT trigger before execution begins.
