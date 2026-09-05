# Private codex_workflow

Version **1.1.14-private.2**, based on upstream experimental 1.1.14 commit
`a224f32c423ef56be322de160d5440bba0a786b2`.

This private package keeps upstream's task-specific orchestration, batched
independent work, on-demand Companion, concise worker reports, and Archivist
for documentation and closing handoffs.

## Private behavior

- **Heavy is the default.** Questions and small bounded tasks still use its
  direct path with no workers.
- Every Luna role uses `max` reasoning. Senior Executor remains Sol `medium`.
- No token accounting, reporting skill, deployment counting marker, or report
  table is included.
- No release checks, network downloads, automatic updates, or release publishing.
  An explicit local package is required for a manual migration.
- Installation happens only when the owner asks. Opening a new project does
  not install anything or interrupt its task.

## Routes and roles

| Route | Work ownership |
| --- | --- |
| Light | Main agent works directly, without subagents. |
| Medium | Main owns implementation and verification; Companion, Investigator, and Archivist provide bounded support. |
| Heavy (default) | Main directs the task and delegates bounded execution, verification, research, context, and documentation where useful. |

The six roles are Default Executor, Senior Executor, Tester, Companion,
Investigator, and Archivist. Companion is created on demand. Archivist replaces
upstream 1.1.13's separate Doc-writer and Closure Steward.

## Documentation locations

Project documents stay in `<project>/agent_docs/`: `project_overview.md`,
`project_core_tech.md`, `project_structure.md`, `project_progress.md`,
`project_diary.md`, `latest_session_work.md`, and assigned module documents.
The main agent owns lasting diary updates during deployment; Archivist owns
assigned documentation and closing handoffs. Existing documents and protected
project instructions are preserved during a manual migration.

`~/.codex/codex_workflow/operate/` holds workflow command guides and version
metadata. It is not the destination for project documentation. The lifecycle
launcher is `~/.codex/codex_workflow/runtime/workflow.py`.

## Installation and manual migration

Requires Python 3.11 or newer. Build or obtain the reviewed private ZIP and its
matching `SHA256SUMS`, verify and extract it, then read the included
`codex_workflow/operate/bootstrap.md` for a fresh user runtime or
`codex_workflow/operate/update.md` for an existing runtime. Installation and
migration are separate owner-requested operations; producing a ZIP installs
nothing.

For 1.1.13 installations, run a later authorized migration with the incoming
package's `runtime/workflow.py`, because the old launcher cannot discover the
new `operate/` layout. The planned rollout covers all existing projects in
one owner-authorized operation: replace the shared user runtime once, then
migrate every project wrapper using an explicit `--project` target for each.
Project instruction files and documents remain separate. Do not stop after
updating only part of the intended project set or automatically discover and
install into unrelated repositories.

## Commands

| Prompt | Purpose |
| --- | --- |
| `codex_workflow --install` | Install into the explicitly selected project. |
| `codex_workflow --personal` | Change project workflow preferences. |
| `codex_workflow --update` | Manually migrate the selected project using an explicitly supplied verified local package. |
| `codex_workflow --disable` / `--enable` | Disable or enable the selected project. |
| `codex_workflow --remove` | Preview removal, then remove owned files after explicit confirmation; preserve project documents. |

`--check-update` is not provided. No command discovers or downloads releases.
For source preparation, package verification and provenance see [RELEASING.md](RELEASING.md).
For the ownership map see [workflow_break_down.md](workflow_break_down.md).
