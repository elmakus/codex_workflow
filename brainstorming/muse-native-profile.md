# Brainstorm — Muse native worker profile

Date: `2026-09-21`
Scope ID: `muse-native-profile`
Revision: `R1`
Status: `ready_for_definition`

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

## Research outcome

Completed Research: `research/muse-native-profile.md` / `R-MUSE-NATIVE-01`.

Verified conclusions:
- current CLIProxyAPI has merged Muse/Meta OAuth Device Flow and subscription-backed credential minting;
- current CLIProxyAPI advertises `muse-spark-1.3-contributor` with `max` reasoning and contains an explicit Codex/Responses-oriented Meta execution path;
- current Codex custom agents can override model/reasoning and inherit `mcp_servers` and `skills.config` from the parent when omitted;
- live compatibility must still be proven for the exact workstation because current Codex issue evidence shows real MCP/skills inheritance edge cases;
- native Codex lifecycle can replace external Muse transport mechanisms for the new profile, but must preserve the existing workflow guarantees: role identity, Executor/Tester independence, freshness, bounded packages, safe cancellation/failure reporting, fail-closed provider selection, workspace ownership and durable Project Workflow state;
- external `muse-max` should remain available during this feature as fallback and A/B comparison.

No material user/product/strategic question remains before Project Definition. Remaining uncertainty is implementation/live-validation evidence and belongs in Planning/Execution acceptance.

## Definition candidates

- add a third compute profile, provisionally `muse-native`;
- keep `plus` and external `muse-max` unchanged during this feature;
- route all six workflow roles through native Codex custom-agent lifecycle under `muse-native`;
- target `muse-spark-1.3-contributor / max` through CLIProxyAPI using Muse/Meta OAuth from the Muse subscription;
- require live native-provider, MCP, skill, wait/resume/cancel and quality-comparison acceptance;
- no silent provider/model/effort fallback;
- do not retire external `muse-max` without a separate later evidence-backed decision.


## Muse Max → Muse Native preservation matrix

The feature must migrate **behavioral guarantees**, not mechanically copy external Muse transport machinery. The following matrix is the parity contract to carry into Project Definition and Planning.

