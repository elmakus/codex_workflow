# Intake — compaction runtime routing

Status: active
Workstream: `issue-compaction-runtime-routing`
Kind: `issue`
Branch: `fix/compaction-runtime-routing`

## Authorized scope

Diagnose and repair the observed worker-routing failure in `codex_workflow`: before context compaction Main correctly routed `muse-max` Tester/Executor roles through Muse, but after compaction it dispatched an internal Codex Tester and obtained GPT-5.6 Luna Max. The fix must remain token-light and must not narrow the diagnosis to workflow-version drift.

## Baseline evidence

- Intended baseline: current `main` at `8130efb340ea2c6308e33c96dbff2a53bc98fc49`.
- Current `muse-max` allocation on that baseline assigns all six supported roles to `muse-code` / Muse Spark 1.3 Contributor Max.
- `heavy_route.md` and `delegation.md` prohibit internal Codex worker APIs for those `muse-max` roles.
- The production incident rollout records a pre-compaction Muse-backed Tester and Executor, then a later post-compaction `spawn_agent(agent_type="tester", fork_context=false, ...)` returning `gpt-5.6-luna` / `max`.
- The same rollout then returned to `runtime/muse_worker.py` only after the user challenged the incorrect Luna Max dispatch.
- A workflow upgrade occurred during that long-lived session and is a secondary stale-contract factor, but the issue must be solved even when no workflow version changes.

## Dependency classification

The defect exists against current `main`: current profile authority still leaves internal Codex worker TOMLs available while `muse-max` routing relies on Main respecting the external-harness contract. No unmerged state from `feat/muse-main-orchestration-efficiency` is required to reproduce or define the problem.

Classification: independent workstream based on `main`.

## Intake questions still open

Determine the smallest fail-closed runtime boundary that prevents a forgotten/stale Main routing decision from successfully dispatching an internal Codex worker for a `muse-max` role, including after compaction, without imposing a heavy repeated context reload. Confirm whether this is a bounded micro-fix or requires Research/Planning.
