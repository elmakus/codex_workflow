# Master Plan — Muse native worker profile

Revision: `R4`
Status: `draft`
Updated: `2026-09-21`
Independent plan review: `RECOMMENDED`

> Planning organizes the approved Project Definition in `requirements/REQUIREMENTS.md` Revision R3. Accepted requirements and decisions remain authoritative.

## 1. Accepted target / canonical inputs

- Requirements: `requirements/REQUIREMENTS.md` — Revision R3, `approved`
- Current-scope decision:
  - `decisions/DEC-007-muse-native-profile.md`
- Inherited decisions:
  - `decisions/DEC-001-worker-topology.md`
  - `decisions/DEC-002-compute-profiles.md` — profile-count clause superseded by DEC-007
  - `decisions/DEC-003-communication-context.md` — plus-only Material Event Push applicability superseded for `muse-native` by DEC-007
  - `decisions/DEC-004-selective-upstream-adoption.md`
  - `decisions/DEC-005-fork-release-version-generation.md`
  - `decisions/DEC-006-muse-event-driven-waiting.md`
- Current-scope research: `research/muse-native-profile.md` / `R-MUSE-NATIVE-01`
- Promotion provenance: `brainstorming/muse-native-profile.md` — `muse-native-profile@R1`
- Workstream: `feature-muse-native-profile`
- Baseline: `main@016a42ba0cf0d274bf12d718db6d7580abe54658`

Historical requirements REQ-001 through REQ-029 retain their completed execution history except the explicitly superseded portions of REQ-011 and REQ-014. This plan directly owns REQ-030 through REQ-044 and regression-preserves all non-superseded inherited authority.

## 2. Verified execution baseline

Current source and Research establish:

- `compute_profiles.py` currently supports only `plus` and `muse-max`.
- `WorkerModel` currently carries model, reasoning effort and harness, but no explicit per-worker provider field.
- `plan_compute_profile()` enables internal Codex agents only for `plus`; `muse-max` deliberately keeps installed Codex worker TOMLs dormant.
- Current worker TOMLs already provide the six native Codex role contracts and can serve as the semantic source for `muse-native`.
- Current `heavy_route.md` and `delegation.md` contain mature no-polling, freshness, independent Tester, repair/recheck, exact-three Investigator, bounded package and quiet-orchestration semantics that must be expressed for the new profile.
- External `muse-max` additionally owns `muse_worker.py`, Muse session/lease, capability hints, JSONL normalization, run retention and one-cell Code Mode waiting. These are transport mechanisms, not parity requirements for `muse-native`.
- CLIProxyAPI current source/release evidence supports Muse/Meta OAuth, `muse-spark-1.3-contributor` with `max`, and a Codex/Responses-oriented Meta execution path.
- Current Codex documentation supports custom-agent model/reasoning configuration and documented MCP/skills inheritance, but live issue evidence makes exact installed-environment verification mandatory.

## 3. Inherited non-goals / invariants / constraints

- Keep `plus` behavior unchanged.
- Keep external `muse-max` behavior and its adapter/session/capability-hint path unchanged.
- Do not retire `muse-max` in this workstream.
- Do not restore `luna-xhigh`, `pro-x5`, Companion, Micro Executor, Medium route or Deployment Token Report.
- Do not adopt `multi_agent_v2` timeout ownership.
- Main remains orchestration/integration/acceptance authority.
- Tester remains independent from the implementing worker.
- No sibling-to-sibling worker coordination.
- Required provider/model/effort and required capabilities fail visibly; there is no silent fallback.
- Do not copy OAuth/access credentials into repository state, worker capsules, documentation or normal evidence.
- Do not recreate `muse_worker.py`, Muse session registry, Muse raw-run retention, `--disable-sandbox` or the one-cell terminal-wait workaround for `muse-native` merely for symmetry.
- External live OAuth/account setup is an environment prerequisite for final live acceptance, not repository-owned credential mutation.
- Release-triggering VERSION changes, tag/GitHub Release publication and deployment remain separately gated.

## 4. Milestones

### M07 — native profile and provider foundation

