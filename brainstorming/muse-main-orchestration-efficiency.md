# Brainstorm — Muse Main orchestration efficiency

Date: `2026-09-20`
Scope ID: `muse-main-orchestration-efficiency`
Revision: `R1`
Status: `ready_for_definition`

## Problem / goal

The `muse-max` profile currently allows normal concise orchestration updates from Main. Live evidence proves that Main can also be re-entered repeatedly while one healthy Muse worker is still running, causing repeated large-context Sol Medium requests.

The feature goal is to eliminate periodic Main inference while waiting for healthy Muse work and make user-visible orchestration materially quieter without restoring the historical hard-silent mode.

## Current understanding

### Verified facts

- Current `heavy_route.md` still forbids routine polling for internal Codex workers and retains long event-driven `wait_agent` behavior.
- Current `muse-max` uses external Muse invocations through `runtime/muse_worker.py`; the adapter itself stays alive and synchronously waits for its Muse child.
- The dominant repeated Sol cost occurs **above** `muse_worker.py`: Main cycles through Code-Mode command-session `exec/write_stdin/wait` boundaries while the same Muse process remains healthy.
- In the observed healthy Executor interval, 24 repeated Sol Medium requests cost USD 1.934; cached input was 99.82%, and most requests performed almost no reasoning.
- Live Codex logs show 13 roughly 31-second `exec` waits interleaved with 12 roughly 25-second Code-Mode `wait` calls.
- A requested 60-second terminal yield still crossed the Code-Mode foreground boundary after roughly 31 seconds; increasing `yield_time_ms` alone is not sufficient.
- The initial interrupted-worker `session_busy` path caused legitimate recovery work but does not explain the continuing periodic requests during the healthy replacement worker.
- Current `muse-max` communication is normal concise milestone commentary. Historical `luna-xhigh` strict silent orchestration suppressed essentially all mid-task progress except blockers/risks/user-requested updates.
- Communication suppression alone cannot solve the cost issue; the wait transport must suppress Main sampling as well.

### Existing accepted decisions

No existing accepted requirement or decision authorizes this feature yet. Existing accepted behavior is the current `muse-max` orchestration/runtime model on `main`.

### Implementation-time facts still to prove

- First candidate: one long-lived Code Mode `exec` cell using the existing per-cell `// @exec: {"yield_time_ms": ...}` pragma, with shell-session waits performed internally inside that cell so Main is not re-entered.
- Live proof must confirm that this cell can remain pending for a realistic multi-minute Muse run and that cancellation still works safely.
- Only if that native path fails should the design add a dedicated managed tool/MCP/broker dependency.

These are implementation feasibility questions, not unresolved product choices.

## Ideas / alternatives considered

### Option A — communication-only reduction

Rejected as incomplete: it can reduce narration but leaves periodic Main sampling untouched.

### Option B — managed event-driven Muse boundary plus moderated quiet mode

Selected exploratory direction and now supported by Research.

One bounded Muse turn should remain runtime-owned until terminal/material completion without Main polling. User-visible communication becomes a quiet milestone mode rather than historical hard silence.

### Option C — restore historical strict silent orchestration

Rejected by explicit user preference. The desired communication policy is intentionally less strict.

## Trade-offs / questions

The key design constraint is the separation between **communication suppression** and **inference suppression**.

The feature should not trade away existing stateful Muse correctness: timeout/cancel cleanup, session binding, fail-closed resume/replacement, Executor/Tester independence and private raw artifacts remain protected.

## Research outcome

Completed Research: `research/muse-main-orchestration-efficiency.md` / `R-MUSE-MAIN-ORCH-01`, including the user-requested ecosystem scan. Upstream Codex, Claude Code and MCP evidence confirms this is a common long-running-tool orchestration problem rather than a Muse-specific anomaly.

Evidence supports these Definition candidates:

- no periodic Main/model sampling solely to observe a healthy running Muse worker;
- managed terminal/material-event wait boundary instead of Main-driven terminal/session polling;
- quiet milestone communication for `muse-max`: suppress routine operational narration but allow concise user-meaningful phase transitions;
- no timer-based Main wake-up solely to say work is still running;
- live acceptance using Codex-LB and Codex rollout evidence;
- preserve current Muse safety/session/review guarantees and leave `plus` unchanged.

## Open questions

No material user/product/strategic question blocks Project Definition.

The exact managed wait implementation remains to be proven in Planning/Execution Prep and must fail closed to a bounded dependency if the host cannot support the required event-driven boundary.

## Outcome of this session

- Tentative conclusions: proceed with the combined event-driven-wait + quiet-milestone feature.
- Explicit user/product choices to promote through Project Definition:
  - introduce both the long/blocking event-driven Muse boundary behavior and a quieter `muse-max` orchestration communication policy;
  - the communication policy is approximately halfway toward former strict silent in spirit: meaningful phase transitions stay visible, routine operational narration does not.
- Research still needed: none before Definition.
- Open questions: no user decision required before Definition.
- Next phase/action: `ready for definition`
- Definition promotion authorization: `user_authorized`
- Definition promotion subject: `muse-main-orchestration-efficiency@R1`

> Nothing in this file becomes accepted requirement/decision authority by itself. Project Definition owns promotion into canonical `requirements/` and `decisions/`. Explicit user promotion is still required.
