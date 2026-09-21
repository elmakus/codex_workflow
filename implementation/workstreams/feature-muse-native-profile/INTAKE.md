# Intake — Muse native worker profile

- Workstream ID: `feature-muse-native-profile`
- Kind: `feature`
- Status: `active`
- Branch: `feat/muse-native-profile`
- Integration target: `main`

## Authorized subject

Add a third `codex_workflow` compute profile that preserves the existing six-role workflow topology while running Muse Spark as **native Codex workers** instead of through the external `muse exec` adapter.

The requested target is:

- retain existing `plus`;
- retain existing external-CLI `muse-max` for comparison/fallback;
- add a new native profile (working name: `muse-native`);
- route Explorer, Investigator, Default Executor, Senior Executor, Tester and Archivist through native Codex subagent lifecycle;
- use `muse-spark-1.3-contributor` with `max` reasoning;
- provide the Muse subscription credentials to the native Codex model route through CLIProxyAPI using Muse/Meta OAuth rather than direct Meta API billing.

The feature is intended to remove the external Muse transport complexity where native Codex lifecycle already provides worker waiting, continuation, tool/MCP availability and skill inheritance, while preserving the higher-level role separation and verification semantics of `codex_workflow`.

## Pre-creation discovery and dependency classification

- Baseline: `main@016a42ba0cf0d274bf12d718db6d7580abe54658`.
- No matching `muse-native` branch, workstream or PR was found.
- Existing `muse-max` behavior required by this feature is already integrated on `main`.
- No unmerged parent-only state is required to define or implement the feature.

Classification: **independent**.

Selected base: `main@016a42ba0cf0d274bf12d718db6d7580abe54658`.

## Current evidence to reconcile during discovery

External verification performed immediately before intake found:

- CLIProxyAPI current release line includes the merged native Meta/Muse provider and OAuth Device Flow.
- The provider has been exercised with a paid Muse Code subscription account.
- The current CLIProxyAPI model registry advertises `muse-spark-1.3-contributor` with reasoning levels through `max`.
- The native-worker design still requires repository-level verification of the exact Codex custom-agent/provider configuration, inherited MCP/skills behavior, model-route compatibility and live end-to-end worker execution.

These findings are evidence only until reconciled through the normal Brainstorming/Research and Project Definition lifecycle.

## Downstream classification

Pending Feature Intake materialization of the canonical Brainstorming scope. The `#feature` directive does not itself authorize Project Definition promotion.
