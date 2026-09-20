# Owner workflow ownership and layout

This guide describes the current fork architecture at packaged version
`1.1.17-private.12`. It incorporates selected upstream 1.1.18 behavior while
keeping the fork-specific Muse lifecycle and accepted orchestration decisions
authoritative.

## Deep dive: orchestration design

This section adapts the useful orchestration lessons from upstream to the
architecture that this fork actually supports. It is explanatory documentation,
not a second instruction surface; the executable contracts remain
`codex_workflow/AGENTS.md`, `heavy_route.md`, `delegation.md`, the worker
definitions, and the runtime modules.

### Delegation is an explicit contract

Effective delegation is not "send everything to workers." Main retains scope,
architecture, dependency ordering, integration, acceptance, and the decisions
that need the broadest project view. Workers receive bounded packages with the
authority, context, goal, constraints, and evidence obligations needed for one
role-owned result.

That split reduces unnecessary Main context without giving up control. It also
keeps failures attributable: production work returns to an Executor, independent
verification stays with Tester, and documentation work stays with Archivist
unless a task is genuinely trivial and remains in leaf state.

### Context is budgeted deliberately

Main reads decision-critical project context directly and expands only when the
task requires it. Explorer is the bounded read-only mechanism for broader
project-context discovery, mapping, and evidence retrieval when loading that
surface into Main would be wasteful.

Explorer is not persistent session memory and does not replace Investigator.
When a bounded problem genuinely needs investigation, the workflow uses exactly
three independent Investigator lanes with one shared Problem ID, distinct Task
IDs, and complementary evidence angles. Main compares evidence and
disagreements; lane count is not a voting rule.

### One role model, two worker runtimes

The supported role set is Explorer, Investigator, Default Executor, Senior
Executor, Tester, and Archivist. The role responsibilities stay stable across
the two compute profiles:

- `plus` runs all six roles through the internal Codex worker lifecycle.
- `muse-max` runs all six through the retained Muse logical-session/process
  lifecycle.

Main remains the orchestration owner in both profiles. Worker correctness does
not depend on direct sibling messaging; normal and final results return to Main.

### Mid-task communication is intentionally asymmetric

Internal Codex workers under `plus` may push only three material event classes
to Main: `BLOCKER`, `COURSE_CHANGE`, and `CRITICAL_PARTIAL`. Routine
progress, heartbeats, ETA chatter, ordinary partial findings, and normal
completion stay on the standard result path.

The Muse-backed profile uses its normal bounded invocation/session lifecycle.
The workflow does not add a second background channel merely to imitate an
internal-worker mechanism. This keeps communication aligned with the real
runtime rather than adding orchestration machinery that correctness would have
to depend on.

### Independence survives repair

Tester is a separate verification owner from the implementing Executor. A
normal correction cycle is Executor -> Tester -> owning Executor repair -> same
independent Tester full recheck of the new subject, unless an explicit freshness
requirement or unsafe session recovery requires a new logical worker.

This makes review evidence about an exact implementation subject rather than a
general statement that a task "looked good" at some earlier point.

### Optimize coordination, not ceremony

The workflow batches only work that is genuinely independent, waits on workers
instead of polling them for status, and transfers only the context needed for
the next decision. New layers, pseudo-channels, or negative policy text are not
added merely to describe a capability that the active runtime does not use.

The goal is a small, auditable orchestration contract: Main makes the decisions
that need global context; workers own bounded execution and evidence; durable
project documents carry verified state across sessions.

## Execution

Heavy is the only workflow route. Leaf-state questions and genuinely trivial
bounded actions work directly from `AGENTS.md` without workers and without
loading the Heavy contract. Bounded but nontrivial work enters deployment state
and loads `heavy_route.md`.

Main keeps project-document intake proportionate to the current task and uses
Explorer for bounded broader project-context discovery, mapping, and evidence
retrieval. Detailed worker-package, follow-up, and recovery instructions live in
`delegation.md` and are loaded only when Main actually needs those operations.

Main controls scope, architecture, dependencies, scheduling, acceptance, and
final claims. In Heavy it is strictly an orchestrator rather than a production
executor: implementation, broad repository/security analysis, testing,
task-level Git/GitHub operations, repair, and delegable research stay with the
appropriate workers. Capacity pressure does not transfer that ownership to Main.

