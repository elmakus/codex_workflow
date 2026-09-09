# Private 1.1.14-private.3 notes

> **Historical document — not the current workflow contract.**
>
> This file describes the old `1.1.14-private.3` line and is retained only as
> release history. The current package on `main` is `1.1.17-private.1`.
> Do not use the behavior below to reconstruct current policy.
>
> Important current differences include:
>
> - the workflow does **not** set `max_concurrent_threads_per_session`;
> - the workflow owns seven workers, including `micro_executor`;
> - Micro uses Luna High as its installed fallback and may use Spark High as an
>   optional spawn-time override when available;
> - Main directly maintains `project_progress.md`, `project_diary.md`, and
>   `latest_session_work.md` during deployment;
> - Investigator may use project evidence, Internet sources, or both;
> - silent orchestration is now strict: changed findings, hypotheses, plans,
>   Git state, checkpoints, and other intermediate progress are not narrated
>   while work can continue safely without user input;
> - detailed delegation/recovery policy is progressively disclosed through
>   `delegation.md`.
>
> See `docs/proposed_by_chatgpt_review_notes.md`, `codex_workflow/heavy_route.md`,
> `codex_workflow/delegation.md`, current worker TOMLs, and current tests for the
> active private contract.

Upstream base: experimental 1.1.14 commit
`a224f32c423ef56be322de160d5440bba0a786b2` (2026-09-05).
Previous private release line: `1.1.14-private.2`.

## Retained upstream behavior

- Batched independent work and on-demand Companion.
- Role-specific concise reports and main-owned acceptance decisions.
- Main owns the project diary; Archivist owns assigned documentation and handoff.
- Lifecycle guides and version metadata live under `operate/` and the launcher
  under `runtime/workflow.py`. Project documents remain under `agent_docs/`.
- Heavy has no workflow-imposed aggregate active-subagent limit; the main
  chooses worker count and concurrency for the task.
- Lifecycle migration uses ownership-aware replacement/removal, verified backup,
  and compensating transactions.

## Private behavior

The following bullets describe `1.1.14-private.3` historically; they are not
current requirements unless they are also present in the current runtime.

- Heavy is the only workflow route. Leaf-state questions and small bounded tasks
  work directly from `AGENTS.md` without subagents or reading `heavy_route.md`;
  that contract is loaded only for substantive deployment-state work.
- Documentation reads are proportional to the task rather than requiring a
  complete `agent_docs/` intake for every substantive deployment.
- Luna roles use `max` reasoning. Senior Executor uses Astra `low`.
- The workflow kept Codex multi-agent enabled with
  `max_concurrent_threads_per_session = 20` as the platform safety ceiling.
  **This fixed ceiling was later retired and is not part of the current
  `1.1.17-private.1` contract.**
- Heavy is orchestrator-first. A normal worker wait is 25 minutes and a timeout
  with no new evidence should lead to another long wait rather than status
  polling or takeover.
- Routine successful orchestration and intermediate completions were silent by
  default; the current release uses a stricter silent-orchestration contract.
- Archivist treats `agent_docs/` as durable cross-session project memory with
  canonical document ownership and cross-references instead of duplication.
- Token accounting, its skill and script, deployment markers, and report tables
  are removed.
- Owner-release discovery is restored only for `elmakus/codex_workflow`.
  `--check-update` is read-only; `--update` requires an owner release containing
  both the versioned ZIP and `SHA256SUMS`, verifies SHA-256, safely extracts it,
  and delegates to the incoming runtime. There is no upstream release channel,
  background auto-update, or automatic release publication.
- A verified explicit local `--source` path remains available for recovery and
  for the first migration from private.2, whose installed launcher predates the
  owner-release updater.
- Migration preserves unrelated content and supports bringing an older project
  wrapper up to the already-installed shared runtime version. Retired owned
  runtime files, including the former `medium_route.md`, are removed.

## Installation status

Building or publishing a release does not install it. Owner-requested migration
replaces the shared runtime once and migrates each intended project wrapper
explicitly. Project-local instructions, personalization and `agent_docs/` are
preserved.

## Verification evidence

For current installations, use validation evidence from the exact current
package being installed. Historical `1.1.14-private.3` evidence must not be
used as proof for `1.1.17-private.1` behavior.
