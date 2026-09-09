# Current private workflow design notes

This file records the current owner-approved behavior of `elmakus/codex_workflow` after the `proposed-by-chatgpt` candidate was merged into `main`.

The canonical implementation is `main`. The current package version is `1.1.17-private.1`. These notes are guidance for future review; source code, tests, and the current runtime contracts remain authoritative.

## Core workflow

- Heavy is the only substantive orchestration route.
- Small, bounded leaf work stays direct and does not enter Heavy merely because multi-agent is enabled.
- `medium_route.md` is intentionally retired.
- Documentation reads are proportional to the task rather than loading the complete `agent_docs/` set on every deployment entry.
- Heavy is orchestrator-first: Main owns direction, architecture, integration, acceptance, and final claims while delegable implementation, testing, research, migration, repair, and similar production work normally stay with workers.
- Main's model is not pinned by this workflow. Main is whichever model the user selects in the Codex GUI/session.

## Progressive disclosure

`heavy_route.md` contains the standing Heavy contract. Detailed worker-package, Micro routing, follow-up, repair, and recovery rules live in `delegation.md` and should be loaded only when those details are actually needed.

Do not move all delegation detail back into Heavy and do not split it into unnecessary additional layers.

## Workers

The workflow owns seven workers:

1. `micro_executor`
2. `default_executor`
3. `senior_executor`
4. `tester`
5. `archivist`
6. `companion`
7. `investigator`

Current worker model policy:

- Micro Executor: `gpt-5.6-luna`, high reasoning as the installed fallback profile.
- Default Executor: `gpt-5.6-luna`, max.
- Senior Executor: `gpt-6-astra`, low.
- Tester: `gpt-5.6-luna`, max.
- Archivist: `gpt-5.6-luna`, max.
- Companion: `gpt-5.6-luna`, max.
- Investigator: `gpt-5.6-luna`, max.

For a genuine tiny deterministic subtask, Main may spawn the `micro_executor` role with a runtime model override to `gpt-5.3-codex-spark` at high reasoning when Spark is exposed and accepted. Spark is optional. If it is unavailable, the same role falls back to its installed Luna High profile.

If a Micro task grows into exploration, architecture, security judgement, migration reasoning, broader ownership, or substantially harder reasoning, reclassify it directly to Default Executor or Senior Executor rather than building a Micro reasoning ladder.

Investigator may collect bounded evidence from the project, the Internet, or both. Main retains causal, architectural, solution, and acceptance decisions.

## Concurrency

Heavy does not impose an aggregate active-subagent limit. Main chooses useful concurrency according to dependencies and ownership, while the Codex platform determines the slots actually available.

The workflow intentionally does **not** set `max_concurrent_threads_per_session`. Old workflow-owned fixed-concurrency keys are retired during settings patching/migration. Multi-agent remains enabled.

Do not restore a fixed value of 20 merely because older private notes or tests mention it.

## Wait and recovery behavior

Prefer `delegate -> resume -> wait -> integrate`.

When workers are running and no useful independent work remains, use one appropriately long event-driven `wait_agent` call. The normal Heavy wait is `1500000` ms (25 minutes), within the permitted `300000`-`3600000` ms range.

A timeout with no new evidence is not itself a reason to poll, list threads, message, interrupt, replace, inspect progress, or let Main take over. If the worker is still presumed healthy, wait again.

For an irrecoverably unavailable worker, pass the available recovery sources to a replacement worker and let that worker determine completed versus remaining work. Main should not reconstruct the predecessor's detailed work itself.

## Silent orchestration

During execution, Main must not send user-visible progress/status narration, intermediate findings, hypotheses, evidence summaries, routing decisions, worker-state updates, Git/branch-state updates, checkpoints, or next-step descriptions.

Do not narrate an "important discovery", changed hypothesis, changed plan, successful intermediate result, newly discovered evidence, or repository state. Incorporate it internally and continue.

A mid-task user-visible message is allowed only when:

- work cannot continue without a user decision or missing information;
- an immediate security, publication, destructive-action, or authorization risk requires explicit approval; or
- the user explicitly requested progress updates for that task.

If work can continue safely without user input, remain silent. Whole-task completion still gets one normal final response.

Tool/activity rows shown by the Codex UI are not controlled by this prose contract; the rule concerns user-visible narration emitted by Main.

## Documentation ownership

During a substantive deployment Main directly maintains:

- `agent_docs/project_progress.md`
- `agent_docs/project_diary.md`
- `agent_docs/latest_session_work.md`

Archivist must not modify those three during deployment. Archivist owns the remaining verified durable documentation and closing handoff within its assigned scope.

`agent_docs/` remains durable cross-session project memory. Preserve unrelated content and avoid duplicating stable facts across documents.

## Updater and release channel

Release discovery is owner-controlled and may use only GitHub Releases from:

`elmakus/codex_workflow`

Preserve the hardened updater behavior, including trusted URL/path validation, bounded metadata/download/archive sizes, SHA-256 verification, safe ZIP extraction, strict checksum parsing, transactional update/rollback, ownership-aware cleanup, and preservation of unrelated user state.

A verified explicit local `--source` update path remains supported. There is no background/startup auto-update and no automatic GitHub Release publication.

Token-reporting machinery remains intentionally removed.

## Review checklist

A future reviewer should challenge implementation quality, but should not mistake the choices above for accidental drift. In particular verify:

- Heavy-only plus direct leaf behavior remains coherent;
- `delegation.md` is progressively disclosed rather than always loaded;
- all seven workers are package-owned and lifecycle-safe;
- Spark is optional and Luna High fallback works;
- no fixed concurrency key is reintroduced;
- silent orchestration has no "material plan/scope change" narration loophole;
- Main-owned deployment documents remain outside Archivist's write scope;
- owner-only update/release security is preserved;
- package validation, lifecycle, migration, rollback, and release-security regression coverage remains intact.
