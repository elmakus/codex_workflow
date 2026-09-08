# Owner workflow ownership and layout

This guide describes `1.1.14-private.3`, based on experimental upstream 1.1.14.

## Execution

Heavy is the only workflow route. Leaf-state questions and small bounded tasks
work directly from `AGENTS.md` without workers and without loading the Heavy
contract. Substantive work enters deployment state and loads `heavy_route.md`.

The main agent controls scope, architecture, dependencies, scheduling,
acceptance, and final claims. In Heavy it is an orchestrator rather than a
production executor: implementation, broad repository/security analysis,
testing, task-level Git/GitHub operations, repair, and delegable research stay
with the appropriate workers by default. When assigned work genuinely needs
intervention, Main should prefer the existing worker/thread and resume, wait,
message, or reassign the remainder rather than take over substantive work.

A timeout-only `wait_agent` result with no new evidence is not itself an
intervention signal. If the worker remains presumed healthy, Main should issue
another long wait instead of polling status, listing threads, inspecting
progress, interrupting, replacing, or taking over. The normal wait is 25 minutes
and returns early if the worker completes sooner.

Independent operations can be batched when parallelism is worthwhile; dependent
work and overlapping writes remain sequential. For repetitive independent units,
bounded batches or sequential execution are preferred when they reduce duplicate
context and main-agent coordination cost. Routine orchestration and successful
intermediate completions remain silent unless the user needs a decision/risk
update or explicitly asked for progress.

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

These user files are not separate copies for each project. An update replaces
the shared runtime once and migrates each intended existing project wrapper with
an explicit target. No installed files are changed merely by building or
publishing a package.

## Lifecycle and owner release channel

Installation and updates are explicit owner actions. Opening a project does not
install or update anything automatically.

From `1.1.14-private.3`, `check-update` queries GitHub Releases only for
`elmakus/codex_workflow`. A release is usable only when it is non-draft, has a
valid SemVer tag, and contains both the exact versioned ZIP and `SHA256SUMS`.
`update` downloads and checksum-verifies those assets, safely extracts the ZIP,
and delegates migration to the incoming runtime. There is no upstream release
channel and no background/startup auto-update.

The explicit verified local `--source` path remains available for recovery and
manual migration. It is also required for the first transition from private.2,
whose installed launcher predates owner-release discovery.

The incoming package represents the desired state of workflow-owned files.
Owned files present in the incoming package are added/replaced; files recorded
as previously owned but absent from the incoming package are removed. Workers
and workflow-owned skills use the same ownership-aware approach. Unrelated user
settings, unrelated workers/skills, content outside managed regions, project
instructions, personalization, documents and enabled/disabled state are
preserved. The update is backed up and applied transactionally.

A later migration removes retired workflow-owned files using ownership metadata,
while preserving unrelated user files. Removal is planned before confirmation
and preserves project documentation.

See the actual bundled `operate/` guide for the selected operation.
