# Delegation Contract

Read this file only when preparing or following up on delegated work, routing a Micro Execution task, or recovering an unavailable worker. Heavy entry alone does not require it.

## Active Worker Runtime

The active compute profile owns the worker harness as well as model allocation.

For `muse-max`, every workflow role (`micro_executor`, `default_executor`, `senior_executor`, `tester`, `archivist`, `companion`, and `investigator`) runs through the native Muse Code CLI with Muse Spark 1.3 Contributor / max. Main remains the user-selected Codex model and is never replaced by the profile. Materialize the role capsule in a temporary Markdown file and invoke:

```text
python3 ~/.codex/codex_workflow/runtime/muse_worker.py \
  --role <role> \
  --workspace <project-root> \
  --task-file <capsule-file>
```

The runner loads the installed workflow worker TOML only as the role contract, then launches `muse exec` with `muse-spark-1.3-contributor`, `max`, sandbox enforcement on, approvals disabled, and the workspace explicitly trusted. Muse authentication and subscription accounting stay owned by the official Muse Code CLI.

Under `muse-max`, do not use `spawn_agent`, `agent_type`, `fork_turns`, Codex model overrides, `resume_agent`, `wait_agent`, or `send_message` for workflow roles. Each worker call is a bounded external Muse Code invocation. A follow-up or repair launches a new invocation with the same Task ID, the changed capsule information, and any durable evidence needed to continue. A fresh independent review is a fresh `tester` invocation. The live-test profile is sequential by default; do not emulate Codex subagent concurrency with unmanaged background processes.

For `plus`, `luna-xhigh`, and `pro-x5`, use the normal internal Codex worker lifecycle described below. Every later reference in this file to internal worker APIs applies only to those Codex-backed profiles unless a paragraph explicitly says otherwise. The previous contract phrase `Senior Executor (Sol Medium in every current profile)` no longer applies globally: Senior remains Sol Medium in those three Codex-backed profiles, while `muse-max` deliberately routes Senior to Muse Spark 1.3 Contributor Max so every worker role uses Muse.

## Work Packages

Start each initial package with **Task ID**, a logical identifier unique within the deployment. Then use only the capsule for that role:

| Role | Capsule |
| --- | --- |
| Companion | **Project Context Scope**; **Context Task + Goal**; **Main-Agent Context Guidance** |
| Investigator | **Investigation Context**; **Evidence Question + Goal**; **Main-Agent Investigation Guidance** |
| Micro, Default, or Senior Executor | **Implementation Context + Ownership**; **Implementation Task + Goal**; **Main-Agent Implementation Guidance** |
| Tester | **Verification Context**; **Verification Goal**; **Main-Agent Verification Guidance** |
| Archivist | **Documentation Context + Audience**; **Documentation Task + Goal**; **Main-Agent Documentation Guidance** |

Keep packages short and sufficient. Include only the references, boundaries, decisions, constraints, intended outcome, approach, and cautions that materially help that worker. Initial internal Codex workers normally use `fork_turns="none"`; `muse-max` uses a fresh external invocation instead.

Require Task ID in every report. A follow-up repeats Task ID and sends only the capsule parts whose information changed. Do not resend stable context unless a fresh `muse-max` invocation needs the durable reference to recover it.

For Companion, give the bounded project surface and context outcome that can replace multiple Main reads or preserve useful retained context.

For Investigator, give one unfamiliar or ambiguous evidence gap. It may inspect bounded project evidence, Internet sources, or both as the assignment requires. It remains read-only and supplies evidence and implications; Main retains root-cause, architecture, solution, integration, and acceptance decisions.

For Executors, give enough transferred project knowledge to complete the bounded package well, but leave local discovery, command selection, implementation, self-check, and ordinary repair to the worker. Give Senior the unresolved hard-decision context when solving it is the assignment. Give Micro only work whose cause, desired result, ownership, and edit surface are already clear.

For Tester, transfer acceptance intent, risks, contracts, boundaries, relevant evidence, and any required gates. Let Tester choose and execute the specific checks. For Archivist, transfer verified facts only and keep the three Main-owned deployment-state documents outside its deployment write scope.

Ask every worker for a concise decision-ready return containing outcome, material changes or findings, verification evidence, limitations, residual risk, and only decisions Main must make.

## Fresh and Independent Contexts

When a controlling project/workflow requirement says `FRESH CODEX REQUIRED`, `FRESH CODEX RECOMMENDED`, fresh independent review, fresh execution context, context reset, or equivalent, satisfy freshness with a fresh worker context in the active worker runtime. Under `muse-max`, launch a new external Muse worker with only the minimal durable handoff and bounded task context. Under Codex-backed profiles, create a new internal worker/subagent by default, use the normal worker mechanism (for example `spawn_agent` when exposed), set `fork_turns="none"`, and transfer only the minimal durable handoff and bounded task context needed for the assignment.

Freshness means conversational/context isolation, not a new top-level Codex App thread. Do not use app-level `create_thread` solely to obtain review independence, milestone isolation, or a context reset.

For an independent review, create a new Tester worker in the active worker runtime (and an Investigator only when a bounded evidence gap materially helps) that did not perform the implementation being reviewed. Give it the exact target/base identity, acceptance intent, relevant durable evidence, and minimal required context. The implementing worker must not substitute for the independent reviewer.

