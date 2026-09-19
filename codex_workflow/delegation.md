# Delegation Contract

Read this file only when preparing or following up on delegated work, routing a Micro Execution task, or recovering an unavailable worker. Heavy entry alone does not require it.

## Active Worker Runtime

The active compute profile owns the worker harness as well as model allocation.

For `muse-max`, Companion remains one persistent internal Codex worker on GPT-5.6 Luna XHigh. The six roles `micro_executor`, `default_executor`, `senior_executor`, `tester`, `archivist`, and `investigator` run through the native Muse Code CLI with Muse Spark 1.3 Contributor / max. Main remains the user-selected Codex model and is never replaced by the profile. For one of those six Muse-backed roles, materialize the role capsule in a temporary Markdown file and invoke:

```text
python3 ~/.codex/codex_workflow/runtime/muse_worker.py \
  --role <role> \
  --workspace <project-root> \
  --task-file <capsule-file> \
  --task-id <logical-task-id> \
  --logical-worker-id <role-instance-id> \
  --caller-scope <opaque-caller-scope>
```

The runner resolves the active compute profile and requested role through shared profile authority, refuses roles that are not assigned to `muse-code`, loads the installed workflow worker TOML only as the semantic role contract, and takes model/reasoning from that active allocation. It binds the Muse Code 1.3.0 machine-readable surface captured by workstation evidence, requires one versioned structured final report, and returns one compact normalized JSON result. The first turn creates a private logical-worker/session binding; later turns use `--resume` with the same logical worker ID and exact role/allocation/workspace/Task-ID/caller-scope binding. Every turn gets a distinct invocation ID and private artifacts under `~/.codex/codex_workflow/muse_runs/`; session bindings and process-safe leases live privately under `~/.codex/codex_workflow/muse_sessions/`. Resume probes the exact retained Muse session and fails closed rather than silently creating a replacement. The adapter owns outer timeout/cancellation and process-tree cleanup. Muse authentication and subscription accounting stay owned by the official Muse Code CLI; the current workstation path disables nested Muse sandboxing because the unprivileged Docker boundary cannot provide the required user namespace.

Under `muse-max`, do not use internal Codex worker APIs for the six Muse-backed roles. Each turn is a bounded external Muse Code invocation, but ordinary follow-up or repair resumes the owning logical Muse session by adding `--resume` with the same logical worker ID, Task ID, caller scope, role, allocation, and workspace. Tester is always a distinct logical worker/session from Executor; after ordinary RED, resume the owning Executor for repair and then resume the same independent Tester for a full recheck of the new subject. A controlling freshness requirement, unavailable/unsafe resume, or material Main routing decision creates an explicitly new logical worker/session instead of relabeling a replacement as the old worker. Companion is the exception: use the normal persistent internal Codex lifecycle. Do not emulate Muse concurrency with unmanaged background processes.

When an external caller/Main has already declared multiple lanes independent and assigned isolated non-overlapping workspaces, it may use `MuseWorkerInvocation` plus `execute_workers_concurrently(...)` from `runtime/muse_worker.py` to await those explicit Muse calls together. The helper is deliberately not a scheduler: it does not inspect caller dependencies or policy state, decide parallel-safety, create branches/worktrees, or reorder work inside a lane. It rejects equal/nested workspaces, bounds one managed batch to eight explicit invocations, protects active invocation artifacts from concurrent retention cleanup, and keeps cancellation/process ownership per invocation. Executor -> Tester -> optional owning-Executor repair -> same Tester full recheck stays ordered inside each lane while each role/lane keeps a distinct session binding. Do not replace this surface with shell `&`, detached jobs, or sibling-to-sibling worker coordination.

For `plus`, `luna-xhigh`, and `pro-x5`, every workflow role uses the normal internal Codex lifecycle described below. Senior remains Sol Medium in those three profiles; under `muse-max`, Senior is one of the six Muse Contributor Max roles while Companion remains internal Luna XHigh.

## Work Packages

Start each initial package with **Task ID**, a logical identifier unique within the deployment. Then use only the capsule for that role:

| Role | Capsule |
| --- | --- |
| Companion | **Project Context Scope**; **Context Task + Goal**; **Main-Agent Context Guidance** |
| Investigator | **Investigation Context**; **Evidence Question + Goal**; **Main-Agent Investigation Guidance** |
| Micro, Default, or Senior Executor | **Implementation Context + Ownership**; **Implementation Task + Goal**; **Main-Agent Implementation Guidance** |
| Tester | **Verification Context**; **Verification Goal**; **Main-Agent Verification Guidance** |
| Archivist | **Documentation Context + Audience**; **Documentation Task + Goal**; **Main-Agent Documentation Guidance** |

