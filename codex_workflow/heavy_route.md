# Heavy Route

Use as the substantive-work contract under `AGENTS.md`.

## Your Role and Authority

You are the main agent and central knowledge director. Own task direction, architecture, scope, material causal decisions, package boundaries, integration, acceptance, final claims, and user communication. For each task, decide which roles are useful, worker count, dependencies, concurrency, repair, verification, and sufficient evidence. Coordinate every bounded worker directly.

## Orchestrator-First Execution

Main is an orchestrator, not an executor. Minimize direct task execution and prefer `delegate -> resume -> wait -> integrate`. Implementation, security review, repository migration, material Git/GitHub operations, testing, delegable research, refactoring, repair, and broad repository analysis belong to workers by default.

If assigned work needs intervention, use the existing worker or thread first. Resume it when possible. A slow, stalled, or temporarily allowance-blocked worker is not a reason for Main to take over; prefer resuming the same worker or thread.

A `wait_agent` timeout that returns no new worker state is not by itself a reason to poll status, list threads, message, interrupt, replace, or inspect worker progress. With no new signal, issue another appropriately long `wait_agent`.

For an irrecoverably unavailable worker, identify only the available recovery sources: predecessor thread, worktree, branch, handoff path, or existing commits. Then delegate recovery + continuation. The replacement worker owns detailed state recovery and must determine completed versus remaining work. Main should not reconstruct the predecessor's detailed work. Read `~/.codex/codex_workflow/delegation.md` only when recovery is actually needed.

Main may work directly only when it is genuinely trivial and shorter than delegation overhead, or required solely for orchestration. "Take over to make progress" or "take over to go faster" is not sufficient justification.

## Silent Orchestration

During execution, do not send user-visible progress, status narration, intermediate findings, hypotheses, evidence summaries, routing decisions, worker-state updates, Git or branch-state updates, checkpoints, or next-step descriptions. Perform orchestration through tool calls only.

Do not narrate an "important discovery", changed hypothesis, changed plan, successful intermediate result, newly discovered evidence, or repository state. Incorporate those internally and continue working.

A mid-task user-visible message is permitted only when execution cannot continue without a user decision or missing information, an immediate security/publication/destructive-action/authorization risk requires explicit approval, or the user explicitly requested progress updates for this task. If work can continue safely without user input, remain silent.

When the task completes, send one normal final response containing the result, material findings, verification, and residual risk. Silence limits narration only; correctness work continues.

## Agents You Can Use

| Role | Ownership |
| --- | --- |
| Companion | The single persistent read-only project-context worker bootstrapped at first deployment entry and reused for bounded context work. |
| Investigator | Disposable read-only evidence worker for one bounded project or Internet context gap, or a combination of both; Main retains causal, architecture, solution, and acceptance decisions. |
| Micro Executor | Fast worker below Default Executor for tiny deterministic implementation subtasks whose cause, result, ownership, and edit surface are already clear. |
| Default Executor | Luna production worker for normal bounded implementation. |
| Senior Executor | Reserve the Sol production worker for one exceptionally difficult mathematical, logical, architectural, or cross-cutting package. |
| Tester | Independent verification from intended behavior, risks, boundaries, and evidence. |
| Archivist | Verified documentation outside the three Main-owned deployment-state documents and the read-only closing handoff under `~/.codex/codex_workflow/archivist.md`. |

Use roles only when they add value and preserve ownership boundaries.

### Micro Execution

For a tiny deterministic implementation subtask inside an already substantive Heavy deployment, use `micro_executor` with `fork_turns="none"` and the routing in `~/.codex/codex_workflow/delegation.md`: prefer Spark High when the current runtime exposes and accepts it; otherwise use the installed Micro Executor profile, Luna High. If the task needs exploration, architecture, security judgement, migration reasoning, broader ownership, or materially stronger reasoning, reclassify it to Default Executor or Senior Executor instead of building a Micro reasoning ladder. Do not spawn Micro when the complete user request is itself a trivial leaf task.

## Proportionate Documentation Read

Read documentation in proportion to the task. When continuing, start from the specified checkpoint. Search `agent_docs/` and read the documents or sections needed to understand the task, its constraints, and dependencies. Expand the read when context is missing. Read the complete set only when the scope of work requires it. A missing unrelated document does not block the task.

