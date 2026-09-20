# Brainstorm — Muse Main orchestration efficiency

Date: `2026-09-20`
Scope ID: `muse-main-orchestration-efficiency`
Revision: `R1`
Status: `tentative`

## Problem / goal

The `muse-max` profile currently allows normal concise orchestration updates from Main. In observed live use, Main (Sol Medium) can be re-entered repeatedly while Muse work/recovery is in progress, with large mostly-cached contexts and non-trivial per-turn cost.

The feature goal is to reduce unnecessary Main turns without making the UI as silent as the historical strict `luna-xhigh` mode.

## Current understanding

### Verified facts

- Current `heavy_route.md` still forbids routine polling for internal Codex workers and retains long event-driven `wait_agent` behavior.
- Current `muse-max` uses external bounded Muse invocations through `runtime/muse_worker.py`, with logical-session resume and adapter-owned timeout/cancellation.
- Current `muse-max` communication policy is normal concise milestone updates, not historical strict silent orchestration.
- Live Codex LB evidence supplied by the user shows repeated Main requests with roughly 175–196k input tokens, almost entirely cached, and around USD 0.08–0.12 per request during active orchestration/recovery.

### Existing accepted decisions

No existing accepted requirement or decision authorizes this feature yet. Existing accepted behavior is the current `muse-max` orchestration model on `main`.

### Assumptions to verify

- Whether repeated Sol turns come primarily from user-visible progress/update policy, from tool/invocation boundaries, from recovery/reconciliation paths, or a combination.
- Whether a healthy long-running Muse invocation can remain one blocking tool/process boundary from Main's perspective in the current workstation/runtime.
- Which exact progress events can be suppressed without hiding meaningful milestones or blockers.

## Ideas / alternatives considered

### Option A — communication-only reduction

Reduce Main's user-visible update cadence but leave runtime/tool lifecycle unchanged.

Trade-off: low implementation risk, but may not reduce Codex LB requests if hidden Main turns still occur.

### Option B — blocking/event-driven Muse boundary plus moderated quiet mode

Keep each healthy Muse invocation as one long/blocking boundary from Main's perspective, forbid routine status/recovery checks without a terminal/material signal, and reduce routine user-visible orchestration updates substantially while retaining meaningful milestones.

This is the currently preferred direction.

### Option C — restore historical strict silent orchestration

Reapply the old `luna-xhigh` strict-silent policy.

Rejected by user preference: desired behavior is intentionally less strict, approximately halfway between current `muse-max` concise updates and the historical strict-silent mode.

## Trade-offs / questions

The key design constraint is to distinguish **communication suppression** from **inference suppression**. Hiding text is insufficient if Main is still re-entered for status checks.

## Research needed

Research must establish:
1. the exact current Main/Muse execution and recovery paths that can produce repeated Main turns;
2. whether those turns are required by runtime/tool semantics or are workflow-induced;
3. the minimal contract/runtime changes needed for a healthy Muse call to remain a single long/blocking event-driven boundary;
4. a concrete moderated communication policy that is materially quieter than current `muse-max` but not as strict as historical silent orchestration;
5. regression/acceptance signals that prove both reduced wake-ups and preserved blocker/milestone visibility.

## Open questions

No unresolved user/product decision currently blocks Research. Exact implementation boundaries are evidence questions for Research.

## Outcome of this session

- Tentative conclusions: pursue Option B.
- Explicit user/product choices to promote through Project Definition:
  - introduce both the long/blocking event-driven Muse boundary behavior and a quieter `muse-max` orchestration communication policy;
  - the communication policy should be roughly halfway toward the former strict-silent behavior, not a full restoration.
- Research still needed: exact wake-up causes, runtime/workflow ownership boundary, and measurable acceptance.
- Open questions: none requiring user input before Research.
- Next phase/action: `research`
- Definition promotion authorization: `pending`
- Definition promotion subject: `none`

> Nothing in this file becomes accepted requirement/decision authority by itself. Project Definition owns promotion into canonical `requirements/` and `decisions/`.
