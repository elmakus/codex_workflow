# elmakus codex_workflow fork

Version **1.1.17-private.4**, based directly on upstream prerelease `v1.1.17`
commit `414a5d301ff17ca6e655330474c8346863d0d5d0`.

This public fork keeps upstream's lifecycle/runtime foundation while applying
owner-specific orchestration, model, update-channel, and safety choices.

## Private behavior

- **Heavy is the only workflow route.** Leaf-state questions and small bounded
  tasks work directly without subagents and without reading `heavy_route.md`.
- Deployment state has a hard user-visible output gate in `AGENTS.md`: if work
  can continue safely without user input, Main remains silent until the final
  response. Intermediate findings, plan changes, worker results, repository
  state, and next-step narration are not reasons to speak.
- Heavy uses progressive disclosure: standing orchestration stays in
  `heavy_route.md`; detailed work-package, Micro Execution, follow-up, and
  recovery guidance lives in `delegation.md` and is loaded only when needed.
- Micro Executor is a distinct seventh worker below Default Executor. Its stable
  profile is Luna High; when the current Codex runtime/account supports it, the
  same role may run with GPT-5.3-Codex-Spark at high reasoning. Spark is optional.
- Default Executor uses Luna Max. Senior Executor uses Sol Medium. Tester,
  Companion, Investigator, and Archivist use Luna Max.
- Investigator may inspect one bounded project evidence gap, Internet sources,
  or both, while remaining read-only. Main retains causal, architecture,
  solution, integration, and acceptance decisions.
- Companion is created once at the first deployment-state entry while Main's
  context is still small, then reused for bounded context work. Its bootstrap is
  scoped to the current goal and does not trigger a full `agent_docs/` or
  unrelated-module intake.
- Main owns deployment updates to `project_progress.md`, `project_diary.md`, and
  `latest_session_work.md`. Archivist handles other assigned documentation and
  the read-only closing handoff.
- Heavy has no workflow-imposed aggregate worker limit. The workflow does not
  write a fixed `max_concurrent_threads_per_session`; available concurrency is
  left to the Codex platform/account.
- Heavy is orchestrator-first, uses long event-driven waits, treats an empty
  timeout as a reason to wait again rather than poll, and keeps routine
  orchestration silent unless the user needs a decision or risk update.
- Running workers may use `send_message` to `/root` only for rare material
  mid-task `BLOCKER`, `COURSE_CHANGE`, or `CRITICAL_PARTIAL` events. Routine
  progress and normal completion never use that channel; receipt of a material
  event, including a `wait_agent` wake, complements the existing long-wait
  lifecycle rather than replacing it.
- No token-accounting skill, deployment counting marker, usage-report table, or
  reporting obligation is included.
- Release discovery and downloads are restricted to GitHub Releases published
  from `elmakus/codex_workflow`. There is no background/startup auto-update and
  no release channel from upstream.
- Installation and updates happen only when the owner asks.

## Workflow and roles

For substantive work Main enters deployment state, immediately bootstraps the
single session Companion, and loads `codex_workflow/heavy_route.md`. Companion
starts only bounded goal-relevant context work; Main can continue independent
Heavy intake and orchestration without waiting for it. Main chooses only useful
worker capabilities and owns scope, architecture, scheduling, integration,
acceptance, and final claims. Before preparing/following up a worker package,
using Micro Execution, or recovering a worker, Main loads
`~/.codex/codex_workflow/delegation.md`.

| Role | Model / reasoning | Responsibility |
| --- | --- | --- |
| Micro Executor | Spark / high when available; otherwise Luna / high | Tiny deterministic implementation subtasks inside Heavy. |
| Default Executor | Luna / max | Normal bounded implementation and repair. |
| Senior Executor | Sol / medium | Exceptionally difficult bounded production or solution work. |
| Tester | Luna / max | Independent verification. |
| Companion | Luna / max | Persistent read-only project context, created once at first deployment entry and reused. |
| Investigator | Luna / max | Disposable read-only project/Internet evidence investigation. |
| Archivist | Luna / max | Verified documentation outside Main-owned deployment-state docs and closing handoff. |

If a micro task ceases to be tiny and deterministic, Main reclassifies it
directly to Default Executor or Senior Executor; there is no Micro reasoning
escalation ladder.

## Documentation locations

Project documents stay in `<project>/agent_docs/`: `project_overview.md`,
`project_core_tech.md`, `project_structure.md`, `project_progress.md`,
`project_diary.md`, `latest_session_work.md`, and assigned module documents.
Existing documents and protected project instructions are preserved during
migration. The progress and latest-session templates contain project state only,
not embedded maintenance instructions.

`~/.codex/codex_workflow/operate/` holds workflow command guides and version
metadata. The lifecycle launcher is
`~/.codex/codex_workflow/runtime/workflow.py`.

## Updates

The normal update channel is the owner's GitHub Releases in
`elmakus/codex_workflow`.

`codex_workflow --check-update` performs a read-only check. It accepts only
non-draft SemVer releases containing both the expected versioned ZIP and
`SHA256SUMS`.

`codex_workflow --update` downloads those assets, verifies SHA-256, applies
strict URL/path/size checks, safely extracts and validates the package, and
delegates migration to the incoming runtime. A verified local `--source` path
remains available internally for recovery and explicit/manual migrations.

The incoming package is the desired state of workflow-owned files. Unrelated
Codex settings/workers/skills, user content outside managed regions,
project-local instructions, personalization, and `agent_docs/` are preserved.
Updates create a timestamped backup and apply through a compensating transaction.

## Commands

| Prompt | Purpose |
| --- | --- |
| `codex_workflow --install` | Install into the explicitly selected project. |
| `codex_workflow --check-update` | Read-only check of owner releases. |
| `codex_workflow --update` | Install the latest verified owner release into the selected project/runtime. |
| `codex_workflow --personal` | Change project workflow preferences. |
| `codex_workflow --disable` / `--enable` | Disable or enable the selected project. |
| `codex_workflow --remove` | Preview removal, then remove owned files after explicit confirmation; preserve project documents. |

For release preparation and provenance see [RELEASING.md](RELEASING.md).
For the ownership map see [workflow_break_down.md](workflow_break_down.md).
