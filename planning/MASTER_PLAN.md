# Master Plan — codex_workflow upstream 1.1.18 selective alignment

Revision: `R1`
Status: `draft`
Updated: `2026-09-20`
Independent plan review: `RECOMMENDED`

> Planning organizes the already-approved Project Definition in `requirements/REQUIREMENTS.md`. Accepted requirements/decisions remain authoritative.

## 1. Accepted target / canonical inputs

- Requirements: `requirements/REQUIREMENTS.md` — Revision R1, `approved`
- Accepted decisions:
  - `decisions/DEC-001-worker-topology.md`
  - `decisions/DEC-002-compute-profiles.md`
  - `decisions/DEC-003-communication-context.md`
  - `decisions/DEC-004-selective-upstream-adoption.md`
- Relevant research/evidence: `research/upstream-1.1.18-audit.md`
- Promotion provenance: `brainstorming/upstream-1.1.18-alignment.md`
- Project baseline: fork `1.1.17-private.12` with Muse runtime/session lifecycle, owner-release updater, historical source backups, and existing multi-project update regression coverage.

## 2. Execution baseline

The current fork already:
- resolves older project workflow versions through historical `.source_backup/<version>`;
- can migrate multiple projects against their recorded historical source;
- has compute profiles `plus`, `luna-xhigh`, `pro-x5`, `muse-max`;
- has Companion and Micro Executor roles;
- routes most `muse-max` worker roles through the Muse adapter while Companion remains internal Codex;
- enables `[features] multi_agent = true` and intentionally removes workflow-owned `multi_agent_v2` settings;
- has Medium route and Deployment Token Report removed.

Execution must adapt selected upstream semantics to this baseline instead of importing upstream commits wholesale.

## 3. Inherited non-goals / invariants / external constraints

- Do not introduce upstream `multi_agent_v2` timeout ownership.
- Do not reintroduce Medium route or Deployment Token Report.
- Do not preserve supported compatibility for Companion, Micro Executor, `luna-xhigh` or `pro-x5`.
- Preserve Muse process/session safety properties and owner-release update behavior.
- Preserve explicit downgrade protection and unrelated user-owned state.
- Worker correctness must not depend on sibling messaging.
- Documentation intake remains proportionate rather than mandatory-full-framework.
- Implementation is selective semantic adoption, not a wholesale upstream merge.

## 4. Milestones

### M01 — project-only update and legacy-migration hardening

- Outcome: equal-version updates use a bounded project-only path and stale legacy route imports fail closed.
- Checkpoint: runtime/update lifecycle supports current-runtime project catch-up without replacing shared runtime state.
- Acceptance:
  - same installed/selected runtime version does not require release re-download when the installed source is authoritative;
  - older target project is updated from its recorded historical source;
  - only changed target-project files are backed up/mutated on project-only update;
  - already-current project returns a true no-op without creating a backup;
  - project-newer-than-incoming still requires explicit downgrade approval;
  - stale removed-route references in protected/local instruction input fail closed unless reviewed local instructions are supplied;
  - reviewed local-instruction override is accepted consistently by bootstrap/install/update;
  - historical-source and existing multi-project regression behavior remains GREEN.
- Requirement coverage: REQ-001, REQ-002, REQ-003, REQ-004, REQ-016, REQ-021.
- Dependencies: none.
- Inherited constraints / rationale: DEC-004; upstream behavior is adapted, not copied blindly.
- Planned work packages:
  - isolate project-only planning/backup behavior from shared-runtime update planning;
  - reconcile launcher equal-version flow so installed source can be reused safely;
  - extend local-instruction review plumbing and stale-reference validation;
  - add/adjust focused regression coverage for equal-version, downgrade, backup and stale-route behavior.
- JIT decomposition / deferred-detail trigger: exact Card split after Execution Prep reads current runtime/update tests and CLI call graph.
- Planning re-evaluation trigger: evidence shows project-only semantics cannot be isolated without changing accepted shared-runtime/update contract.
- Definition re-open trigger: required behavior would change owner-release source policy, downgrade authority, or historical-source guarantees.
- Boundary gate / explicit user authorization: none.

### M02 — six-role worker topology and investigation contract