Keep packages short and sufficient. Include only the references, boundaries, decisions, constraints, intended outcome, approach, and cautions that materially help that worker. Initial internal Codex workers normally use `fork_turns="none"`; the six Muse-backed `muse-max` roles create separate logical worker/session identities and then use bounded external invocations for their turns.

Require Task ID in every report. A follow-up repeats Task ID and sends only the capsule parts whose information changed. When resuming a safe Muse logical worker, rely on its retained conversation only for its own prior trajectory; still provide new subject identity and changed evidence needed for the current turn. A fresh/replacement Muse worker receives the minimum durable context needed to recover without predecessor trajectory.

For Companion, give the bounded project surface and context outcome that can replace multiple Main reads or preserve useful retained context.

For Investigator, give one unfamiliar or ambiguous evidence gap. It may inspect bounded project evidence, Internet sources, or both as the assignment requires. It remains read-only and supplies evidence and implications; Main retains root-cause, architecture, solution, integration, and acceptance decisions.

For Executors, give enough transferred project knowledge to complete the bounded package well, but leave local discovery, command selection, implementation, self-check, and ordinary repair to the worker. Give Senior the unresolved hard-decision context when solving it is the assignment. Give Micro only work whose cause, desired result, ownership, and edit surface are already clear.

For Tester, transfer acceptance intent, risks, contracts, boundaries, relevant evidence, and any required gates. Let Tester choose and execute the specific checks. For Archivist, transfer verified facts only and keep the three Main-owned deployment-state documents outside its deployment write scope.

Ask every worker for a concise decision-ready return containing outcome, material changes or findings, verification evidence, limitations, residual risk, and only decisions Main must make.

## Fresh and Independent Contexts

When a controlling project/workflow requirement says `FRESH CODEX REQUIRED`, `FRESH CODEX RECOMMENDED`, fresh independent review, fresh execution context, context reset, or equivalent, satisfy freshness with a fresh worker context in the active role harness. For the six Muse-backed `muse-max` roles, create a new logical worker/session identity and give it only the minimal durable handoff and bounded task context; starting another `muse exec` process against an old session is not fresh. For internal Codex roles — including `muse-max` Companion and every role in `plus`, `luna-xhigh`, and `pro-x5` — create a new internal worker/subagent by default, use the normal worker mechanism (for example `spawn_agent` when exposed), set `fork_turns="none"`, and transfer only the minimal durable handoff and bounded task context needed for the assignment.

Freshness means conversational/context isolation, not a new top-level Codex App thread. Do not use app-level `create_thread` solely to obtain review independence, milestone isolation, or a context reset.

For an independent review, create a new Tester worker in the active worker runtime (and an Investigator only when a bounded evidence gap materially helps) that did not perform the implementation being reviewed. Give it the exact target/base identity, acceptance intent, relevant durable evidence, and minimal required context. The implementing worker must not substitute for the independent reviewer.

App-level `create_thread` is allowed only when the user explicitly asks for a separate top-level application thread/session, or when the required task genuinely needs a capability or isolation property unavailable to the active worker runtime. If that exception is used, do not assume the child thread inherited the parent's approval, sandbox, network, or permission profile; treat effective child permissions as an independent runtime fact.

## Material Event Push

For internal Codex workers, the standing worker-side material-event policy is defined once in project `AGENTS.md`; do not repeat it in every task capsule. They may use runtime `send_message` to `/root` only for `BLOCKER`, `COURSE_CHANGE`, or `CRITICAL_PARTIAL` events under that policy. Ordinary progress, ETA, heartbeats, status chatter, routine partial findings, and normal completion are not follow-up traffic.

The six Muse-backed `muse-max` roles have no `send_message` path. Their normal completion/blocker boundary is the adapter's single compact normalized result; raw Muse trajectories remain in private run artifacts. Do not build a polling or background-message shim. Companion remains an internal Codex worker and follows the normal event policy.

Do not use Main follow-ups to poll worker status. Send a follow-up only when Main has new evidence, a changed decision, or changed capsule information that the existing worker needs. For internal Codex workers, a `wait_agent` timeout without new evidence is not a reason to request an update. Prefer worker-to-Main material-event routing when the active runtime supports it; do not instruct sibling messaging unless the sibling's active task is materially affected and Main routing would create unnecessary delay or wasted work.

## Micro Execution

Micro Executor is a distinct worker below Default Executor. Use it only for a tiny deterministic implementation subtask inside an already substantive Heavy deployment. Do not spawn it when the complete user request is itself a trivial leaf task; Main handles those directly.

