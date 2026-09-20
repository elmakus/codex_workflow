# Research — Muse Main orchestration wake-up and communication behavior

Date: `2026-09-20`
Research question: `Which current codex_workflow/Main/Muse paths cause repeated Sol Main turns during Muse execution or recovery, and what minimal workflow/runtime changes can make healthy Muse execution a single long/blocking event-driven boundary while reducing routine user-visible orchestration updates to a moderated level without restoring historical strict-silent behavior?`

## Durable continuation metadata — policy-activated only

Research ID: `R-MUSE-MAIN-ORCH-01`
Status: `consumed`
Origin role: `brainstorming`
Origin subject: `muse-main-orchestration-efficiency@R1`
Return target: `brainstorming:muse-main-orchestration-efficiency@R1`
Return reconciliation: `applied`
Return reconciliation result: `brainstorming/muse-main-orchestration-efficiency.md — muse-main-orchestration-efficiency@R1 ready_for_definition`

## Scope

Inspect current `elmakus/codex_workflow` main and the live workstation path that invokes Muse. Compare the current `muse-max` communication policy with the historical strict-silent policy. Separate:

- user-visible communication cadence;
- Main sampling/tool-turn cadence;
- healthy Muse invocation lifecycle;
- timeout/cancellation/recovery/reconciliation behavior.

The purpose of this Research is evidence and implementation-boundary discovery only. It does not authorize production changes.

## Sources / evidence

Repository evidence:

- `codex_workflow/runtime/muse_worker.py` on current main.
- `codex_workflow/runtime/muse_sessions.py` on current main.
- `codex_workflow/runtime/compute_profiles.py` on current main.
- `codex_workflow/heavy_route.md` and `codex_workflow/delegation.md` on current main.
- `scripts/test_muse_adapter.py` and `scripts/test_muse_profile.py` on current main.
- historical `codex_workflow/runtime/compute_profiles.py` at `a64b41632d708f456d80e7543de1110b82da1c00`, which still contains the former `luna-xhigh` strict-silent policy.
- accepted workstation Muse-runtime authority/evidence in `elmakus/chatgpt-ce-workstation`: `requirements/MUSE_MAX_RUNTIME.md`, M10 stateful-runtime evidence and M10 live interruption/recovery evidence.

Live evidence from the running workstation:

- active `muse_worker.py` and Muse child-process readback during a real long-running Tester invocation;
- private Muse run/session artifacts for the observed Default Executor sequence;
- Codex core/app-server logs in `~/.codex/logs_2.sqlite`;
- the exact Codex rollout for the observed Main turn;
- Codex-LB `request_logs` for the same interval.

No secret values or raw Muse trajectories are copied into this record.

## Verified findings

### F1 — The dominant cost is real repeated Main sampling, not merely visible commentary

During one healthy replacement Default Executor Muse invocation, the worker remained active for roughly fourteen minutes and completed successfully.

Inside the worker-active interval, Codex-LB recorded **24 additional GPT-5.6 Sol Medium requests** between the dispatch-side setup and terminal processing:

- aggregate cost: **USD 1.934**;
- average cost per request: **USD 0.0806**;
- input size: about **193.5k–197.1k tokens**;
- aggregate cached-input ratio: **99.82%**;
- **19/24** requests used at most 6 reasoning tokens;
- **18/24** emitted only 31 or 67 output tokens.

Including the dispatch/terminal edges, the observed window was 26 Main requests and **USD 2.099**.

This is therefore not primarily a reasoning-cost problem. It is a high-frequency Main re-entry problem with a very large cached context.

### F2 — `muse_worker.py` itself already waits synchronously for Muse

Current `muse_worker.py` launches Muse through `subprocess.Popen`, drains stdout/stderr privately, keeps an outer timeout (30 minutes by default), and stays alive until terminal completion, timeout, cancellation or failure.

Its internal `process.poll()` loop runs inside the Python adapter process. That loop does **not** invoke Sol and is not the source of the repeated Codex-LB requests.

Live process readback confirmed the adapter and its Muse child remain continuously alive while the worker is running.

### F3 — The repeated Main wake-ups occur in the Codex command/tool waiting path above the adapter

The exact live Codex turn shows the real pattern.

Main launched the adapter with a Code-Mode `exec` call containing `tools.exec_command(... yield_time_ms: 30000)`. When the command remained active, Main repeatedly used `tools.write_stdin(... yield_time_ms: 60000)` through another `exec` call.

Despite the requested 60-second yield, the Code-Mode script returned after roughly 31 seconds as an asynchronous cell. Main then issued a separate `wait` call for that cell; after that completed, Main sampled again and started another `write_stdin` cycle.

For the healthy worker interval, Codex logs contain:

- **13** `exec` calls, average handler duration about **30.9 s**;
- **12** `wait` calls, average handler duration about **25.1 s**.