- Outcome: active workflow/package topology contains only Explorer, Investigator, Default Executor, Senior Executor, Tester and Archivist, with direct reports to Main.
- Checkpoint: worker definitions, route/delegation contracts and package validation agree on one six-role topology.
- Acceptance:
  - Companion and Micro Executor are absent from active worker/package/route contracts;
  - Explorer exists and owns bounded project-context discovery/mapping/evidence retrieval;
  - Investigator owns fault/solution/feasibility/prior-art research;
  - every qualifying bounded Investigator problem requires exactly three independent lanes with shared Problem ID, distinct Task IDs and complementary angles;
  - Main compares returned evidence/disagreements rather than voting;
  - hard report word ceilings are removed in favor of smallest complete evidence-linked reports;
  - worker final results return directly to Main;
  - no active contract requires or permits direct sibling messaging;
  - Senior Executor, Tester and Archivist remain supported;
  - Medium route and Deployment Token Report remain absent.
- Requirement coverage: REQ-005, REQ-006, REQ-007, REQ-008, REQ-009, REQ-010, REQ-020, REQ-021.
- Dependencies: M01 checkpoint.
- Inherited constraints / rationale: DEC-001, DEC-004.
- Planned work packages:
  - add Explorer worker and package ownership;
  - remove Companion/Micro worker definitions and all topology references;
  - rewrite Investigator and worker reporting contracts;
  - reconcile Heavy/delegation/AGENTS/package validation/tests around the six-role topology.
- JIT decomposition / deferred-detail trigger: after M01 result, inspect exact worker/package reference graph and split non-overlapping cleanup from contract changes.
- Planning re-evaluation trigger: removal reveals a fork runtime dependency on Companion/Micro not represented in accepted baseline.
- Definition re-open trigger: preserving runtime correctness would require keeping either removed role as a supported concept.
- Boundary gate / explicit user authorization: none.

### M03 — two-profile execution and communication semantics

- Outcome: only `plus` and `muse-max` remain, each with one coherent worker-runtime/communication contract.
- Checkpoint: profile rendering, CLI, routing and tests expose no supported-path behavior for removed profiles.
- Acceptance:
  - `plus` and `muse-max` are the only selectable/supported compute profiles;
  - `luna-xhigh` and `pro-x5` code/tests/docs/commands are removed;
  - under `plus`, all workflow workers use internal Codex worker lifecycle;
  - under `muse-max`, all six supported worker roles use retained Muse logical-session/process lifecycle;
  - no internal Companion/profile exception remains;
  - Material Event Push exists only in the `plus` internal-worker contract for BLOCKER / COURSE_CHANGE / CRITICAL_PARTIAL and routes only worker → Main;
  - `muse-max` has no Material Event Push contract or emulation language;
  - proportionate documentation intake remains authoritative and Explorer is the bounded broader-context mechanism;
  - generated platform configuration continues to avoid workflow-owned `multi_agent_v2` timeout settings.
- Requirement coverage: REQ-008, REQ-011, REQ-012, REQ-013, REQ-014, REQ-015, REQ-019, REQ-021.
- Dependencies: M02 checkpoint.
- Inherited constraints / rationale: DEC-002, DEC-003.
- Planned work packages:
  - reduce compute profile registry/rendering/CLI to two profiles;
  - reconcile Muse role mapping/session adapter expectations for the six-role set;
  - remove obsolete profile-specific branches and regressions;
  - rewrite communication/context policy to plus-only material events and direct Main routing;
  - preserve platform-settings regression that rejects workflow-owned V2 timeout configuration.
- JIT decomposition / deferred-detail trigger: after M02 establishes final worker set, resolve exact profile maps and Muse adapter role enumeration.
- Planning re-evaluation trigger: retained Muse adapter cannot support Explorer or another accepted role without changing milestone ordering.
- Definition re-open trigger: correctness requires retaining a removed profile or introducing a new supported profile/communication model.
- Boundary gate / explicit user authorization: none.

### M04 — documentation, packaging and integrated regression closure