Good fits include a mechanical rename across known files, changing explicit configuration values, a version or manifest edit, adding a small entry that follows an existing pattern, tiny boilerplate, a known lint/format repair, or a small test edit whose cause and desired result are already established.

Do not use Micro Executor for broad discovery, unknown-root-cause debugging, architecture, security judgement, migration reasoning, repository-wide review, or work whose ownership is not already clear.

The installed internal `micro_executor` profile is selected by `plus`, `luna-xhigh`, or `pro-x5`: Luna High in `plus`, Luna XHigh in `luna-xhigh`, and Sol Low in `pro-x5`. Spark is an optional acceleration path only for `plus` and `pro-x5`; `luna-xhigh` intentionally keeps Micro on Luna XHigh. Under `muse-max`, Micro is one of the six Muse Spark 1.3 Contributor / max external roles.

### Preferred route: Spark where enabled

When the active profile is `plus` or `pro-x5`, and the current `spawn_agent` surface supports model overrides and Spark is available, spawn the Micro Executor with:

- `agent_type="micro_executor"`
- `fork_turns="none"`
- `model="gpt-5.3-codex-spark"`
- `reasoning_effort="high"` when `high` is supported for Spark; otherwise omit the effort override and use Spark's supported default.

If Spark is unavailable, unsupported, quota-blocked, or rejected specifically because that model cannot be spawned, treat that as routing information rather than task failure. Do not retry Spark repeatedly.

When the active profile is `luna-xhigh`, skip the Spark route and spawn `micro_executor` with no model override. When the active profile is `muse-max`, skip this entire internal Spark route and use the external Muse runner from **Active Worker Runtime**.

### Stable route: active compute profile

For internal-Codex Micro allocations in `plus`, `luna-xhigh`, and `pro-x5`, spawn the same package as:

- `agent_type="micro_executor"`
- `fork_turns="none"`

with no model override. The installed Micro Executor is rendered from the active global compute profile.

Do not create a reasoning escalation ladder for Micro Execution. If Spark or the active Micro worker reports that the task requires meaningful exploration, architecture, security judgement, migration reasoning, broader ownership, or materially stronger reasoning, Main reclassifies the package:

- normal bounded implementation -> Default Executor using the active compute profile;
- exceptionally difficult bounded package -> Senior Executor using the active compute profile.

The compute profile changes worker harness/model allocation only. It does not change role semantics, task classification, ownership, or escalation boundaries.

## Worker Follow-up and Repair

For internal Codex roles, resume the existing worker/thread when possible. Send only new evidence or changed capsule parts. Do not create a replacement merely because a worker is slow or a wait timed out.

For the six Muse-backed `muse-max` roles, each bounded invocation ends at its report, but the logical worker/session may continue. For ordinary follow-up or repair, resume the same bound session with the same logical worker ID and send the changed capsule parts and exact current subject/evidence. Resume is fail-closed: missing retention, binding mismatch, concurrent use, rejected probe, or another unsafe condition must return a recovery classification; Main then decides whether to retry, reconcile workspace state, or create an explicitly new A2/B2-style worker. Companion remains persistent and follows the internal Codex rule above.

When Tester finds an ordinary production defect, send the focused evidence to the owning Executor role for repair, then return the repair delta to an independent Tester for recheck. Main owns acceptance, not the worker's production or verification steps.

Escalate to a Main-owned decision only when evidence changes scope, contract, ownership, architecture, security or migration risk, required authority, or another material boundary.

## Recovery

For internal Codex roles, a `wait_agent` timeout without new evidence is not a recovery event. Wait again when the worker is still presumed healthy.

If a worker is irrecoverably unavailable and has no complete handoff:

1. Main identifies only available recovery sources, such as the predecessor thread, worktree, branch, handoff path, existing edits, or existing commits.
2. Main gives those sources plus the original Task ID and remaining goal to a replacement worker in the active worker runtime.
3. The replacement worker inspects predecessor evidence, determines completed versus remaining work, and continues from the first unfinished step.
4. Main integrates the replacement's decision-ready result.

For internal Codex roles, prefer `resume predecessor -> if impossible, delegate recovery + continuation -> integrate`. For a Muse-backed `muse-max` role, prefer `resume the exact bound logical session when safe -> otherwise reconcile durable workspace/evidence and create an explicitly new logical worker -> integrate`. Never silently create a new Muse session under an old A1/B1 identity. Main should not reconstruct the predecessor's detailed work before delegating the remainder.
