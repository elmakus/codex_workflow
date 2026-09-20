<!-- codex-workflow-id: viettran-edgeAI/codex_workflow -->
<!-- codex-workflow-managed-start -->
# AGENTS.md

## Design Principles

- Keep modules cohesive, interfaces explicit, coupling minimal, and behavior testable, replaceable, and reusable.
- Define proportionate acceptance and verification before implementation. Never weaken coverage, assertions, or failure visibility to save time.
- Avoid unnecessary process or safeguards; preserve unrelated user work and use verified facts in durable documentation.

## Rollout Efficiency

Batch independent reads, searches, metadata checks, and other known-input operations. Keep dependencies and overlapping mutations sequential. When using workers, dispatch independent workers when the active worker runtime supports safe concurrency, wait for the relevant set, and synthesize their reports once.

Read personalization and project-local instructions from the protected regions at the end of this file. Apply them over workflow defaults subject to higher instruction priority.

## Deployment Communication

In `deployment state`, follow the profile-specific user-communication policy in `~/.codex/codex_workflow/heavy_route.md`. The active compute profile controls whether orchestration is silent, restrained, or uses normal concise progress updates.

Regardless of profile, never expose hidden reasoning or narrate internal instruction-conflict resolution. User-visible updates must remain concise, relevant, and outcome-oriented. Questions required to unblock execution and immediate security, publication, destructive-action, or authorization risks may always be raised.

## Working State

Use `deployment state` for substantive work, including any implementation, testing, repair, migration, broad analysis, or material repository operation. Use `leaf state` only for questions and genuinely trivial bounded actions.

## Project Documentation

Use the durable documents under `agent_docs/`: `project_overview.md` (goals, architecture, workflow, decisions), `project_core_tech.md` (technology notes), `project_structure.md` (layout and ownership), `project_progress.md` (progress and milestone), `project_diary.md` (lasting decisions and lessons), `latest_session_work.md` (handoff evidence), and any module-specific Markdown.

In deployment state, you own `project_progress.md`, `project_diary.md`, and `latest_session_work.md`. Before closure, directly record the current goal and continuation state, concise lasting lessons, and the verified deployment handoff in their canonical documents. Archivist owns other assigned project and public documentation from verified facts, including overview, structure, core technologies, and module documents. Assign module documents explicitly. Perform a direct user-requested document edit yourself outside deployment.

Keep raw logs, temporary reasoning, and short-lived checkpoints out of durable documents; give each fact one canonical home. Never delete a main project document without warning and a second explicit confirmation.

## Workflow

In leaf state, work directly without reading `~/.codex/codex_workflow/heavy_route.md` or spawning subagents. Do not classify nontrivial work as leaf merely because it is bounded or short. When work is substantive, enter `deployment state`, read that Heavy contract, and delegate execution under it. Use Explorer for bounded project-context discovery when broader mapping or evidence retrieval would reduce Main context load.

## Bounded Context Discovery

Main keeps documentation intake proportionate to the current task. When broader project-context discovery, mapping, or evidence retrieval would otherwise consume substantial Main context, create a bounded disposable Explorer assignment with **Task ID**, **Project Context Scope**, **Context Task + Goal**, and **Main-Agent Context Guidance**.

Explorer is read-only and task-scoped. It is not a persistent session secretary and must not bootstrap a complete-project or complete-`agent_docs/` intake unless the bounded assignment actually requires that surface. Explorer returns the smallest complete evidence-linked map or retrieval result directly to Main and does not coordinate another worker.

## Worker Material Event Push

For internal Codex workers, when the runtime exposes `send_message`, a running worker may send one concise message to `/root` only for a material mid-task event whose value would materially decrease if delayed until its normal final result:

- `BLOCKER` — the worker cannot make useful progress without a Main-owned decision or missing input.
- `COURSE_CHANGE` — evidence invalidates, cancels, or materially changes work currently being performed by Main or another worker.
- `CRITICAL_PARTIAL` — an immediately actionable partial result where delaying delivery is likely to cause significant wasted work or an incorrect orchestration decision.

Use `EVENT_TYPE | Task ID | essential fact or blocker | requested action`. Do not use `send_message` for routine progress, heartbeats, ETA, "still working", status chatter, ordinary partial findings, or normal completion. Do not resend an unchanged event. Normal completion stays on the standard worker final-result/status path and returns directly to Main. After sending, continue any independent useful work; wait only when genuinely blocked. Route all material events to `/root`/Main; direct sibling messaging is not part of the workflow contract.

Under `muse-max`, the six Muse-backed roles do not have the Codex `send_message` channel. Each bounded Muse turn ends at process completion or failure even when its logical session remains reusable; do not emulate material-event push with polling or unmanaged background processes. Their final result returns directly to Main.

## Proportionate Documentation Read

Read documentation in proportion to the task. When continuing, start from the specified checkpoint. Search `agent_docs/` and read the documents or sections needed to understand the task, its constraints, and dependencies. Expand the read when context is missing. Read the complete set only when the scope of work requires it. A missing unrelated document does not block the task.

## Platform Paths

Interpret `/` as a platform-neutral separator and translate paths for the current operating system and shell.
<!-- codex-workflow-managed-end -->

<!-- codex-workflow-project-personalization-start -->
<!-- codex-workflow-project-personalization-end -->

<!-- codex-workflow-project-local-instructions-start -->
<!-- codex-workflow-project-local-instructions-end -->
