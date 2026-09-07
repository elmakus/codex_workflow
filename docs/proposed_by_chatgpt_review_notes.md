# Review Notes for `proposed-by-chatgpt`

This document records the intent behind the changes on the `proposed-by-chatgpt` branch. It is meant for a later independent Codex review so that deliberate user-approved differences are not mistaken for accidental drift from upstream.

## Review objective

Review this branch for implementation errors, regressions, stale references, migration problems, contradictory instructions, or unnecessary complexity. Do not treat the design choices listed below as bugs merely because they differ from upstream. They were explicitly chosen by the repository owner.

The desired outcome is a simpler private workflow with one substantive orchestration mode, minimal context overhead for small tasks, selective subagent use, and preserved runtime safety limits.

## User-approved design decisions

### 1. Heavy is the only substantive workflow route

The previous Light / Medium / Heavy route selection is intentionally removed.

- `medium_route.md` should not exist in the current package.
- There should be no user-facing route-selection logic.
- Substantive work enters `deployment state` and uses `heavy_route.md`.
- Heavy is not intended to mean "spawn many agents by default". It is the single orchestration contract from which the main agent decides which capabilities are actually useful.

Reason: three routes duplicated policy and forced an unnecessary route-selection decision. The owner preferred one adaptive orchestration model.

### 2. Small tasks must remain cheap and direct

Questions, small edits, and other bounded work use `leaf state` and should be handled directly by the main agent.

For leaf work, the intended behavior is:

- do not spawn subagents merely because multi-agent is enabled;
- do not require Archivist closure;
- do not require reading `heavy_route.md` just to answer a small question;
- read project documentation only when needed for the task.

Reason: reduce unnecessary context consumption, agent turns, documentation reads, and process overhead.

### 3. Heavy has no separate instruction-level aggregate worker cap

The sentence limiting Heavy itself to "at most 20 active subagents" was intentionally removed.

The main agent should choose concurrency according to the work, dependencies, ownership boundaries, and usefulness of parallelism.

This does **not** mean unlimited Codex runtime concurrency.

### 4. The Codex runtime ceiling remains exactly 20

This is an explicit owner decision and must be preserved:

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 20

[features]
multi_agent = true
```

`MAX_CONCURRENT_WORKERS = 20` in `runtime/platform_settings.py` is intentional.

Reason: remove a redundant policy-level Heavy cap while retaining a real platform safety ceiling. A later reviewer should not "align with upstream" by deleting this runtime limit.

### 5. Multi-agent remains enabled

The workflow must continue to set `multi_agent = true`.

Reason: Heavy needs access to Companion, Investigator, Executors, Tester, and Archivist when those roles improve the result. The simplification is about choosing agents adaptively, not disabling multi-agent capability.

### 6. Senior Executor intentionally uses Astra Light

Senior Executor is intentionally configured as:

- model: `gpt-6-astra`
- reasoning effort: `low`

It remains reserved for an exceptionally difficult bounded implementation/reasoning package rather than routine work.

This is an explicit private customization; do not revert it to the previous Sol configuration solely because upstream differs.

### 7. Proportionate documentation reading is intentional

The private workflow deliberately keeps proportionate documentation reads instead of requiring the complete `agent_docs/` framework to be read on every deployment entry.

Expected behavior:

- start from the specified checkpoint when continuing work;
- search/read only documents or sections needed to understand the task, constraints, and dependencies;
- expand the read when context is missing;
- read the complete framework only when the scope actually requires it;
- a missing unrelated document must not block work.

Reason: preserve continuity without paying the token/context cost of full-document ingestion for every task.

### 8. `agent_docs/` remains durable canonical memory

The new Archivist guidance imported from upstream is intentional and should remain:

- `agent_docs/` is durable cross-session project memory, not a scratch area;
- each stable fact should have one canonical home;
- cross-reference rather than duplicate stable information;
- preserve unrelated existing documentation;
- maintain the roles of overview, core tech, structure, progress, diary, latest-session, and module-specific docs.

This rule complements, rather than replaces, proportionate reading.

### 9. Existing worker-role boundaries remain useful

Keep all six worker definitions available:

- Companion
- Investigator
- Default Executor
- Senior Executor
- Tester
- Archivist

The main agent should omit roles that add no value. Companion remains at most one persistent instance, Senior at most one, and one Archivist owns closure for a substantive deployment.

### 10. Existing long-wait behavior should remain

When workers are already running and no useful independent work remains, the main agent should prefer one appropriately long event-driven `wait_agent` call over repeated short polling.

The existing guidance around a normal `1200000` ms wait and sensible `300000`-`3600000` ms range is intentional.

Reason: avoid wasteful polling turns while still continuing immediately when a child finishes early.

### 11. Token-reporting and online-update machinery stay removed

Do not restore the deployment token report, reporting skill, online release checks, automatic downloads, automatic publication, or similar machinery merely to match upstream.

The private package intentionally uses explicit verified local update sources and a simpler closure path.

## Migration expectations

A review should specifically verify that upgrading an existing installation to this branch behaves safely:

- the retired `medium_route.md` is removed from the installed workflow runtime when it was previously workflow-owned;
- unrelated user files/settings are preserved;
- worker ownership cleanup remains safe;
- the runtime still writes `multi_agent = true` and `max_concurrent_threads_per_session = 20`;
- project-local instructions and durable `agent_docs/` content are preserved;
- existing rollback / backup behavior remains intact.

## What the reviewer should challenge

The reviewer should freely challenge implementation quality. In particular, check for:

- stale references to Light or Medium in active runtime/instruction surfaces;
- contradictory state or workflow instructions;
- accidental need to read Heavy for leaf tasks;
- broken package validation after deleting `medium_route.md`;
- broken update cleanup for old installed copies of `medium_route.md`;
- incorrect Senior model assertions or worker validation;
- tests that were weakened instead of updated to the new contract;
- unnecessary new abstraction, duplication, or indirection introduced only to make tests pass;
- any case where the runtime ceiling of 20 was accidentally removed or duplicated as a second Heavy policy limit.

If a cleaner implementation achieves the same approved behavior with less code or less indirection, propose it.

## Verification status at the time this note was added

The branch was prepared as a review candidate. The full regression command should be run by the reviewer before approval:

```sh
python3 -B scripts/test_workflow_runtime.py -v
```

Also run package validation:

```sh
python3 -B codex_workflow/runtime/workflow.py validate --package-root codex_workflow --json
```

Do not approve the branch solely because these design notes say the changes are intentional; intentional design still needs independent implementation verification.
