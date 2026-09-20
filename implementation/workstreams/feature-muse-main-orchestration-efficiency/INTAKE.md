# Intake — Muse Main orchestration efficiency

- Workstream ID: `feature-muse-main-orchestration-efficiency`
- Kind: `feature`
- Status: `active`
- Branch: `feat/muse-main-orchestration-efficiency`
- Integration target: `main`

## Authorized subject

Reduce unnecessary Main (Sol Medium) orchestration turns while preserving useful user-visible progress for the `muse-max` profile.

The authorized feature contains two coupled goals:

1. Ensure Muse worker execution behaves as a long/blocking, event-driven boundary from Main's perspective, avoiding routine status polling or repeated Main wake-ups while a healthy Muse invocation is still running.
2. Reintroduce a moderated form of silent orchestration for `muse-max`: materially quieter than the current normal concise updates, but intentionally less strict than the historical `luna-xhigh` strict-silent behavior (user direction: roughly halfway toward the former strict-silent mode).

## Pre-creation discovery and dependency classification

- Baseline: `main@8130efb340ea2c6308e33c96dbff2a53bc98fc49`.
- No matching branch, workstream or PR for this subject was found.
- The feature modifies current `muse-max` orchestration behavior that already exists on `main`; it does not require parent-only state from an unmerged workstream.

Classification: **independent**.

Selected base: `main@8130efb340ea2c6308e33c96dbff2a53bc98fc49`.

## Intake continuation

Feature discovery must materialize the canonical Brainstorming record before Intake can complete. Definition promotion remains pending unless separately and explicitly authorized for the exact Brainstorming revision.