The sequence is effectively:

```text
Main sample
  -> write_stdin / wait for worker terminal
  -> ~31 s foreground boundary
Main sample
  -> wait for async Code-Mode cell
  -> ~25 s
Main sample
  -> next write_stdin
  -> ...
```

Every boundary re-enters Sol with the full conversation context. The same top-level user turn and same Codex conversation remain active throughout.

### F4 — Increasing Muse timeout or `yield_time_ms` alone does not solve the problem

The adapter already allows a long outer timeout. The observed repeated sampling happened while the Muse process was healthy and continuously running.

The live rollout also proves that requesting `yield_time_ms: 60000` on `write_stdin` did not create a 60-second model-free wait: the Code-Mode foreground execution surfaced an asynchronous cell after about 31 seconds and required a later `wait`.

Therefore the fix cannot be only:

- a larger `muse_worker.py` timeout;
- a larger terminal yield value;
- a prompt saying "wait longer";
- or suppressed user-visible text.

### F5 — The initial `session_busy` recovery event is real but is not the dominant recurring cause

The first interrupted Executor identity failed closed with `failure_kind=session_busy` and explicit reconciliation was required. That recovery path created legitimate extra Main work.

However, after Main created a clean explicit replacement Executor, the replacement ran normally and still produced the periodic Sol request pattern for its entire healthy execution.

Recovery efficiency is worth preserving, but fixing recovery alone would not remove the periodic cost.

### F6 — Current no-polling semantics are stronger for internal Codex workers than for external Muse waiting

`heavy_route.md` still contains the intended long event-driven `wait_agent` behavior for internal Codex workers: no routine status polling, a long wait, and another long wait after an empty timeout.

Muse-backed roles do not use `wait_agent`. They are external processes reached through `muse_worker.py`, and current documentation does not provide an equivalent Main-facing event-driven wait primitive that survives the Code-Mode foreground boundary without another model sample.

The policy intent survived, but the Muse transport does not currently realize the same cost behavior.

### F7 — Communication suppression and inference suppression are separate controls

Current `muse-max` renders normal concise commentary with relevant progress updates at meaningful milestones.

Historical `luna-xhigh` strict silent orchestration prohibited essentially every mid-task progress/status/intermediate update except a blocking user decision, immediate risk/authorization need, an explicit progress request, or the final response.

Changing only the communication text can remove some low-value narration, but it cannot eliminate the observed `exec -> wait -> exec` sampling loop. The worker-wait transport must be corrected independently.

## Repository/current-state findings

### Runtime ownership

Existing accepted workstation authority says:

- `chatgpt-ce-workstation` owns Muse installation, PATH, login/auth persistence and workstation availability;
- `codex_workflow` owns the Muse worker lifecycle/orchestration semantics;
- workstation code is not the Muse worker scheduler.

That boundary should remain intact. The cost fix belongs primarily in `codex_workflow`, with a cross-repository dependency only if the Codex host cannot expose a sufficiently long event-driven tool boundary.

### Current implementation surfaces likely affected

At minimum the feature is expected to touch or verify:

- `codex_workflow/runtime/muse_worker.py` or a tightly related managed Muse await/broker surface;
- `codex_workflow/heavy_route.md`;
- `codex_workflow/delegation.md`;
- `codex_workflow/runtime/compute_profiles.py`;
- `scripts/test_muse_adapter.py`;
- `scripts/test_muse_profile.py`;
- README/runtime documentation.

The exact source split remains a Planning/Execution-Prep decision after a live feasibility gate for the Main-facing wait mechanism.

## Alternatives

### A — Communication-only quieting

Change `muse-max` text to emit fewer progress messages.

Result: useful as the second half of the feature, but **insufficient** for cost control because hidden Main samples remain.

### B — Larger terminal yields / more aggressive "do not poll" prompting

Keep the current terminal-session topology and request larger waits.

Result: **insufficient as the primary solution**. Live evidence shows a requested 60-second `write_stdin` wait still crossed the Code-Mode foreground boundary at about 31 seconds and required another model-mediated `wait`.

A no-polling instruction should still exist as a safety rule, but it cannot be the only mechanism.

### C — Managed terminal-completion boundary for Muse

Provide a `codex_workflow`-owned Main-facing invocation/await surface in which one healthy Muse turn remains pending without periodic Main sampling and returns only on:

- terminal completion;
- terminal failure;
- timeout/cancellation;
- or another genuinely material runtime event requiring Main.

The underlying implementation may be a dedicated managed tool/broker or another host-supported event-driven primitive. It must not be an unmanaged shell `&` job plus Main polling.

Result: **preferred architecture**, subject to a live feasibility proof of the exact Codex-host integration.

### D — Restore historical strict silent orchestration unchanged