- Outcome: the repository can select/render a third `muse-native` profile as an internal Codex-worker allocation targeting Muse Contributor/Max through a configured CLIProxyAPI provider, without altering the two existing profiles.
- Requirement coverage: REQ-030, REQ-031, REQ-040, REQ-042, REQ-044.
- Dependencies: Definition R3 / DEC-007.
- Planned work packages:
  - extend compute-profile authority to exactly three supported profiles;
  - add the minimal provider-routing field/configuration needed for internal worker TOMLs while preserving unrelated user-owned provider settings;
  - render all six `muse-native` workers to `muse-spark-1.3-contributor`, `max`, native Codex harness and the CLIProxyAPI provider route;
  - make internal Codex agents enabled for `plus` and `muse-native`, but preserve current external `muse-max` disabling behavior;
  - preserve profile-switch transaction/rollback behavior and selected-profile persistence across update paths;
  - add focused tests for profile validation, summary/CLI output, worker rendering, provider rendering, reversibility and no-secret ownership;
  - create an isolated provider smoke probe that distinguishes unsupported routing from merely missing/unconfigured OAuth environment.
- Stable acceptance:
  - exactly three profiles are selectable;
  - all six `muse-native` worker configs resolve to the exact model/effort/provider intent;
  - no profile switch mutates CLIProxyAPI OAuth credentials or embeds secrets;
  - `plus` and `muse-max` render identically to baseline;
  - a configured live environment can identify the exact Contributor/Max route without fallback, or the smoke probe returns a precise environment blocker rather than falsely passing.
- JIT trigger: exact TOML/provider ownership shape may be refined from the current Codex/CLIProxyAPI config surface once the first isolated smoke probe is executed; the target provider/model/effort and secret-ownership constraints are fixed.
- Planning re-evaluation trigger: native custom agents cannot select the configured provider without changing global Main provider/model behavior or requiring broad unrelated user config ownership.
- Definition re-open trigger: exact Contributor/Max through CLIProxyAPI OAuth is technically impossible without changing the accepted provider/auth target or allowing fallback.
- Boundary gate: repository implementation/tests are authorized; credential creation/login remains user/environment owned.

### M08 — native orchestration parity and capability behavior

- Outcome: `muse-native` expresses and proves the existing higher-level orchestration contract through native Codex worker lifecycle instead of external Muse transport.
- Requirement coverage: REQ-032 through REQ-041 plus REQ-044.
- Dependencies: M07 repository foundation GREEN; live provider access required for the runtime portions of acceptance.
- Planned work packages:
  - render/apply the same quiet milestone communication policy to `muse-native`;
  - route healthy native-worker waiting through normal Codex wait semantics with no status/list/progress polling and no liveness-only user update;
  - encode ordinary same-worker continuation, genuine fresh-context creation and fail-visible resume/replacement semantics;
  - preserve independent Tester and the Executor → Tester RED → same Executor repair → same Tester full recheck lifecycle;
  - preserve exact-three independent Investigator lanes and safe dependency/workspace concurrency rules using native Codex workers, without importing the Muse helper's max-8 transport cap;
  - expose the bounded BLOCKER / COURSE_CHANGE / CRITICAL_PARTIAL material-event path available to native workers while preserving no routine progress and no sibling messaging;
  - use native MCP/tool and skills configuration/inheritance instead of `MuseCapabilityHints` for `muse-native`, while retaining capability hints unchanged for external `muse-max`;
  - update Heavy/delegation/profile guidance and focused tests so transport-specific Muse mechanisms are explicitly scoped only to `muse-max`;
  - live-probe wait/resume/freshness/cancellation and at least one required MCP plus one required skill in the installed environment.
- Stable acceptance:
  - quiet milestone behavior under `muse-native` matches the semantic policy of `muse-max`;
  - a healthy multi-minute native worker creates no Main-driven status/list/progress loop and no liveness-only commentary;
  - same-worker continuation and fresh-worker isolation are distinguishable and correct;
  - independent Tester plus RED-repair-recheck completes with the intended identities;
  - exact-three Investigator lanes run under native lifecycle and preserve direct-to-Main evidence;
  - required MCP and required skill work live or fail visibly with exact capability evidence;
  - timeout/cancel/recovery shows no silent replacement/provider change or relevant orphaned execution;
  - external `muse-max` adapter/session/capability-hint behavior remains GREEN.
- JIT trigger: exact native material-event/capability plumbing follows current installed Codex APIs; Execution Prep may refine tests/capsules without changing accepted semantics.
- Planning re-evaluation trigger: achieving parity requires introducing a new durable scheduler/session subsystem rather than using native Codex lifecycle, or changes milestone ordering materially.
- Definition re-open trigger: native lifecycle cannot preserve Tester independence, no-poll waiting, required capability behavior or fail-closed identity without weakening accepted semantics.
- Boundary gate: live OAuth-backed execution cannot be marked GREEN until the environment has a valid user-provided CLIProxyAPI Muse OAuth credential.

### M09 — integrated parity matrix, A/B evidence and documentation

