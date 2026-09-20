# Intake — compaction runtime routing

Status: complete
Workstream: `issue-compaction-runtime-routing`
Kind: `issue`
Branch: `fix/compaction-runtime-routing`

## Authorized scope

Diagnose and repair the observed worker-routing failure in `codex_workflow`: before context compaction Main correctly routed `muse-max` Tester/Executor roles through Muse, but after compaction it dispatched an internal Codex Tester and obtained GPT-5.6 Luna Max. The fix must remain token-light and must not narrow the diagnosis to workflow-version drift.

## Baseline and diagnostic evidence

- Baseline: current `main` at `8130efb340ea2c6308e33c96dbff2a53bc98fc49`.
- Accepted `REQ-013` requires every supported `muse-max` worker role to use the Muse process/session lifecycle with no internal Codex exception.
- Current `muse-max` allocation correctly maps all six supported roles to `muse-code`, and `heavy_route.md` / `delegation.md` prohibit internal Codex worker APIs for those roles.
- The production incident rollout records correct Muse-backed Tester/Executor dispatch before compaction, followed after compaction by `spawn_agent(agent_type="tester", fork_context=false, ...)`, which successfully created GPT-5.6 Luna / Max. The same session returned to `runtime/muse_worker.py` only after the user challenged that dispatch.
- Current `platform_settings.py` unconditionally enables Codex internal multi-agent tools, while `plan_compute_profile()` changes profile allocation/settings but does not change that tool surface. The six internal worker TOMLs therefore remain executable dormant fallbacks even under `muse-max`.
- Upstream Codex configuration defines `[agents].enabled` as the multi-agent enable gate. Current upstream regression coverage proves that `agents_enabled = false` with MultiAgentV2 disabled removes `spawn_agent`, `send_message`, `wait_agent`, `list_agents`, and both multi-agent namespaces from the model tool surface.
- Upstream also documents that enabled `features.multi_agent_v2` takes precedence over `agents.enabled`; `muse-max` must therefore fail closed rather than claim the guard is active if an external effective V2 override would re-expose internal agents.
- The always-injected workflow `AGENTS.md` currently does not carry a compact post-compaction dispatch invariant. The detailed harness rule lives in Heavy/delegation context, which can become stale or weak after compaction.
- A workflow upgrade occurred during the observed long-lived session and is a secondary stale-contract factor. The primary defect and this fix do not depend on any version change: the same failure is possible whenever Main forgets the harness rule after compaction while the internal tool surface remains available.

## Dependency classification

The defect is present on current `main` and requires no unmerged parent-only state. The active `feat/muse-main-orchestration-efficiency` workstream may touch neighboring orchestration documentation but is not required to reproduce or fix this issue.

Classification: independent workstream based on `main`.

## Micro-fix qualification

Path: `micro_fix`.

- Root cause and intended behavior are concrete: a documentation-only role→harness prohibition is not enforced at the Codex internal-agent surface, so post-compaction routing loss can successfully execute the forbidden path; `REQ-013` already defines the intended behavior.
- Change is bounded and low strategic risk: make Codex internal-agent availability profile-aware, add a tiny always-injected dispatch revalidation invariant, and cover profile switching/regressions.
- No accepted requirement, architecture, or product decision changes; this enforces existing `REQ-012`/`REQ-013` and DEC-002.
- Acceptance is directly measurable through rendered config/profile transitions, fail-closed V2 conflict behavior, contract tests, and existing Muse/runtime suites.
- No substantial migration or deployment strategy is required. Existing update/profile operations already own `config.toml` mutations and preserve unrelated user settings.

## Intended bounded correction

- Under `plus`, keep internal Codex multi-agent tools enabled as today.
- Under `muse-max`, set the workflow-owned `[agents].enabled = false` guard so a stale/forgotten Main route cannot successfully use `spawn_agent` for workflow roles, while preserving DEC-002's existing `[features].multi_agent = true` ownership.
- Under `plus`, set `[agents].enabled = true`; switching profiles must update that guard transactionally and idempotently.
- If an externally enabled MultiAgentV2 setting would override the guard, `muse-max` activation/update must fail closed with a clear validation error rather than leave an apparently protected but actually exposed surface.
- Put only the minimal dispatch invariant in always-injected `AGENTS.md`: resolve the single-line active profile immediately before each worker dispatch, never trust pre-compaction remembered routing, and treat internal Codex worker APIs as forbidden under `muse-max` even if a stale long-lived session still exposes them.
- Do not add a full workflow/document reload after compaction. Do not alter Muse session/process semantics.

Next route: `execution_prep:micro_fix`.