A timeout-only `wait_agent` result with no new evidence is not itself an
intervention signal. If the worker remains presumed healthy, Main issues another
long wait instead of polling status. The normal wait is 25 minutes and returns
early if the worker completes sooner.

Under `plus`, internal Codex workers may push one rare material mid-task event
to Main with `send_message`. Only `BLOCKER`, `COURSE_CHANGE`, and
`CRITICAL_PARTIAL` qualify; progress, ETA, heartbeats, routine partial
findings, and normal completion stay on the standard worker result path. Material
events route only worker -> Main and do not replace `wait_agent` or normal
completion.

User-visible orchestration follows one of exactly two supported profiles:
restrained meaningful milestones in `plus`, and normal concise milestone
updates in `muse-max`. Neither profile exposes hidden reasoning,
instruction-conflict narration, or routine worker-state chatter.

| Role | `plus` | `muse-max` | Responsibility |
| --- | --- | --- | --- |
| Explorer | Luna/max | Muse Contributor/max | Bounded read-only project-context discovery, mapping, and evidence retrieval. |
| Investigator | Luna/max | Muse Contributor/max | Bounded fault/solution/feasibility/prior-art research; qualifying problems use exactly three independent lanes. |
| Default Executor | Luna/max | Muse Contributor/max | Normal bounded implementation and repair. |
| Senior Executor | Sol/medium | Muse Contributor/max | Exceptionally difficult bounded production or solution work. |
| Tester | Luna/max | Muse Contributor/max | Independent verification. |
| Archivist | Luna/max | Muse Contributor/max | Verified documentation outside Main-owned deployment-state docs and closing handoff. |

The compute profile is global user-runtime state, not project personalization.
It is stored in `~/.codex/codex_workflow/settings.toml`; missing settings on an
older installation mean `plus`. Under `plus`, all six roles use the internal
Codex worker lifecycle. Under `muse-max`, all six roles use the retained Muse
logical-session/process lifecycle with Muse Spark 1.3 Contributor Max. Main is
outside this mechanism. The workflow never auto-detects a subscription.

Archivist has no usage-reporting responsibility. This package does not include
token accounting, deployment counting markers, a reporting skill, or report
scripts.

## Project files

Each project keeps its own `AGENTS.md`, protected
`.codex_workflow_hidden_resources/` state, and `agent_docs/` documentation.

- `project_overview.md`: project goals, architecture, workflow and decisions.
- `project_core_tech.md`: technology and architecture details.
- `project_structure.md`: layout and ownership.
- `project_progress.md`: goal, progress and next milestone.
- `project_diary.md`: lasting decisions and lessons.
- `latest_session_work.md`: verified handoff and continuation point.
- Module documents: assigned explicitly as needed.

During deployment Main owns updates to `project_progress.md`, `project_diary.md`,
and `latest_session_work.md`. Archivist may initialize listed template/recovery
files during installation, but during deployment it leaves those three files
unchanged and handles other assigned documentation plus the read-only closing
handoff.

## Shared user files

`~/.codex/codex_workflow/` contains the compact Heavy contract,
`delegation.md`, `archivist.md`, runtime modules, installed templates, ownership
state, and the persistent compute-profile selection. `operate/` contains
lifecycle guides and version metadata; `runtime/workflow.py` is the launcher.
Worker definitions are installed under `~/.codex/agents/`.

The workflow enables Codex multi-agent support but does not impose the retired
`max_concurrent_threads_per_session = 20` setting. Migration removes that old
workflow-owned key while preserving unrelated Codex configuration.

## Lifecycle and owner release channel

Installation, updates, and compute-profile changes are explicit owner actions.
Opening a project does not install, update, or change compute profile
automatically.

`check-update` queries GitHub Releases only for `elmakus/codex_workflow`. A
release is usable only when it is non-draft, has a valid SemVer tag, and contains
both the exact versioned ZIP and `SHA256SUMS`. `update` checksum-verifies the
assets, validates trusted URLs and bounded archive input, safely extracts the
ZIP, and delegates migration to the incoming runtime. There is no upstream
release channel and no background/startup auto-update.

The incoming package represents the desired state of workflow-owned files.
Owned files present in the package are added/replaced; previously owned files
absent from it are retired. Workers and workflow-owned skills use the same
ownership-aware approach. Unrelated user settings, unrelated workers/skills,
content outside managed regions, project instructions, personalization,
documents, enabled/disabled state, and the selected compute profile are
preserved. Updates are backed up and applied transactionally.