- Outcome: the three-profile system is integrated, documented and supported by live parity/regression evidence, including a comparable external-`muse-max` versus `muse-native` task.
- Requirement coverage: REQ-030 through REQ-044 integrated acceptance; inherited non-superseded REQ-001 through REQ-029 regression coverage.
- Dependencies: M08 GREEN.
- Planned work packages:
  - execute the full preservation/parity matrix from `brainstorming/muse-native-profile.md` as an acceptance checklist;
  - run one bounded A/B task through external `muse-max` and `muse-native` with the same higher-level role/task/acceptance contract and record model/provider/harness identity plus material quality/lifecycle observations;
  - run repository regression coverage for profile switching, install/update preservation, Heavy/delegation contracts and external Muse adapter/session behavior;
  - reconcile README, workflow breakdown, commands/profile table and relevant benchmark guidance to exactly three profiles;
  - preserve evidence of any native-vs-external behavioral differences without using one benchmark to justify retirement of `muse-max`;
  - prepare the workstream for independent Card/milestone/final-integration review and PR integration under the normal workflow.
- Stable acceptance:
  - every REQ-043 live gate has exact evidence;
  - all 14 preservation-matrix parity gates are GREEN or an accepted narrower evidence-equivalent gate is recorded without weakening Definition;
  - A/B execution is reproducible enough to compare harness behavior without changing model/effort/task acceptance;
  - `plus` and `muse-max` regressions remain GREEN;
  - docs/CLI/profile reporting contain no stale two-profile assumption and no claim that external `muse-max` is deprecated/retired;
  - no OAuth or provider secret appears in committed artifacts/evidence.
- JIT trigger: exact A/B task fixture may be selected after M08 proves the native path; it must be bounded, deterministic enough for comparison and exercise real implementation/verification lifecycle.
- Planning re-evaluation trigger: integrated acceptance reveals a cross-repository delivery dependency or migration strategy not represented by M07/M08.
- Definition re-open trigger: evidence supports changing the accepted product decision (for example retiring `muse-max` or changing the model/provider target); such changes are explicitly out of this workstream.
- Boundary gate: release/version/tag/deployment remains outside current authorization unless separately approved.

## 5. Requirement coverage matrix

| Requirement | Coverage |
|---|---|
| REQ-001–REQ-010, REQ-012–REQ-013, REQ-015–REQ-029 | inherited regression authority across M07–M09 as affected |
| REQ-011 | historical two-profile clause superseded by REQ-030; legacy-profile removal retained in M07/M09 |
| REQ-014 | historical plus-only event-push applicability superseded by REQ-039; external `muse-max` prohibition retained in M08/M09 |
| REQ-030 | M07 profile set; M09 integrated docs/regression |
| REQ-031 | M07 exact native model/provider allocation; M09 live confirmation |
| REQ-032 | M08 role/package/report parity |
| REQ-033 | M08 quiet orchestration; M09 integrated parity |
| REQ-034 | M08 native no-poll wait; M09 live acceptance |
| REQ-035 | M08 continuation/freshness |
| REQ-036 | M08 independent Tester and repair/recheck |
| REQ-037 | M08 exact-three Investigator/native concurrency |
| REQ-038 | M08 MCP/skills live acceptance |
| REQ-039 | M08 bounded native material events |
| REQ-040 | M07/M08 transport replacement boundaries |
| REQ-041 | M08 cancellation/recovery |
| REQ-042 | M07–M09 credential/secret boundary |
| REQ-043 | M08 live gates + M09 full integrated matrix/A-B |
| REQ-044 | M07–M09 unchanged `plus` and `muse-max` regressions |

## 6. Dependency / execution order

`M07 → M08 → M09`.

M07 establishes deterministic repository/profile/provider configuration without requiring the external Muse transport. M08 then proves the behavioral parity that depends on native lifecycle. M09 performs full integrated/A-B acceptance only after those foundations are stable.

A missing OAuth login may block only live provider/runtime acceptance; it does not authorize bypassing tests or marking a live gate GREEN, and it does not require storing credentials in the repository.

## 7. Verification strategy

Verification is layered:

1. profile/model/provider rendering unit tests;
2. profile-switch/idempotency/rollback/update-preservation tests;
3. static Heavy/delegation communication and transport-scope tests;
4. isolated CLIProxyAPI/native-agent provider smoke;
5. live native worker role launch;
6. multi-minute no-poll wait evidence;
7. same-worker continuation + fresh-worker isolation;
8. Executor/Tester RED-repair-recheck;
9. exact-three Investigator native lanes;
10. required MCP capability probe;
11. required skill probe;
12. timeout/cancel/recovery probe;
13. unchanged `plus` and external `muse-max` regression suites;
14. one bounded A/B `muse-max` versus `muse-native` task;
15. integrated repository test suite and documentation/profile consistency checks.

