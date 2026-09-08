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

The existing guidance around a normal `1800000` ms (30 minute) wait and sensible `300000`-`3600000` ms range is intentional.

Reason: Luna max can be slow; avoid wasteful polling turns while still continuing immediately when a child finishes early.

### 11. Token-reporting and online-update machinery stay removed

Do not restore the deployment token report, reporting skill, online release checks, automatic downloads, automatic publication, or similar machinery merely to match upstream.

The private package intentionally uses explicit verified local update sources and a simpler closure path.

### 12. Heavy Main is an orchestrator, not a production executor

This is an explicit owner decision motivated by Heavy cost economics.

For substantive Heavy work, Main should minimize direct task execution. Code implementation, broad repository analysis, security review, testing, repository migration, material Git/GitHub task operations, refactoring, repair, delegable research, and work already assigned to a worker should stay with specialized workers by default.

If assigned work stops progressing, the intended order is:

1. inspect the existing worker/thread status;
2. resume that worker when possible;
3. wait or message it when it is still running/waiting;
4. if it completed partially, reuse its result and delegate only the remainder;
5. reassign the remainder only when the original worker is irrecoverably unavailable.

A slow, stalled, or temporarily allowance-blocked worker is not sufficient reason for Main to take over its work. After allowance recovers, resuming the same worker/thread is preferred.

If the predecessor is irrecoverably unavailable and left no complete handoff, Main should not reconstruct its detailed work. Main should identify only available recovery sources such as predecessor thread ID, worktree, branch, handoff path, or existing commits and pass those references to the replacement worker. The replacement worker owns reading those sources, determining completed versus remaining work, and continuing from the first unfinished step. The intended flow is `resume predecessor -> if impossible, delegate recovery + continuation -> integrate`, not `resume impossible -> Main reconstructs -> delegate remainder`.

Direct Main task execution remains allowed only for genuinely trivial work that costs less than delegation, or operations needed solely for orchestration. That exception must not be stretched to cover implementation, security review, repository migrations, material Git/GitHub task operations, testing, or delegable research. "Take over to make progress" or "take over to go faster" is intentionally rejected as justification.

Main may perform targeted lightweight final inspection for a high-risk decision or final claim, but this must not become a second execution of the worker's substantive task.

For repetitive independent units such as many similar repository migrations, do not maximize concurrency mechanically. Prefer bounded batches or sequential execution when that reduces duplicated context and Main coordination cost. This is a preference, not a global one-repo-at-a-time rule and not a new aggregate subagent cap.

Reason: the more expensive Main model should spend context and reasoning on planning, coordination, integration, acceptance, and user communication rather than duplicating work that a cheaper specialized worker can perform.

### 13. Heavy orchestration is silent by default

Routine orchestration should happen through tool calls without a user-visible narration after every wait, resume, thread/status check, worker message, queue decision, result reuse, or routine transition. Silence is about output economy only; Main still performs all reasoning, monitoring, lifecycle operations, acceptance verification, and problem handling required for correctness.

Successful intermediate completions are also silent by default. If individual stages or repositories complete successfully while more work remains and everything is proceeding as expected, Main should not report each completion; defer those results to the final response. During execution, user-visible status is reserved for a blocker requiring the user's decision, a security/publication risk, a material scope/plan change, or progress updates explicitly requested by the user. Whole-task completion still receives the normal final response.

Reason: repeated prose about internal orchestration or routine successful milestones consumes output/context tokens from the more expensive Main without improving execution or helping the user make a decision.

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
- any Heavy wording that still encourages Main to perform executor/researcher/tester work directly;
- any path where a stalled worker is treated as permission for Main takeover before resume/wait/message/reassignment is exhausted;
- any path where an unavailable predecessor without a complete handoff causes Main to read/reconstruct detailed predecessor state instead of delegating recovery + continuation;
- any wording that encourages narration after routine wait/resume/status/message/queue operations or routine successful intermediate completions instead of silent tool-call orchestration;
- final-verification wording broad enough to make Main redo the substantive task;
- concurrency wording that accidentally creates either a new hard global cap or a blanket one-item-at-a-time rule;
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
