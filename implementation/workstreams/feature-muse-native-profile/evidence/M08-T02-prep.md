# M08-T02 JIT preparation evidence — installed native surface

Date: 2026-09-21
Workstream: `feature-muse-native-profile`
Milestone: `M08 — Native orchestration parity and capability behavior`
Predecessor: `M08-T01` terminal with independent GREEN review.

## Exact installed observations

Read-only inspection of the user-owned `Tower` workstation established:

- workstation container: `chatgpt-ce-workstation:candidate-ff89c28ab47d5999`;
- installed workflow version: `1.1.18-private.3`;
- active workflow compute profile: `muse-max`;
- Codex Desktop CLI binary: `/opt/codex-desktop/resources/codex`;
- Codex version: `codex-cli 0.155.0-alpha.9.2`;
- Codex feature inventory reports `multi_agent` stable/enabled, `skill_search` stable/enabled and `skill_mcp_dependency_install` stable/enabled;
- native MCP inventory exposes enabled `node_repl` and `cua_repl` surfaces; the bundled `codex_app` MCP entry is disabled;
- six native workflow agent TOMLs are installed: Explorer, Investigator, Default Executor, Senior Executor, Tester and Archivist;
- installed skills include the built-in read-only `review-agent` skill plus user-level skills; `review-agent` is suitable for a harmless native skill-inheritance smoke;
- the Codex user config still has no `[model_providers.cliproxyapi]` route;
- running CLIProxyAPI image is `eceasy/cli-proxy-api:v7.3.4`;
- that installed CLIProxyAPI binary exposes `-meta-login`, so the installed release contains a Meta OAuth entry point;
- CLIProxyAPI publishes its service on workstation ports 8317/8085, but M07 already established that an unauthenticated `/v1/models` request returns HTTP 401.

No authentication token, API key, OAuth credential, credential-store content or secret-bearing environment value was read, copied, printed or changed.

## JIT classification

The native Codex lifecycle/capability surface is present and concrete enough to contract the next live Card without inventing a transport layer.

The live `muse-native` Card cannot start yet because the workstation lacks the required user-owned Codex `cliproxyapi` model-provider route and therefore cannot issue the exact pinned `cliproxyapi / muse-spark-1.3-contributor / max` native-worker request.

No CLIProxyAPI upgrade is currently indicated solely for Meta OAuth availability: the installed `v7.3.4` binary already exposes `-meta-login`. The remaining prerequisite is user-owned provider/account/client-auth configuration, not repository code.

## Smallest next live proof

The first live successor should prove one exact native worker path before materializing the rest of the M08 matrix:

1. temporarily select `muse-native` using the existing transactional profile operation;
2. launch one native Tester worker through the installed Codex multi-agent lifecycle with the exact Muse model/reasoning/provider allocation;
3. require the enabled native `node_repl` MCP surface and the installed read-only `review-agent` skill in a harmless verification task;
4. resume that same worker/thread once to prove ordinary native continuation identity;
5. capture non-secret provider/model/effort + worker/thread evidence and prove no external `muse_worker.py`/Muse-session transport was used;
6. restore the pre-probe `muse-max` profile and verify the installed state was restored.

After this proof is GREEN, remaining M08 no-poll/freshness/Tester-repair/Investigator/cancel-recovery coverage can be contracted JIT from the observed live native behavior.
