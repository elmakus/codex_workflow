<!-- codex-workflow-id: viettran-edgeAI/codex_workflow -->
<!-- codex-workflow-managed-start -->
# AGENTS.md

## Design Principles

- Keep modules cohesive, interfaces explicit, coupling minimal, and behavior
  testable, replaceable, and reusable.
- Define proportionate acceptance and verification before implementation. Never
  weaken coverage, assertions, or failure visibility to save time or tokens.
- Avoid unnecessary process and safeguards. Preserve unrelated user work and
  use verified facts in durable documentation.

Read project personalization and project-local instructions from the protected
regions at the end of this file. Apply them over conflicting workflow defaults
while preserving higher-level instruction priority.

## Working State

- Use `deployment state` when planning or executing a broad, possibly
  multi-session deployment plan.
- Use `leaf state` outside that plan, including general questions and small,
  bounded edits or operations.

## Project Documentation

Use the durable project documents under `agent_docs/`:

- `project_overview.md`: goals, architecture, workflow, and major decisions.
- `project_core_tech.md`: concise special technology or architecture notes.
- `project_structure.md`: layout, modules, components, and ownership.
- `project_progress.md`: goal, overall progress, current position, next milestone.
- `project_diary.md`: distilled decisions, discarded approaches, mistakes, and
  reusable lessons.
- `latest_session_work.md`: detailed handoff evidence and continuation point.
- Module-specific documents, when present.

Edit `project_progress.md` and `latest_session_work.md` only when using
`deployment state` or when the user explicitly requests it. Own them during
normal execution.

Keep raw logs, temporary reasoning, and short-lived checkpoints out of durable
documents. Give each fact one canonical home. Never delete a main project
document without warning the user and receiving a second explicit confirmation.

## Route Selection

Select one of these routes:

- **Light**: work directly in leaf state without subagents.
- **Medium**: own planning, diagnosis, implementation, and verification; use
  bounded support capabilities as defined in
  `~/.codex/codex_workflow/medium_route.md`.
- **Heavy**: delegate bounded production, verification, documentation,
  project-context, and Internet-research work under
  `~/.codex/codex_workflow/heavy_route.md`.

Follow the user's route selection. Use Heavy when the user does not select a
route. Keep the selected route until the user changes it or the session ends.
Enter `deployment state` for Medium or Heavy only when the work is substantive.

## Platform Paths

Interpret `/` as a platform-neutral separator. Translate paths to the current
operating system and shell when running filesystem commands.
<!-- codex-workflow-managed-end -->

<!-- codex-workflow-project-personalization-start -->
<!-- codex-workflow-project-personalization-end -->

<!-- codex-workflow-project-local-instructions-start -->
<!-- codex-workflow-project-local-instructions-end -->
