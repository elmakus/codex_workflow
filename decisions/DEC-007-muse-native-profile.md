# Decision — three-profile compute model and native Muse worker path

- Decision ID: `DEC-007`
- Date: `2026-09-21`
- Status: `accepted`
- Authority: `user`
- Supersedes: `DEC-002 profile-count clause; DEC-003 plus-only Material Event Push applicability clause`
- Related requirements: `REQ-030–REQ-044`
- Related milestone/card: `none`

## Context

The fork currently supports `plus` and external-CLI `muse-max`. The external Muse path now has mature role/session/wait/safety behavior, but it also requires a separate `muse exec` transport, capability-hint plane and long-running terminal-wait workaround.

Verified current evidence shows that CLIProxyAPI now supports Muse/Meta OAuth, exposes `muse-spark-1.3-contributor` with `max` reasoning, and contains a Codex/Responses-oriented Meta execution path. Current Codex custom agents support per-agent model/reasoning configuration and document parent inheritance for MCP and skills, although live issue evidence requires those capability paths to be acceptance-tested rather than assumed.

## Decision

Add a third supported compute profile named `muse-native`.

The supported profile set becomes exactly:
- `plus`;
- `muse-max`;
- `muse-native`.

`luna-xhigh` and `pro-x5` remain removed/unsupported.

Under `muse-native`:
- all six supported workflow roles use the native Codex worker lifecycle;
- Main remains the user-selected Codex model;
- all six roles target `muse-spark-1.3-contributor` with `max` reasoning;
- model access is routed through the configured CLIProxyAPI provider using Muse/Meta OAuth-backed subscription credentials;
- provider/model/reasoning selection is fail-closed with no silent fallback to another Muse allocation, direct Meta billing path or another provider.

The new profile preserves the mature higher-level orchestration contract from `muse-max`: quiet milestone communication, no liveness polling, Task ID/capsule/report discipline, role boundaries, exact-three Investigator lanes, same-worker ordinary continuation, genuine fresh contexts when required, independent Tester, RED → owning Executor repair → same independent Tester recheck, direct worker-to-Main communication and controlled concurrency.

These are behavioral guarantees, not requirements to copy external Muse transport internals. `muse-native` uses native Codex worker/thread, wait, continuation, cancellation, sandbox and capability configuration instead of the Muse subprocess/session/JSONL/one-cell-wait machinery unless live evidence proves a narrowly scoped compatibility shim necessary.

Because `muse-native` is an internal Codex-worker profile, it may use the existing bounded Material Event Push classes (BLOCKER, COURSE_CHANGE, CRITICAL_PARTIAL) under the same no-routine-progress/no-sibling-messaging constraints as `plus`. This supersedes only DEC-003's prior `plus`-only applicability statement; external `muse-max` remains outside Material Event Push.

Keep `plus` and external `muse-max` behavior unchanged. External `muse-max` is retained as comparison/fallback and may be retired only by a later separate accepted decision.

## Rationale

A third profile makes the harness itself testable: the same Muse Contributor/Max worker allocation can be compared through Muse Code versus native Codex orchestration without prematurely deleting the proven external path.

Native lifecycle should remove substantial transport-specific complexity while giving workers direct access to Codex-native wait, continuation, MCP/skills configuration and sandbox behavior. Preserving the existing higher-level orchestration contract avoids trading implementation simplicity for behavioral regression.

## Alternatives considered

- Keep only external `muse-max`: rejected for this feature because it retains the exact MCP/skills/wait transport complexity being evaluated.
- Replace `muse-max` immediately: rejected because native provider/capability/lifecycle behavior still requires live proof.
- Use direct Meta API billing rather than Muse OAuth through CLIProxyAPI: rejected by explicit user choice.
- Copy the full external Muse adapter/session/artifact stack into `muse-native`: rejected unless a specific live compatibility failure demonstrates a narrowly necessary piece.

## Consequences

- Compute profile rendering, CLI/profile commands, tests and docs must support exactly three active profiles.
- Native worker TOMLs/configuration must support the CLIProxyAPI model route for `muse-native`.
- Internal-agent enablement must be true for both `plus` and `muse-native`, while external `muse-max` retains its existing external-harness behavior.
- Quiet communication/no-polling policy must be rendered for `muse-native`.
- MCP/skills, native wait/continuation/cancel and provider identity require live acceptance in the installed environment.
- External Muse adapter/session/capability-hint machinery remains owned by `muse-max` and must not be deleted as part of this feature.
- A later retirement decision may use A/B evidence from this profile but is outside current scope.

## Required authoritative updates

- Requirements: `requirements/REQUIREMENTS.md` Revision R3.
- Planning: new plan revision must cover native-provider feasibility, profile/rendering implementation, parity semantics and live acceptance matrix.
- Workstream: `feature-muse-native-profile`.
- PROJECT.md: add DEC-007 and current Definition provenance.

## Provenance

- Promoted scope: `brainstorming/muse-native-profile.md` — `muse-native-profile@R1`
- Research: `research/muse-native-profile.md` / `R-MUSE-NATIVE-01`
- Promotion authority: explicit user authorization on 2026-09-21