Live checks must record exact relevant provider/model/harness identity and must not expose credentials.

## 8. Data integrity / idempotency / security strategy

- Profile switching remains compensating/idempotent and preserves unrelated Codex settings and workers.
- CLIProxyAPI provider configuration owned by the user/environment must not be deleted or rewritten beyond the minimum workflow-owned selector/config surface proven necessary.
- OAuth/access credentials remain outside repository and task capsules.
- A failed native resume/provider request must not silently spawn/substitute a different identity or route.
- Freshness requirements must never reuse prior conversational state merely because the same role name is requested.
- External Muse session registry/run artifacts remain untouched for `muse-max`.
- Native profile must not introduce a second durable scheduler/session registry unless implementation evidence triggers replanning and accepted authority still permits it.

## 9. Explicit authorization boundaries

The current feature request authorizes repository-local design, implementation, tests, local/live compatibility verification using already-authorized environment access, branch/PR preparation and normal workflow integration steps.

Separate explicit authorization remains required before:

- initiating or changing the user's Muse/Meta OAuth login/subscription credentials;
- storing or migrating any credential;
- changing release-triggering VERSION metadata;
- publishing a tag or GitHub Release;
- external/live deployment beyond bounded local verification already authorized by the project environment.

If live acceptance reaches an unconfigured OAuth environment, persist the exact blocker rather than asking the workflow to own the credential.

## 10. OpenSpec / contract candidate

Execution Prep should create one bounded behavior contract if the implementation spans compute-profile rendering plus Heavy/delegation/native runtime semantics. The contract should capture the `muse-native` profile allocation and parity invariants, not duplicate implementation details or external Muse adapter internals.

## 11. JIT / deferred decomposition

- M07 first Cards: profile/provider rendering + isolated config/provider smoke.
- M07 later Card: switch/update regression and exact live provider smoke, materialized against the implemented config shape.
- M08 first Cards: Heavy/delegation native parity + focused static tests; native runtime/capability live matrix after provider smoke.
- M08 later Cards: repair/recheck, Investigator, MCP/skill and cancel/recovery probes from actual native runtime evidence.
- M09 Cards: full regression/docs plus A/B and integrated acceptance.
- Do not pre-create transport shims or a native session registry; materialize those only through replanning if live evidence proves native lifecycle insufficient while Definition remains satisfiable.

## 12. Fresh-context / review boundary

This R4 plan is a material new execution strategy and requirement-coverage revision. Independent plan review is **RECOMMENDED** and practical.

The authoring chat must stop after freezing the exact R4 draft, creating `planning/reviews/R4.md` as pending, and pointing the selected workstream manifest to that review record. A fresh normal ChatGPT chat performs the independent plan review. GREEN returns to Planning for deterministic approval, then Execution Prep proceeds automatically because repository implementation is already authorized.

## 13. Pre-implementation planning audit

- Definition Complete: GREEN — requirements R3 approved; DEC-007 accepted.
- User/product blockers: none.
- Research uncertainty: provider/native-agent/MCP/skills details are live implementation evidence with explicit staged gates; none requires a new product choice before execution.
- Milestone structure: M07 isolates profile/provider foundation, M08 owns behavioral parity, M09 owns integrated/A-B acceptance.
- Requirement coverage: REQ-030 through REQ-044 mapped; superseded portions of REQ-011/014 are handled explicitly; inherited authority remains regression-protected.
- Safety/security: OAuth credentials remain externally owned; no secret may enter repo/capsules/evidence.
- Recovery: no silent worker/provider substitution; external `muse-max` recovery remains unchanged.
- Overengineering: no native registry/broker/transport shim is planned without concrete failure evidence.
- External dependency: CLIProxyAPI OAuth must be configured for final live acceptance; absence is a precise environment blocker, not a reason to weaken acceptance.
- Authorization gates: repository-local implementation/testing/PR integration is in scope; credential changes and release/deployment are separately gated.
- OpenSpec: one bounded parity/profile contract is a candidate if Execution Prep finds it useful.
- Remaining planning blocker: none.

## 14. Workflow references

- Workflow repository: `elmakus/chatgpt-codex-project-workflow`
- Workflow ref: `main`
- Policy: `chatgpt_only`
- Project Definition authority: `requirements/REQUIREMENTS.md` R3 + `decisions/DEC-007-muse-native-profile.md`
- Plan review lifecycle: `workflow/chatgpt_only/PLAN_REVIEW.md`

The Master Plan is not the live task tracker. Mutable execution state begins only after plan approval through Execution Prep.
