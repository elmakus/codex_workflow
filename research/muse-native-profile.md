# Research — Muse native Codex worker feasibility

Date: `2026-09-21`

Research ID: `R-MUSE-NATIVE-01`
Status: `complete`
Origin role: `brainstorming`
Origin subject: `muse-native-profile@R1`
Return target: `brainstorming:muse-native-profile@R1`
Research question: `Can current Codex native custom agents use muse-spark-1.3-contributor at max reasoning through CLIProxyAPI backed by Muse/Meta OAuth while preserving the MCP/skills and lifecycle properties required by codex_workflow, and which existing muse-max mechanisms remain necessary?`
Return reconciliation: `pending`
Return reconciliation result: `none`

## Scope

Verify the current external/runtime facts that gate Project Definition for the proposed third `muse-native` profile.

Evidence distinguishes:
- CLIProxyAPI Muse OAuth/model capability;
- API/Responses compatibility needed by Codex;
- current Codex custom-agent model/reasoning/tool/skill inheritance semantics;
- known compatibility risks;
- repository-local guarantees that should remain product requirements versus transport mechanisms specific to external `muse exec`.

## Sources / evidence

### CLIProxyAPI

- Repository: https://github.com/router-for-me/CLIProxyAPI
- Latest release observed: `v7.3.10`, published 2026-09-20.
- Meta/Muse provider PR: https://github.com/router-for-me/CLIProxyAPI/pull/5502 — merged 2026-09-15.
- Meta OAuth implementation: `internal/auth/meta/meta.go` and `sdk/auth/meta.go` on current `main`.
- Meta request execution: `internal/runtime/executor/meta_executor_execute.go` on current `main`.
- Model registry: `internal/registry/models/models.json` on current `main`.

### Codex

- Current official Subagents documentation: https://developers.openai.com/codex/subagents
- Current Codex configuration reference/sample for `model_provider` and model providers.
- Current public Codex issue evidence used only as compatibility-risk evidence:
  - https://github.com/openai/codex/issues/16475 — MCP inheritance failures reported despite documented inheritance.
  - https://github.com/openai/codex/issues/29846 — `skills.config` layering/re-enable limitation.
  - https://github.com/openai/codex/issues/20135 — MCP inheritance/scoping limitations.

## Verified findings

### F1 — CLIProxyAPI now has native Muse/Meta OAuth Device Flow

Current CLIProxyAPI contains a first-class Meta authenticator implementing RFC 8628 device authorization against `auth.meta.com`. The flow uses the Muse OAuth client identity, persists OAuth state and mints/refreshes a Meta API credential through the Muse Code key path.

PR #5502 is merged, not merely proposed. Its discussion contains an end-to-end report using a paid Muse Code subscription account: device authorization, credential minting, model catalog and model completions were exercised successfully.

This is sufficient evidence that the intended subscription-backed authentication path exists in the current CLIProxyAPI line. It is not yet workstation-specific proof for this project's deployment.

### F2 — CLIProxyAPI advertises Muse Spark 1.3 Contributor with `max`

The current model registry contains:

- `muse-spark-1.3`;
- `muse-spark-1.3-contributor`.

For `muse-spark-1.3-contributor`, the registry advertises:
- context length: 1,048,576;
- max completion tokens: 65,536;
- thinking levels: `minimal | low | medium | high | xhigh | max`;
- text and image input.

Therefore the requested `muse-spark-1.3-contributor / max` allocation is represented by the current CLIProxyAPI provider catalog.

### F3 — CLIProxyAPI contains a Codex/Responses-oriented Meta execution path

The current Meta executor has a `prepareResponsesRequest` path and translates requests to the internal `codex` format before applying thinking/reasoning controls and forwarding them.

This is stronger evidence than a generic Chat Completions-only proxy: CLIProxyAPI has explicit Codex/Responses translation for the Meta executor.

A live Codex native-worker request through this exact Meta OAuth route is still required before production acceptance because static source support does not prove the installed router/client/provider combination.

### F4 — current Codex custom agents support per-agent model and reasoning configuration

Current official Codex Subagents documentation states that local custom agents are standalone TOML configuration layers and can override normal Codex session settings.

The documentation explicitly supports:
- `model`;
- `model_reasoning_effort`;
- `sandbox_mode`;
- `mcp_servers`;
- `skills.config`.

Codex also supports custom model providers through normal session configuration using `model_provider` plus `[model_providers.<id>]`. Because custom agent files are loaded as session configuration layers, routing a custom worker through a configured CLIProxyAPI provider is architecturally supported.

