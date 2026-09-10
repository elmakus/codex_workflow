# Delegation Contract

Read this file only when preparing or following up on delegated work, routing a Micro Execution task, or recovering an unavailable worker. Heavy entry alone does not require it.

## Work Packages

Start each initial package with **Task ID**, a logical identifier unique within the deployment. Then use only the capsule for that role:

| Role | Capsule |
| --- | --- |
| Companion | **Project Context Scope**; **Context Task + Goal**; **Main-Agent Context Guidance** |
| Investigator | **Investigation Context**; **Evidence Question + Goal**; **Main-Agent Investigation Guidance** |
| Micro, Default, or Senior Executor | **Implementation Context + Ownership**; **Implementation Task + Goal**; **Main-Agent Implementation Guidance** |
| Tester | **Verification Context**; **Verification Goal**; **Main-Agent Verification Guidance** |
| Archivist | **Documentation Context + Audience**; **Documentation Task + Goal**; **Main-Agent Documentation Guidance** |

Keep packages short and sufficient. Include only the references, boundaries, decisions, constraints, intended outcome, approach, and cautions that materially help that worker. Initial workers normally use `fork_turns="none"`.

Require Task ID in every report. A follow-up repeats Task ID and sends only the capsule parts whose information changed. Do not resend stable context.

For Companion, give the bounded project surface and context outcome that can replace multiple Main reads or preserve useful retained context.

For Investigator, give one unfamiliar or ambiguous evidence gap. It may inspect bounded project evidence, Internet sources, or both as the assignment requires. It remains read-only and supplies evidence and implications; Main retains root-cause, architecture, solution, integration, and acceptance decisions.

For Executors, give enough transferred project knowledge to complete the bounded package well, but leave local discovery, command selection, implementation, self-check, and ordinary repair to the worker. Give Senior the unresolved hard-decision context when solving it is the assignment. Give Micro only work whose cause, desired result, ownership, and edit surface are already clear.

For Tester, transfer acceptance intent, risks, contracts, boundaries, relevant evidence, and any required gates. Let Tester choose and execute the specific checks. For Archivist, transfer verified facts only and keep the three Main-owned deployment-state documents outside its deployment write scope.

Ask every worker for a concise decision-ready return containing outcome, material changes or findings, verification evidence, limitations, residual risk, and only decisions Main must make.

## Material Event Push

The standing worker-side material-event policy is defined once in project `AGENTS.md`; do not repeat it in every task capsule. Workers may use runtime `send_message` to `/root` only for `BLOCKER`, `COURSE_CHANGE`, or `CRITICAL_PARTIAL` events under that policy. Ordinary progress, ETA, heartbeats, status chatter, routine partial findings, and normal completion are not follow-up traffic.

Do not use Main follow-ups to poll worker status. Send a follow-up only when Main has new evidence, a changed decision, or changed capsule information that the existing worker needs. A `wait_agent` timeout without new evidence is not a reason to request an update. Prefer worker-to-Main material-event routing; do not instruct sibling messaging unless the sibling's active task is materially affected and Main routing would create unnecessary delay or wasted work.

## Micro Execution

Micro Executor is a distinct worker below Default Executor. Use it only for a tiny deterministic implementation subtask inside an already substantive Heavy deployment. Do not spawn it when the complete user request is itself a trivial leaf task; Main handles those directly.

Good fits include a mechanical rename across known files, changing explicit configuration values, a version or manifest edit, adding a small entry that follows an existing pattern, tiny boilerplate, a known lint/format repair, or a small test edit whose cause and desired result are already established.

Do not use Micro Executor for broad discovery, unknown-root-cause debugging, architecture, security judgement, migration reasoning, repository-wide review, or work whose ownership is not already clear.

The installed `micro_executor` profile is the stable fallback and uses Luna High. Spark is an optional acceleration path, never a workflow requirement.

### Preferred route: Spark

When the current `spawn_agent` surface supports model overrides and Spark is available, spawn the Micro Executor with:

- `agent_type="micro_executor"`
- `fork_turns="none"`
- `model="gpt-5.3-codex-spark"`
- `reasoning_effort="high"` when `high` is supported for Spark; otherwise omit the effort override and use Spark's supported default.

If Spark is unavailable, unsupported, quota-blocked, or rejected specifically because that model cannot be spawned, treat that as routing information rather than task failure. Do not retry Spark repeatedly.

### Stable fallback: Luna High

Spawn the same package as:

- `agent_type="micro_executor"`
- `fork_turns="none"`

with no model override. The installed Micro Executor profile is `gpt-5.6-luna` at `high` reasoning, so this fallback also works when the runtime does not expose model/reasoning overrides at all.

Do not create a reasoning escalation ladder for Micro Execution. If Spark or Luna High reports that the task requires meaningful exploration, architecture, security judgement, migration reasoning, broader ownership, or materially stronger reasoning, Main reclassifies the package:

- normal bounded implementation -> Default Executor (Luna Max);
- exceptionally difficult bounded package -> Senior Executor (Sol Medium).

## Worker Follow-up and Repair

Resume the existing worker/thread when possible. Send only new evidence or changed capsule parts. Do not create a replacement merely because a worker is slow or a wait timed out.

When Tester finds an ordinary production defect, send the focused evidence to the owning Executor for repair, then return the repair delta to the same Tester for recheck. Main owns acceptance, not the worker's production or verification steps.

Escalate to a Main-owned decision only when evidence changes scope, contract, ownership, architecture, security or migration risk, required authority, or another material boundary.

## Recovery

A `wait_agent` timeout without new evidence is not a recovery event. Wait again when the worker is still presumed healthy.

If a worker is irrecoverably unavailable and has no complete handoff:

1. Main identifies only available recovery sources, such as the predecessor thread, worktree, branch, handoff path, or existing commits.
2. Main gives those sources plus the original Task ID and remaining goal to the replacement worker.
3. The replacement worker inspects predecessor evidence, determines completed versus remaining work, and continues from the first unfinished step.
4. Main integrates the replacement's decision-ready result.

Prefer `resume predecessor -> if impossible, delegate recovery + continuation -> integrate`. Main should not reconstruct the predecessor's detailed work before delegating the remainder.
