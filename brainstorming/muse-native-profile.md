# Brainstorm — Muse native worker profile

Date: `2026-09-21`
Scope ID: `muse-native-profile`
Revision: `R1`
Status: `active`

## Problem / goal

Evaluate and define a third `codex_workflow` compute profile that keeps the current six-role orchestration semantics while replacing the external Muse Code CLI transport with native Codex subagents backed by Muse Spark.

The intended value is to remove transport-specific complexity around `muse exec` — external process/session management, Code Mode waiting, adapter capability hints, subprocess cleanup and Muse-specific session plumbing — when equivalent lifecycle/tooling can be supplied by the native Codex worker runtime.

## Explicit user/product choices already made

These choices are exploratory inputs and must later be reconciled through Project Definition before becoming canonical authority:

- keep the existing `plus` profile;
- keep the existing external-CLI `muse-max` profile for comparison/fallback during the new feature;
- add a third profile, working name `muse-native`;
- preserve the existing six logical workflow roles and their authority boundaries;
- use Muse Spark 1.3 Contributor with `max` reasoning for the native workers;
- obtain Muse access through CLIProxyAPI using Muse/Meta OAuth from the Muse subscription rather than direct Meta API billing.

## Current architecture hypothesis

The candidate worker path is:

```text
Codex Main
  -> native Codex worker lifecycle
  -> CLIProxyAPI OpenAI-compatible route
  -> Muse/Meta OAuth credential
  -> muse-spark-1.3-contributor / max
```

This should be compared against the current:

```text
Codex Main
  -> Code Mode
  -> runtime/muse_worker.py
  -> muse exec
  -> Muse Code harness
  -> muse-spark-1.3-contributor / max
```

The feature should change the worker harness/transport, not collapse role separation or make Executor and Tester the same logical worker.

## Expected benefits to verify

- native Codex wait/continuation rather than external terminal-process waiting;
- native subagent MCP/tool availability instead of prompt-level capability hints;
- native skill/config inheritance where supported by the actual Codex runtime;
- simpler cancellation and worker lifecycle ownership;
- less `codex_workflow`-owned Muse transport code;
- direct comparison of Muse Code harness versus Codex harness while keeping the same Muse model/effort.

## Material evidence questions

Formal Research is required before Definition for these current, externally changing facts:

1. Does current CLIProxyAPI release support Muse/Meta OAuth from a Muse Code subscription end to end?
2. Does it expose `muse-spark-1.3-contributor` with `max` reasoning on the route shape usable by Codex?
3. What exact OpenAI/Codex-compatible API surface does CLIProxyAPI expose for the Meta/Muse provider, including Responses compatibility where relevant?
4. Can a current Codex custom/native worker pin that routed model/provider while retaining the required MCP/tool and skill behavior?
5. What compatibility or correctness risks exist when replacing Muse Code harness semantics with native Codex worker semantics?
6. Which current `muse-max` guarantees must be preserved versus which adapter/runtime mechanisms become unnecessary only for `muse-native`?

## Alternatives

### A — keep only external `muse-max`

Lowest migration risk, but retains the adapter/MCP/skills/wait complexity that motivated the feature.

### B — add `muse-native` alongside `plus` and `muse-max`

Current exploratory direction. It permits live A/B evidence before any later decision to retire the external Muse path.

### C — immediately replace `muse-max` with native Muse workers

Not selected for this feature. It would remove the comparison/fallback path before native behavior is proven.

## Definition promotion

- Definition promotion authorization: `pending`
- Definition promotion subject: `none`

The `#feature` directive created this workstream but does not authorize Project Definition promotion.

## Next action

Create and complete a formal Research obligation for the material evidence questions above, then reconcile findings into this exact `muse-native-profile@R1` scope.