App-level `create_thread` is allowed only when the user explicitly asks for a separate top-level application thread/session, or when the required task genuinely needs a capability or isolation property unavailable to the active worker runtime. If that exception is used, do not assume the child thread inherited the parent's approval, sandbox, network, or permission profile; treat effective child permissions as an independent runtime fact.

## Material Event Push

For Codex-backed profiles, the standing worker-side material-event policy is defined once in project `AGENTS.md`; do not repeat it in every task capsule. Workers may use runtime `send_message` to `/root` only for `BLOCKER`, `COURSE_CHANGE`, or `CRITICAL_PARTIAL` events under that policy. Ordinary progress, ETA, heartbeats, status chatter, routine partial findings, and normal completion are not follow-up traffic.

`muse-max` one-shot workers have no `send_message` path. Their normal process output is the completion/blocker boundary; do not build a polling or background-message shim for the live-test profile.

Do not use Main follow-ups to poll worker status. Send a follow-up only when Main has new evidence, a changed decision, or changed capsule information that the existing worker needs. For Codex-backed profiles, a `wait_agent` timeout without new evidence is not a reason to request an update. Prefer worker-to-Main material-event routing when the active runtime supports it; do not instruct sibling messaging unless the sibling's active task is materially affected and Main routing would create unnecessary delay or wasted work.

## Micro Execution

Micro Executor is a distinct worker below Default Executor. Use it only for a tiny deterministic implementation subtask inside an already substantive Heavy deployment. Do not spawn it when the complete user request is itself a trivial leaf task; Main handles those directly.

Good fits include a mechanical rename across known files, changing explicit configuration values, a version or manifest edit, adding a small entry that follows an existing pattern, tiny boilerplate, a known lint/format repair, or a small test edit whose cause and desired result are already established.

Do not use Micro Executor for broad discovery, unknown-root-cause debugging, architecture, security judgement, migration reasoning, repository-wide review, or work whose ownership is not already clear.

The installed internal `micro_executor` profile is selected by the active Codex-backed compute profile: Luna High in `plus`, Luna XHigh in `luna-xhigh`, and Sol Low in `pro-x5`. Spark is an optional acceleration path only for `plus` and `pro-x5`; `luna-xhigh` intentionally keeps Micro on Luna XHigh. Under `muse-max`, Micro uses the same Muse Spark 1.3 Contributor / max external harness as every other worker role.

### Preferred route: Spark where enabled

When the active profile is `plus` or `pro-x5`, and the current `spawn_agent` surface supports model overrides and Spark is available, spawn the Micro Executor with:

- `agent_type="micro_executor"`
- `fork_turns="none"`
- `model="gpt-5.3-codex-spark"`
- `reasoning_effort="high"` when `high` is supported for Spark; otherwise omit the effort override and use Spark's supported default.

If Spark is unavailable, unsupported, quota-blocked, or rejected specifically because that model cannot be spawned, treat that as routing information rather than task failure. Do not retry Spark repeatedly.

When the active profile is `luna-xhigh`, skip the Spark route and spawn `micro_executor` with no model override. When the active profile is `muse-max`, skip this entire internal Spark route and use the external Muse runner from **Active Worker Runtime**.

### Stable route: active compute profile

For Codex-backed profiles, spawn the same package as:

- `agent_type="micro_executor"`
- `fork_turns="none"`

with no model override. The installed Micro Executor is rendered from the active global compute profile.

Do not create a reasoning escalation ladder for Micro Execution. If Spark or the active Micro worker reports that the task requires meaningful exploration, architecture, security judgement, migration reasoning, broader ownership, or materially stronger reasoning, Main reclassifies the package:

- normal bounded implementation -> Default Executor using the active compute profile;
- exceptionally difficult bounded package -> Senior Executor using the active compute profile.

The compute profile changes worker harness/model allocation only. It does not change role semantics, task classification, ownership, or escalation boundaries.

## Worker Follow-up and Repair

Under Codex-backed profiles, resume the existing worker/thread when possible. Send only new evidence or changed capsule parts. Do not create a replacement merely because a worker is slow or a wait timed out.

Under `muse-max`, each one-shot invocation ends at its report. A follow-up or repair is a fresh invocation with the same Task ID plus the changed capsule parts and exact durable references needed to continue; do not rely on hidden conversation continuity.

When Tester finds an ordinary production defect, send the focused evidence to the owning Executor role for repair, then return the repair delta to an independent Tester for recheck. Main owns acceptance, not the worker's production or verification steps.

Escalate to a Main-owned decision only when evidence changes scope, contract, ownership, architecture, security or migration risk, required authority, or another material boundary.

## Recovery

For Codex-backed profiles, a `wait_agent` timeout without new evidence is not a recovery event. Wait again when the worker is still presumed healthy.

If a worker is irrecoverably unavailable and has no complete handoff:

1. Main identifies only available recovery sources, such as the predecessor thread, worktree, branch, handoff path, existing edits, or existing commits.
2. Main gives those sources plus the original Task ID and remaining goal to a replacement worker in the active worker runtime.
3. The replacement worker inspects predecessor evidence, determines completed versus remaining work, and continues from the first unfinished step.
4. Main integrates the replacement's decision-ready result.

For Codex-backed profiles, prefer `resume predecessor -> if impossible, delegate recovery + continuation -> integrate`. Under `muse-max`, prefer `durable evidence -> fresh Muse invocation -> integrate`. Main should not reconstruct the predecessor's detailed work before delegating the remainder.
