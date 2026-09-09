# Owner workflow ownership and layout

This guide describes `1.1.17-private.2`, based directly on upstream prerelease
`v1.1.17` commit `414a5d301ff17ca6e655330474c8346863d0d5d0`.

## Execution

Heavy is the only workflow route. Leaf-state questions and small bounded tasks
work directly from `AGENTS.md` without workers and without loading the Heavy
contract. Substantive work enters deployment state and loads `heavy_route.md`.

On the first deployment-state entry in a workflow session, Main immediately
bootstraps one persistent Companion before broad project discovery, planning, or
other worker dispatch. Its first assignment is built from the current goal and
already-known context only and stays bounded to directly relevant checkpoints,
documents, or project surfaces; it does not imply a full `agent_docs/` or
unrelated-module intake. Main may continue independent Heavy intake and
orchestration while Companion works and waits only when the Companion result
gates a decision. The same Companion is reused for later assignments and later
deployments in the session.

The Heavy contract contains the standing orchestration rules Main needs for the
whole deployment. Detailed worker-package, Micro Execution, follow-up, and
recovery instructions live in `delegation.md` and are loaded only when Main is
actually delegating, following up, routing Micro work, or recovering work.

Main controls scope, architecture, dependencies, scheduling, acceptance, and
final claims. In Heavy it is an orchestrator rather than a production executor:
implementation, broad repository/security analysis, testing, task-level
Git/GitHub operations, repair, and delegable research stay with the appropriate
workers by default.

A timeout-only `wait_agent` result with no new evidence is not itself an
intervention signal. If the worker remains presumed healthy, Main issues another
long wait instead of polling status. The normal wait is 25 minutes and returns
early if the worker completes sooner.

Routine orchestration and successful intermediate completions remain silent
unless the user needs a decision/risk update or explicitly asked for progress.
Heavy has no workflow-imposed aggregate active-subagent limit; the Codex platform
and account determine available concurrency.

| Role | Model / reasoning | Responsibility |
| --- | --- | --- |
| Micro Executor | Spark / high when available; otherwise Luna / high | Tiny deterministic implementation subtasks inside an existing Heavy deployment. |
| Default Executor | Luna / max | Normal bounded implementation and repair. |
| Senior Executor | Astra / low | Exceptionally difficult bounded production or solution work. |
| Tester | Luna / max | Independent verification. |
| Companion | Luna / max | Persistent read-only project context, created once at first deployment entry and reused. |
| Investigator | Luna / max | Disposable read-only investigation across bounded project evidence, Internet sources, or both. |
| Archivist | Luna / max | Verified documentation outside Main-owned deployment-state docs and closing handoff. |

Micro Executor is a separate workflow-owned worker below Default Executor. Its
installed profile is Luna High. When the runtime/account exposes
GPT-5.3-Codex-Spark and model overrides, Main may spawn the same Micro package
with Spark High. Spark availability is not part of correctness. A package that
stops being small and deterministic is reclassified directly to Default or
Senior Executor.

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
`delegation.md`, `archivist.md`, runtime modules, installed templates, and
ownership state. `operate/` contains lifecycle guides and version metadata;
`runtime/workflow.py` is the launcher. Worker definitions are installed under
`~/.codex/agents/`.

The workflow enables Codex multi-agent support but does not impose the retired
`max_concurrent_threads_per_session = 20` setting. Migration removes that old
workflow-owned key while preserving unrelated Codex configuration.

## Lifecycle and owner release channel

Installation and updates are explicit owner actions. Opening a project does not
install or update anything automatically.

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
documents, and enabled/disabled state are preserved. Updates are backed up and
applied transactionally.
