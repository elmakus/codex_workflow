<!-- codex-workflow-id: viettran-edgeAI/codex_workflow -->
<!-- codex-workflow-managed-start -->
# AGENTS.md

## Design Principles

- Keep modules cohesive, interfaces explicit, coupling minimal, and behavior testable, replaceable, and reusable.
- Define proportionate acceptance and verification before implementation. Never weaken coverage, assertions, or failure visibility to save time.
- Avoid unnecessary process or safeguards; preserve unrelated user work and use verified facts in durable documentation.

## Rollout Efficiency

Batch independent reads, searches, metadata checks, and other known-input operations. Keep dependencies and overlapping mutations sequential. When using workers, dispatch independent workers, wait for the relevant set, and synthesize their reports once.

Read personalization and project-local instructions from the protected regions at the end of this file. Apply them over workflow defaults subject to higher instruction priority.

## Deployment Output Gate

In `deployment state`, before task completion, emit no user-visible prose. Continue through tool calls and worker orchestration only.

A non-final user-visible message is allowed only when execution cannot continue without user input, explicit approval is required for an immediate security/publication/destructive-action/authorization risk, or the user explicitly requested progress updates for this task.

Before every non-final user-visible message, ask: **Can execution safely continue without user input?** If yes, do not send the message.

Intermediate findings, discoveries, changed hypotheses, changed plans, worker results, repository or Git state, checkpoints, and descriptions of next steps are never reasons to speak. At completion, send one normal final response.

## Working State

Use `deployment state` for broad, possibly multi-session deployment plans. Use `leaf state` otherwise, including general questions and small bounded operations.

## Project Documentation

Use the durable documents under `agent_docs/`: `project_overview.md` (goals, architecture, workflow, decisions), `project_core_tech.md` (technology notes), `project_structure.md` (layout and ownership), `project_progress.md` (progress and milestone), `project_diary.md` (lasting decisions and lessons), `latest_session_work.md` (handoff evidence), and any module-specific Markdown.

In deployment state, you own `project_progress.md`, `project_diary.md`, and `latest_session_work.md`. Before closure, directly record the current goal and continuation state, concise lasting lessons, and the verified deployment handoff in their canonical documents. Archivist owns other assigned project and public documentation from verified facts, including overview, structure, core technologies, and module documents. Assign module documents explicitly. Perform a direct user-requested document edit yourself outside deployment.

Keep raw logs, temporary reasoning, and short-lived checkpoints out of durable documents; give each fact one canonical home. Never delete a main project document without warning and a second explicit confirmation.

## Workflow

In leaf state, work directly without reading `~/.codex/codex_workflow/heavy_route.md` or spawning subagents. When work is substantive, enter `deployment state`, bootstrap the session Companion below, read that Heavy contract, and use only the worker capabilities that add value to the task.

## Early Companion

On the first transition into `deployment state` in a workflow session, immediately create one persistent Companion with `agent_type="companion"`, `task_name="companion"`, and `fork_turns="none"`, or reuse the existing Companion. Do this before broad project discovery, planning, modifying project state, or dispatching any other worker, while Main's context is still small. Never create a second Companion in the same workflow session.

Prepare the bootstrap assignment from the user request and already-known context only; do not perform broad discovery just to prepare it. Include **Task ID**, **Project Context Scope**, **Context Task + Goal**, and **Main-Agent Context Guidance**. Keep the scope bounded to the current deployment goal. Ask Companion to inspect only directly relevant checkpoints, documents, or project surfaces, retain useful supporting detail, and return a compact source-linked brief. Do not ask it to read the complete `agent_docs/` framework or unrelated module documents unless the current scope actually requires them.

After spawning Companion, continue independent Heavy intake and orchestration immediately. Do not wait solely for Companion unless its result is needed for a decision. Reuse the same Companion for later context assignments and later deployments in the same workflow session. If Companion creation is temporarily unavailable, continue with proportionate Main reads rather than compensating with a broad documentation intake; create the single Companion later only if the capability becomes available.

## Proportionate Documentation Read

Read documentation in proportion to the task. When continuing, start from the specified checkpoint. Search `agent_docs/` and read the documents or sections needed to understand the task, its constraints, and dependencies. Expand the read when context is missing. Read the complete set only when the scope of work requires it. A missing unrelated document does not block the task.

## Platform Paths

Interpret `/` as a platform-neutral separator and translate paths for the current operating system and shell.
<!-- codex-workflow-managed-end -->

<!-- codex-workflow-project-personalization-start -->
<!-- codex-workflow-project-personalization-end -->

<!-- codex-workflow-project-local-instructions-start -->
<!-- codex-workflow-project-local-instructions-end -->