Result: would reduce narration but is intentionally rejected by the user's product choice. It is also not a substitute for the runtime fix.

## Analysis

The feature needs two independent but coordinated controls.

### 1. Event-driven Muse waiting

The semantic contract should be:

```text
Main decides and dispatches one bounded Muse turn
  -> Main does not sample merely because the worker is still healthy/running
  -> runtime owns waiting
  -> terminal/material event wakes Main
  -> Main performs the next orchestration decision
```

A healthy worker must not cause status reads, session listings, `write_stdin` heartbeats, Code-Mode-cell waits, or equivalent Main-visible polling loops.

If the existing Codex command surface cannot keep one tool call pending for the required duration, implementation must add/use a **managed event-driven await surface** rather than emulate waiting with repeated Sol turns.

### 2. Moderated quiet orchestration

"About halfway toward the old strict-silent mode" should be encoded semantically, not as a numeric message quota.

Proposed behavior:

- suppress routine worker-start messages, waiting narration, session/recovery bookkeeping, Git bookkeeping, "still working" updates, hypotheses and low-value intermediate findings;
- allow one concise update at a **user-meaningful phase boundary**, for example implementation completed and independent verification begins, or a RED review enters a real repair loop;
- always surface a blocker requiring user input, an immediate risk/authorization decision, or a material scope/architecture change;
- preserve the normal final result;
- do not create a model turn solely to send a timer-based progress message.

This is materially quieter than current `muse-max`, but unlike historical strict silent it still lets the user see important phase transitions during long substantive work.

## Measurable acceptance candidates

A future Definition/Plan should make the cost property directly testable.

For a healthy Muse invocation lasting at least several minutes:

1. after the Main request that dispatches the worker, **no additional Main sampling request occurs while the worker is merely still running**;
2. the terminal worker result may cause one normal Main continuation;
3. Codex rollout evidence contains no periodic Muse-status `write_stdin` / Code-Mode `wait` loop driven by Main;
4. Codex-LB request count remains flat throughout the healthy wait interval, excluding explicit user input or a genuinely material runtime event;
5. the Muse adapter process remains alive and the same worker completes normally;
6. timeout/cancellation/session-busy/fail-closed recovery semantics from the accepted stateful runtime remain intact;
7. current Executor/Tester logical-session independence and resume behavior remain intact;
8. communication tests prove routine operational narration is suppressed while meaningful phase-boundary, blocker/risk and final communication remain available;
9. `plus` behavior remains unchanged.

Absolute USD cost should not be an acceptance threshold because pricing and context size can change. The invariant is **no periodic Main inference during a healthy worker wait**.

## Assumptions / uncertainties

- The live evidence proves the current Code-Mode terminal path creates the periodic Main sampling loop. It does not yet prove which exact alternative host primitive is the smallest reliable replacement.
- A dedicated long-lived tool/MCP/broker call is the leading implementation direction, but its maximum pending-call behavior must be proven live before the plan freezes a concrete mechanism.
- If the Codex host imposes an unavoidable short pending-tool boundary on all available extension surfaces, the feature may require a narrowly scoped dependency outside `codex_workflow`. That is an implementation feasibility gate, not evidence that periodic Main polling is desirable.
- No evidence currently requires changing the accepted Muse logical-session registry, worker identity model, raw-artifact isolation, or process-tree cleanup semantics.

## Recommendation

Proceed with a single feature containing two milestones/surfaces:

1. **Main-wait efficiency:** introduce and live-prove a managed event-driven Muse completion boundary that eliminates periodic Sol sampling while a healthy Muse turn is active.
2. **Quiet milestone communication:** replace current `muse-max` normal-concise commentary with a moderated quiet policy that suppresses operational chatter but retains meaningful phase-boundary updates, blockers/risks and final results.

Treat communication-only changes as incomplete unless the Main-sampling acceptance gate is also GREEN.

## Project Definition candidates

The following are evidence-backed candidates for promotion, not yet accepted authority:

- `muse-max` MUST NOT cause periodic Main/model sampling solely to observe a healthy running Muse worker.
- A Muse turn MUST expose a managed terminal/material-event wait boundary to Main; repeated terminal/session polling is not an acceptable steady-state orchestration mechanism.
- Existing Muse timeout/cancel, session binding, fail-closed resume/replacement, Executor/Tester independence and artifact-isolation guarantees MUST remain intact.
- `muse-max` SHOULD use a quiet milestone communication policy: no routine operational narration, but concise user-meaningful phase transitions remain allowed.
- No timer-based progress update may justify waking Main solely to emit status.
- Acceptance MUST include live Codex-LB + Codex-rollout evidence demonstrating no periodic Main inference during a multi-minute healthy Muse invocation.
- `plus` semantics remain unchanged.