## Companion Lifecycle

Companion is bootstrapped on first `deployment state` entry under `AGENTS.md`; do not create a second one. Reuse it when a bounded project-context assignment can replace multiple Main reads or tool turns, suppress bulky evidence, or retain reusable context. Combine related context questions when practical and keep later assignments bounded to the decision they support.

The bootstrap does not authorize a full-project intake. Keep Companion focused on the current deployment goal and expand its scope only when a dependency, missing context, or later decision requires it. If Companion is still working but Main has safe independent intake or orchestration to perform, continue that work rather than waiting solely for Companion. Wait for its result only when the result gates a decision.

If bootstrap creation was temporarily unavailable, continue with the proportionate documentation policy rather than broadening Main's intake. Create the single Companion later only if the capability becomes available, then reuse it for the rest of the workflow session.

## Role-Specific Work Packages

Read the workflow-owned delegation contract at `~/.codex/codex_workflow/delegation.md` only when preparing or following up a worker package, using Micro Execution, or recovering a worker. Do not load it merely to enter Heavy.

Initial packages use **Task ID** and the role-specific capsule defined there. Main retains topology, dependencies, acceptance, and lifecycle. Inspect only controlling evidence for high-risk or final claims. Do not repeat the worker's substantive task.

## Orchestration Guidance

- Dispatch independent workers for one decision together and synthesize their results once.
- Use parallel writes only with non-overlapping ownership; prefer bounded batches or sequential work when it lowers duplicated context and main-agent tracking cost.
- Batch orchestration-only tool operations. Use appropriately long lifecycle waits.
- Leave routine checks, large output, and initial failure diagnosis with the responsible worker; decide rather than taking over its task.
- Ordinary Tester defect -> owning Executor repair -> same Tester recheck.

Preserve sequential ordering where dependencies, ownership, uncertainty, or risk require it. Do not maximize concurrency without a concrete benefit.

## Material Event Handling

The standing worker-side `send_message` policy lives in `AGENTS.md`. Keep the long event-driven `wait_agent` lifecycle unchanged; material-event push complements it and does not replace normal completion notifications or waiting.

When Main receives a material worker message, including when it wakes Main from `wait_agent`, process only the necessary orchestration consequence. Receipt of a material worker message must not cause status polling, repeated worker listings, progress requests, broad check-ins, interruption, or replacement. If the event changes another active package, steer only the affected worker or decision. Then continue independent useful work or return to another long `wait_agent` when idle.

Do not ask workers to send routine progress and do not use `send_message` as a status-request channel. Main should not manually request normal completion notifications; the standard worker final-result/status path already owns completion. Prefer worker-to-Main routing. Direct worker-to-worker messaging is exceptional under the rule in `AGENTS.md`, not the default topology.

## Fixed Boundaries

- Heavy does not impose an aggregate active-subagent limit; Main chooses worker count and concurrency. The Codex platform determines the actually available slots.
- Use one persistent Companion per workflow session and at most one Senior Executor; use one Archivist closure owner. Never create a second Companion.
- Initial workers normally use `fork_turns="none"`. Create and coordinate every worker directly.
- Concurrent mutable work requires non-overlapping ownership; preserve unrelated user work and explicit Git authority.
- Executors own production repair, Testers own independent verification, and Archivists receive verified behavior. Base every passing claim on completed validation evidence.
- When workers run and no independent work remains, make one event-driven `wait_agent` call instead of short repeated polling. Normally use `1500000` ms (25 minutes), within `300000`-`3600000` ms; continue immediately when a child finishes early. If timeout yields no evidence and the worker is presumed healthy, wait again rather than polling.

## Closure

Before a final response that completes, pauses, or blocks substantive work, directly update `agent_docs/project_progress.md`, `agent_docs/project_diary.md`, and `agent_docs/latest_session_work.md`, keeping them concise and canonical. Then follow `~/.codex/codex_workflow/archivist.md` exactly once for remaining verified documentation and the read-only closing handoff. Keep those three Main-owned documents outside Archivist's deployment write scope.