- Outcome: repository naming/docs/package metadata describe the resulting architecture and integrated regression evidence is GREEN.
- Checkpoint: canonical docs/package/test surface has no stale architecture references and the repository is ready for normal release preparation.
- Acceptance:
  - `workflow_breakdown.md` is the canonical filename and stale references to `workflow_break_down.md` are reconciled;
  - useful upstream benchmark/deep-dive documentation is present only in architecture-correct adapted form;
  - README/releasing/runtime architecture and package validation describe only the final six roles/two profiles;
  - no active documentation claims Companion, Micro Executor, removed profiles, sibling messaging, mandatory full-doc intake, Medium route, Deployment Token Report, or V2 timeout ownership as supported;
  - focused M01–M03 regressions plus full project CI/regression suites are GREEN;
  - release/package validation succeeds with the resulting worker set and docs layout;
  - no unrelated user-owned/runtime behavior is removed.
- Requirement coverage: REQ-017, REQ-018, REQ-020, REQ-021 plus integrated acceptance for REQ-001 through REQ-019.
- Dependencies: M03 checkpoint.
- Inherited constraints / rationale: all accepted decisions.
- Planned work packages:
  - rename/reconcile architecture document references;
  - adapt upstream benchmark/deep-dive material to fork architecture;
  - clean public/operator/runtime documentation;
  - run integrated package/schema/runtime/Muse/update/profile regression coverage and fix only defects inside accepted Definition.
- JIT decomposition / deferred-detail trigger: after M03, use actual final diff/reference search to define documentation and residual-cleanup Cards.
- Planning re-evaluation trigger: integrated testing reveals a sequencing problem across M01–M03 while Definition remains valid.
- Definition re-open trigger: integrated evidence contradicts an accepted target-state requirement/decision.
- Boundary gate / explicit user authorization: GitHub Release/tag/publication is outside this plan's automatic authority and requires explicit user authorization.

## 5. Requirement coverage matrix

| Requirement | Owner milestone | Planned work package or JIT trigger | OpenSpec candidate |
|---|---|---|---|
| REQ-001 | M01 | historical-source regression preservation | no |
| REQ-002 | M01 | project-only equal-version planner/launcher path | yes |
| REQ-003 | M01 | scoped backup/no-op/update tests | yes |
| REQ-004 | M01 | preserve/extend downgrade guard | yes |
| REQ-005 | M02 | six-role package/topology reconciliation | no |
| REQ-006 | M02 | Explorer/Investigator role contracts | no |
| REQ-007 | M02 | three-lane Investigator dispatch contract | no |
| REQ-008 | M02/M03 | direct Main reporting + profile communication cleanup | no |
| REQ-009 | M02 | worker report contract rewrite | no |
| REQ-010 | M02 | retained role/package regression | no |
| REQ-011 | M03 | two-profile registry/CLI/docs cleanup | no |
| REQ-012 | M03 | plus internal-worker contract | no |
| REQ-013 | M03 | muse-max six-role Muse mapping | yes |
| REQ-014 | M03 | plus-only Material Event Push | no |
| REQ-015 | M03 | proportionate intake + Explorer routing | no |
| REQ-016 | M01 | stale-route/local-instruction migration guard | yes |
| REQ-017 | M04 | architecture file rename/reference cleanup | no |
| REQ-018 | M04 | adapted upstream benchmark/deep-dive docs | no |
| REQ-019 | M03 | platform-settings regression preserving no V2 timeout ownership | no |
| REQ-020 | M02/M04 | absence guards + integrated reference scan | no |
| REQ-021 | M01–M04 | selective adaptation boundary enforced throughout | no |

OpenSpec candidates are resolved just-in-time only if Execution Prep confirms that the affected CLI/state/runtime contract merits a dedicated behavior contract.

## 6. Dependency / execution order

`M01 → M02 → M03 → M04`.

M01 is isolated first because it changes update/migration mechanics independently of worker topology. M02 establishes the final role set before profile/runtime mapping is simplified in M03. M04 intentionally follows the functional milestones so public documentation and integrated package verification describe actual final behavior rather than speculative intermediate state.

Execution Prep may split independent work inside a milestone when ownership is non-overlapping, but one selected ChatGPT-only Task Board still permits only one `in_progress` Card at a time.

## 7. Deployment / migration / rollback strategy