The exact `model_provider` + CLIProxyAPI + Contributor/Max worker combination remains a required live compatibility probe rather than an assumption.

### F5 — MCP and skills inheritance are documented, but must be acceptance-tested

Official Subagents documentation states that `mcp_servers` and `skills.config` inherit from the parent when omitted by a custom agent.

This directly addresses two major drawbacks of the current external Muse adapter.

However, current public Codex issues show real edge cases:
- subagents have been reported to miss inherited MCP tools despite the documented contract;
- `skills.config` has layering limitations when a skill is disabled at a broader level;
- inherited MCP servers can be hard to narrow and may create duplicated runtime processes.

Therefore Project Definition should not promise that migration automatically fixes every MCP/skill problem. It should require a live acceptance matrix for the actual installed Codex version and the project's required MCP/skills.

### F6 — native worker lifecycle can replace transport mechanisms, not workflow guarantees

For `muse-native`, native Codex worker lifecycle can in principle own:
- spawn/wait/continuation;
- worker thread/session lifecycle;
- cancellation/stop behavior;
- normal subagent result return;
- sandbox/permission inheritance;
- MCP/tool/skill session configuration.

That means these current external-Muse mechanisms should not be mandatory implementation requirements for the new profile:
- `runtime/muse_worker.py` subprocess transport;
- Muse CLI JSONL normalization;
- Muse session registry/lease as the native-profile worker identity transport;
- terminal/Code Mode wait workaround;
- Muse-specific raw invocation retention solely required by external process management;
- capability-hint prompt plumbing used as a substitute for direct tool/skill availability.

But the product-level guarantees they currently help enforce must remain where applicable:
- role identity and authority boundaries;
- independent Executor versus Tester;
- freshness/independence semantics;
- bounded worker packages;
- safe cancellation and clear failure reporting;
- no silent provider/model fallback;
- controlled concurrency and workspace ownership;
- durable Project Workflow state remains outside ephemeral worker threads.

### F7 — keep external `muse-max` during the experiment

There is no evidence supporting immediate deletion of the existing `muse-max` path.

Keeping all three profiles initially provides:
- a fallback if Codex native/provider integration fails;
- A/B comparison of Muse Code harness versus Codex harness using the same Contributor/Max model target;
- a clean migration boundary where external adapter code can be retired later only through a separate evidence-backed decision.

## Feasibility conclusion

**Feasible enough for Project Definition.**

No current evidence blocks defining and planning a third native profile.

The main unresolved items are implementation/live-validation facts, not product decisions:
1. exact custom-agent/provider TOML and CLIProxyAPI endpoint configuration on the workstation;
2. live native worker inference using OAuth-backed `muse-spark-1.3-contributor / max`;
3. MCP inheritance for the exact servers used by this workflow;
4. skill availability/invocation for the exact installed skill set;
5. worker wait/resume/cancel behavior in the current Codex build;
6. comparison against external `muse-max` for quality and lifecycle regressions.

These should become staged execution/acceptance gates rather than blockers to Definition.

## Definition candidates

Evidence supports promoting the following only after the explicit Brainstorming → Definition gate:

- Add a third compute profile, provisionally named `muse-native`.
- Keep `plus` and external `muse-max` unchanged during this feature.
- Route all six workflow worker roles through native Codex custom-agent lifecycle under `muse-native`.
- Target `muse-spark-1.3-contributor` with `max` reasoning through CLIProxyAPI.
- Use CLIProxyAPI Muse/Meta OAuth backed by the user's Muse subscription.
- Preserve role topology and Executor/Tester independence across all profiles.
- Treat native MCP/skills inheritance as a required live acceptance property, not an assumed benefit.
- Preserve fail-closed model/provider selection; do not silently fall back to another Muse model, effort or provider.
- Keep external `muse-max` available until a separate later decision explicitly retires it.
- Make live end-to-end provider, MCP, skill, wait/resume/cancel and quality comparison evidence part of acceptance.

## Remaining uncertainties

- Exact installed workstation CLIProxyAPI version/configuration is deployment evidence and was not changed by this Research.
- Static source and documentation do not prove the local Codex client can route this custom agent successfully until a live probe is executed.
- Known Codex MCP/skills issues may affect the exact environment even though the documented inheritance contract is suitable.

No unresolved user/product/strategic choice remains that must be answered before Project Definition.
