# Private workflow ownership and layout

This guide describes `1.1.14-private.2`, based on experimental upstream 1.1.14.

## Execution

Heavy is the only workflow route. Leaf-state questions and small bounded tasks
work directly from `AGENTS.md` without workers and without loading the Heavy
contract. Substantive work enters deployment state and loads `heavy_route.md`.

The main agent controls scope, architecture, dependencies, scheduling,
acceptance, and final claims. Independent operations can be batched; dependent
work and overlapping writes remain sequential. Companion is optional and
created when bounded context work is useful. Reports have role-specific word
budgets, with supporting evidence retained outside routine reports.

Heavy does not impose an aggregate active-subagent limit; the main chooses
worker count and concurrency for each task. The Codex platform configuration
keeps multi-agent enabled and enforces `max_concurrent_threads_per_session = 20`.

| Role | Model / reasoning | Responsibility |
| --- | --- | --- |
| Default Executor | Luna / max | Bounded implementation and repair. |
| Senior Executor | Astra / low | Exceptionally difficult production or solution work. |
| Tester | Luna / max | Independent verification. |
| Companion | Luna / max | Read-only project context, created on demand. |
| Investigator | Luna / max | Read-only external research. |
| Archivist | Luna / max | Verified documentation and closing handoff. |

Archivist has no usage-reporting responsibility. This package does not include
token accounting, deployment counting markers, a reporting skill, or report
scripts. Documentation closure remains part of substantive Heavy work.

## Project files

Each project keeps its own `AGENTS.md`, protected
`.codex_workflow_hidden_resources/` state, and `agent_docs/` documentation.
The same `agent_docs/` location was used by 1.1.13; migration does not relocate
these documents.

- `project_overview.md`: project goals, architecture, workflow and decisions.
- `project_core_tech.md`: technology and architecture details.
- `project_structure.md`: layout and ownership.
- `project_progress.md`: goal, progress and next milestone.
- `project_diary.md`: lasting decisions and lessons; main-agent ownership.
- `latest_session_work.md`: closing evidence and continuation point.
- Module documents: assigned explicitly as needed.

During deployment Archivist owns assigned documents and closing progress and
handoff records. The main updates the diary. Project-specific handoffs outside
`agent_docs/`, when required by local instructions, retain their own paths.

## Shared user files

`~/.codex/codex_workflow/` contains the Heavy contract, `archivist.md`, runtime
modules, installed templates, and ownership state. `operate/` contains lifecycle
guides and version metadata; `runtime/workflow.py` is the launcher. Worker
definitions are installed under `~/.codex/agents/`; the marked user instruction
region and workflow-owned settings are shared as well.

These user files are not separate copies for each project. The planned manual
rollout replaces the shared runtime once and migrates every existing project
wrapper in the same operation, using explicit targets. No installed files are
changed merely by building this package.

## Lifecycle

Installation is explicit. No startup instruction installs into a new Git root.
The CLI has no release discovery or download path. Manual `update` requires an
explicit verified local source and preserves unrelated settings, project
instructions, documents and enabled/disabled state. When the shared runtime is
already current, an older selected project can still be migrated.

A later migration removes retired workflow-owned role and reporting-skill
files using ownership metadata, while preserving unrelated user skills. Removal
is planned before confirmation and preserves the project documentation.

See the actual bundled `operate/` guide for the selected operation.