- Perform implementation on a branch-isolated ChatGPT-only workstream created during Execution Prep; do not use `main` as the mutable implementation lane.
- Preserve coherent commits per bounded Card/logical slice.
- Runtime/update changes require regression evidence against both current project and older-project catch-up scenarios before later milestones rely on them.
- Role/profile removal must be ownership-aware: remove only workflow-owned definitions/settings/docs and preserve unrelated user-owned workers/settings/files.
- The normal release artifact is not published automatically. A final implementation result may be release-ready, but tag/GitHub Release publication requires explicit user authorization.
- Rollback before integration is branch/commit based; update lifecycle changes must also retain transactional/backup guarantees defined by existing runtime behavior.

## 8. System verification strategy

Verification is layered:
1. focused unit/regression tests for the current milestone;
2. exact package/schema/worker/profile validation affected by the milestone;
3. Muse adapter/session regressions after final worker/profile mapping exists;
4. update lifecycle/owner-release regressions after M01 and again at integrated closure;
5. full repository CI/regression suite at M04;
6. static reference scan for removed roles/profiles/routes/features;
7. independent Task Card/milestone review per ChatGPT-only workflow before accepted implementation closure.

Tester acceptance must remain independent from the implementing worker for the reviewed scope.

## 9. Idempotency / data-integrity / security strategy

- Equal-version project update must be idempotent and must not produce unnecessary backup/write churn.
- Historical-source lookup remains version-bound and fail-closed on missing/mismatched sources.
- Downgrade remains explicit-authority only.
- Legacy local-instruction migration never infers user intent from stale workflow-owned route text.
- Removing workers/profiles/settings must be ownership-scoped and preserve unrelated user state.
- Muse session/workspace safety behavior is preserved unless exact regression evidence shows an implementation detail must change inside accepted authority.

## 10. Explicit authorization boundaries

No additional user authorization is required for repository planning, implementation, testing, review, or PR preparation inside this accepted scope.

Explicit user authorization is required before:
- publishing a GitHub Release or tag;
- performing any other external/live deployment not already implied by repository-local verification.

## 11. JIT / deferred decomposition map

- M01 Cards: materialize from current lifecycle/workflow/project_ops/backup regression surface.
- M02 Cards: materialize after M01 GREEN from actual worker/package/reference graph.
- M03 Cards: materialize after M02 GREEN from final six-role profile/Muse mapping.
- M04 Cards: materialize after M03 GREEN from residual reference scan, documentation delta and integrated-test needs.

Do not create speculative future Card IDs before their predecessor evidence exists.

## 12. Fresh-context boundaries

Independent plan review requires a fresh normal ChatGPT chat because this chat authored R1.

Later fresh-context boundaries follow the runtime Context Health Gate and independent implementation-review requirements. Do not create extra session boundaries solely by milestone count.

## 13. Pre-implementation planning audit

- Definition Complete still GREEN: yes; requirements R1 are approved and all strategic choices needed by this plan are accepted.
- False assumptions / P0/P1 risks: primary risks are stale role/profile references, project-only downgrade regression, and Muse role-map drift; each has milestone acceptance coverage.
- Milestone boundaries/order: coherent; update mechanics precede topology, topology precedes profile mapping, docs/integration follow final behavior.
- Dependency completeness: GREEN; M03 depends on final M02 role set and M04 on M03.
- Outcome-level acceptance: explicit for all four milestones.
- Requirement coverage: all REQ-001 through REQ-021 mapped.
- Migration/rollback: branch isolation + ownership-aware removal + existing transactional update semantics; publication remains gated.
- System verification: focused + integrated regressions defined.
- Data integrity/idempotency/security: project-update idempotency, historical source validation, downgrade guard and fail-closed local instruction handling explicitly covered.
- Authorization gates: release/tag publication explicitly gated; no other unresolved gate.
- OpenSpec boundaries: only candidate contracts identified; exact need deferred to Execution Prep.
- Overengineering/premature detail: no Task Cards or low-level implementation interface frozen before predecessor evidence.
- Remaining blockers: none.

## 14. Workflow references

- Workflow repository: `elmakus/chatgpt-codex-project-workflow`
- Workflow ref: `main`
- Policy: `chatgpt_only`
- Project Definition authority: `requirements/REQUIREMENTS.md` + `decisions/`
- Plan review lifecycle: `workflow/chatgpt_only/PLAN_REVIEW.md`

The Master Plan is not the live task tracker. Mutable execution state will be created only after plan approval through Execution Prep.