| Current `muse-max` behavior/mechanism | `muse-native` target | Classification |
| --- | --- | --- |
| Quiet milestone orchestration: routine worker start/wait/status/session/Git/liveness narration stays silent | Preserve the same communication policy verbatim in behavior; healthy native-worker waiting must not create user-visible commentary | **MUST preserve** |
| Healthy worker state must not wake Main merely for liveness | Use native Codex worker wait semantics; timeout/no-new-state is followed by another long wait, never status/list/progress polling | **MUST preserve, native replacement** |
| No timer/heartbeat/"still working" Main turns | Same invariant under native lifecycle | **MUST preserve** |
| Main is orchestrator, not production executor | Unchanged | **MUST preserve** |
| Six roles: Explorer, Investigator, Default Executor, Senior Executor, Tester, Archivist | Same six roles through native Codex workers | **MUST preserve** |
| Muse Spark 1.3 Contributor / max for all six Muse roles | Same model/effort through CLIProxyAPI + Muse OAuth; fail closed if exact route is unavailable | **MUST preserve** |
| Explorer is disposable, bounded, read-only project-context discovery | Same native role semantics | **MUST preserve** |
| Qualifying Investigator problem uses exactly three independent lanes | Same exact-three-lane contract; native Codex concurrency replaces Muse batch transport | **MUST preserve** |
| Worker packages use Task ID + role-specific bounded capsule | Same package/report contract | **MUST preserve** |
| Freshness means a genuinely fresh worker context, not relabeling/resuming an old one | Spawn a fresh native worker, normally with `fork_turns="none"`, and transfer minimal durable context | **MUST preserve, native replacement** |
| Ordinary follow-up/repair resumes the owning logical worker when safe | Resume the same native Codex worker/thread when safe | **MUST preserve, native replacement** |
| Tester must be independent from Executor | Tester is always a separate native worker/thread from the implementing Executor | **MUST preserve** |
| RED repair lifecycle: Executor → independent Tester RED → same owning Executor repair → same independent Tester full recheck | Same lifecycle using native worker resume | **MUST preserve** |
| Slow worker / wait timeout does not transfer work to Main | Wait/resume the worker; only irrecoverable unavailability enters recovery | **MUST preserve** |
| Main follow-up is never used to poll progress | Same; follow-up only carries new evidence/changed decisions/capsule data | **MUST preserve** |
| No sibling-to-sibling coordination | Same; material events/results route through Main | **MUST preserve** |
| Blockers, course changes, critical partials may require Main attention despite quiet mode | Use the native Codex material-event path where available; routine progress remains silent | **MUST preserve, native equivalent** |
| Controlled concurrency only for already-authorized independent lanes with isolated/non-overlapping ownership | Preserve dependency/workspace-safety rules; use native Codex concurrency instead of Muse batch helper | **MUST preserve behavior** |
| `MuseCapabilityHints` communicates required/relevant skills/capabilities to a separate Muse capability plane | Prefer actual inherited native `mcp_servers` / `skills.config`; missing required capability must fail visibly | **REPLACE, do not mechanically port** |
| One outer Code Mode cell owns `muse_worker.py` + nested terminal waits | Native Codex worker lifecycle/wait owns waiting directly | **REMOVE transport workaround** |
| `runtime/muse_worker.py` subprocess, JSONL normalization and generated Muse prompt/schema files | Not used by `muse-native` | **REMOVE for native profile** |
| Stable Muse `session_id` + per-turn `invocation_id`, private registry and process-safe lease | Native Codex worker/thread identity and lifecycle; retain only the semantic distinction between same-worker continuation and fresh-worker replacement | **REPLACE transport mechanism** |
| Fail-closed Muse resume probe/session binding | Native resume must still fail visibly; never silently substitute a fresh worker/model/provider under the old logical identity | **MUST preserve semantic** |
| Muse process-tree timeout/cancellation cleanup | Native Codex cancellation/stop semantics; live acceptance must prove no orphaned worker/process behavior relevant to this deployment | **REPLACE + revalidate** |
| Private `muse_runs/` raw JSONL/stderr retention and retention quotas | Do not recreate solely for parity; retain only evidence/reporting actually required by native workflow acceptance | **DO NOT port unless evidence requires** |
| Muse sandbox disabled inside workstation Docker | Native Codex sandbox/permissions become authoritative; do not inherit the Muse-specific `--disable-sandbox` workaround | **DO NOT port** |
| Managed Muse batch helper capped at 8 calls | Do not carry this transport-specific cap into native profile; native platform/account concurrency applies, while workflow-level dependency and exact-three Investigator rules remain | **DO NOT port** |
| External Muse CLI authentication/subscription ownership | CLIProxyAPI owns Muse OAuth credential path; Codex sees the configured provider route, without silent direct-Meta/API-key fallback | **REPLACE** |
| Compact evidence-linked worker result returned to Main | Preserve concise decision-ready worker reports and keep bulky logs/context out of Main unless needed | **MUST preserve** |

### Parity gates

Before `muse-native` can be considered accepted, live evidence must demonstrate at least:

1. exact `muse-spark-1.3-contributor / max` provider identity with no fallback;
2. all six native roles render and launch correctly;
3. quiet milestone communication remains active;
4. a multi-minute healthy native worker causes no Main-driven status/progress polling;
5. ordinary follow-up resumes the same native worker;
6. a freshness requirement creates a genuinely fresh context;
7. Executor and Tester are independent;
8. RED → same Executor repair → same Tester recheck works;
9. the exact-three Investigator lane contract works with native workers;
10. required MCP capability is available to a native worker or fails visibly;
11. required skill availability/invocation is verified in the installed Codex environment;
12. timeout/cancel/recovery behavior is safe and does not silently replace identity/provider;
13. `plus` and external `muse-max` remain behaviorally unchanged;
14. an A/B task can compare external `muse-max` and `muse-native` without changing the higher-level acceptance contract.

This matrix is intended to prevent a transport simplification from becoming an accidental orchestration-semantics regression.

## Definition promotion

- Definition promotion authorization: `pending`
- Definition promotion subject: `none`

The `#feature` directive created this workstream but does not authorize Project Definition promotion.

## Next action

This scope is `ready_for_definition`. Stop at the policy-owned promotion boundary until the user explicitly authorizes Project Definition for `muse-native-profile@R1`.
