# elmakus codex_workflow fork

Version **1.1.14-private.3**, based on upstream experimental 1.1.14 commit
`a224f32c423ef56be322de160d5440bba0a786b2`.

This public fork keeps upstream's lifecycle/runtime foundation while applying
owner-specific orchestration and model choices.

## Private behavior

- **Heavy is the only workflow route.** Leaf-state questions and small bounded
  tasks work directly without subagents and without reading `heavy_route.md`.
  The Heavy contract is loaded only for substantive deployment-state work.
- Luna roles use `max` reasoning. Senior Executor uses Astra `low`.
- The Codex runtime keeps multi-agent enabled with a fixed ceiling of 20
  concurrent subagents per session; Heavy itself does not impose a second
  aggregate worker-count limit.
- Heavy is orchestrator-first, uses long event-driven worker waits, treats an
  empty timeout as a reason to wait again rather than poll, and keeps routine
  orchestration silent unless the user needs to know something.
- No token accounting, reporting skill, deployment counting marker, or report
  table is included.
- Release discovery and downloads are restricted to GitHub Releases published
  from `elmakus/codex_workflow`. There is no background/startup auto-update and
  no release channel from upstream.
- Installation and updates happen only when the owner asks. Opening a new
  project does not install or update anything.

## Workflow and roles

The project `AGENTS.md` handles leaf-state work directly. For substantive work
the main agent enters deployment state and loads `codex_workflow/heavy_route.md`.
It then chooses only the worker capabilities useful to the task and owns scope,
architecture, scheduling, integration, acceptance, and final claims.

The six roles are Default Executor, Senior Executor, Tester, Companion,
Investigator, and Archivist. Companion is created on demand.

| Role | Model / reasoning | Responsibility |
| --- | --- | --- |
| Default Executor | Luna / max | Bounded implementation and repair. |
| Senior Executor | Astra / low | Exceptionally difficult production or solution work. |
| Tester | Luna / max | Independent verification. |
| Companion | Luna / max | Read-only project context, created on demand. |
| Investigator | Luna / max | Read-only external research. |
| Archivist | Luna / max | Verified documentation and closing handoff. |

## Documentation locations

Project documents stay in `<project>/agent_docs/`: `project_overview.md`,
`project_core_tech.md`, `project_structure.md`, `project_progress.md`,
`project_diary.md`, `latest_session_work.md`, and assigned module documents.
The main agent owns lasting diary updates during deployment; Archivist owns
assigned documentation and closing handoffs. Existing documents and protected
project instructions are preserved during migration.

`~/.codex/codex_workflow/operate/` holds workflow command guides and version
metadata. The lifecycle launcher is
`~/.codex/codex_workflow/runtime/workflow.py`.

## Updates

After **1.1.14-private.3** is installed, the normal update channel is the owner's
GitHub Releases in `elmakus/codex_workflow`.

`codex_workflow --check-update` performs a read-only check. It accepts only
non-draft SemVer releases containing both the expected versioned ZIP and
`SHA256SUMS`.

`codex_workflow --update` downloads those two assets, verifies SHA-256, safely
extracts the package, validates it, and delegates migration to the incoming
runtime. A verified local `--source` path remains available internally for
recovery and explicit/manual migrations.

The first migration from **1.1.14-private.2** still needs the explicit local
package path because that already-installed runtime predates owner-release
discovery. From private.3 onward, future owner releases can use the normal
check/update commands.

The update planner treats the incoming package as the desired state of
workflow-owned files: new owned files are created, changed owned files are
replaced, and previously owned files absent from the new package are removed.
Unrelated Codex settings/workers/skills, user content outside managed regions,
project-local instructions, personalization, and `agent_docs/` are preserved.
A timestamped backup is created before the transaction.

The shared `~/.codex` runtime is updated once, while each existing project
wrapper/state is migrated explicitly with its own `--project` target.

## Commands

| Prompt | Purpose |
| --- | --- |
| `codex_workflow --install` | Install into the explicitly selected project. |
| `codex_workflow --check-update` | Read-only check of `elmakus/codex_workflow` releases. |
| `codex_workflow --update` | Install the latest verified owner release into the selected project/runtime. |
| `codex_workflow --personal` | Change project workflow preferences. |
| `codex_workflow --disable` / `--enable` | Disable or enable the selected project. |
| `codex_workflow --remove` | Preview removal, then remove owned files after explicit confirmation; preserve project documents. |

For release preparation and provenance see [RELEASING.md](RELEASING.md).
For the ownership map see [workflow_break_down.md](workflow_break_down.md).
