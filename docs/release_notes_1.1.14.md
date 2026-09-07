# Private 1.1.14-private.2 notes

Upstream base: experimental 1.1.14 commit
`a224f32c423ef56be322de160d5440bba0a786b2` (2026-09-05).
Previous private base: `898ee86a4b8fb80f4dbfe8780d2ea017db202d37`
(1.1.13-private.2).

## Retained upstream behavior

- Batched independent work and on-demand Companion.
- Role-specific concise reports and main-owned acceptance decisions.
- Archivist replaces Doc-writer and Closure Steward.
- Main owns the project diary; Archivist owns assigned documentation and handoff.
- Lifecycle guides and version metadata live under `operate/` and the launcher
  under `runtime/workflow.py`. Project documents remain under `agent_docs/`.
- Heavy has no workflow-imposed aggregate active-subagent limit; the main
  chooses worker count and concurrency for the task.

## Private behavior

- Heavy is the only workflow route. Leaf-state questions and small bounded tasks
  work directly from `AGENTS.md` without subagents or reading `heavy_route.md`;
  that contract is loaded only for substantive deployment-state work.
- Documentation reads are proportional to the task rather than requiring a
  complete `agent_docs/` intake for every substantive deployment.
- Luna roles use `max` reasoning. Senior Executor uses Astra `low`.
- The workflow keeps Codex multi-agent enabled with
  `max_concurrent_threads_per_session = 20` as the platform safety ceiling.
- Archivist treats `agent_docs/` as durable cross-session project memory with
  canonical document ownership and cross-references instead of duplication.
- Token accounting, its skill and script, deployment markers, and report tables
  are removed.
- No release checks, downloads, automatic updates, or automatic publication.
  Manual migration uses an explicit verified local package.
- Installation is only on request. Opening a new project does not install or
  update the workflow automatically.
- Migration preserves unrelated content and supports bringing an older project
  wrapper up to the already-installed shared runtime version. Retired owned
  runtime files, including the former `medium_route.md`, are removed during an
  explicit migration.

## Installation status

Source preparation does not install into projects or replace the shared user
runtime. Owner-requested migrations use the incoming launcher. A coordinated
rollout replaces the shared runtime once and migrates each intended project
wrapper explicitly. Project-local instructions and `agent_docs/` are preserved.

## Verification evidence

Use the reviewed private source commit and its completed regression/package
validation for the exact behavior being installed. Upstream validation results
are not evidence for this modified private package.
