# Muse native profile

## Profile set and allocation

The runtime MUST support exactly `plus`, external `muse-max`, and native `muse-native`.

For every supported worker role under `muse-native`, the effective allocation MUST be native Codex lifecycle, model `muse-spark-1.3-contributor`, reasoning effort `max`, and the configured CLIProxyAPI provider route.

Main's own selected model MUST remain unchanged by worker-profile selection.

## Provider ownership and fail-closed behavior

The workflow MAY own the minimum provider selector/config necessary to route native workers, but MUST preserve unrelated user-owned Codex/provider configuration.

Profile operations MUST NOT create, migrate, serialize, expose into normal evidence, or delete authentication credentials or access tokens.

Missing or unsupported provider/model/effort/capability state MUST fail visibly. The runtime MUST NOT silently substitute a different provider, model, effort, direct billing route, or worker identity.

## Existing-profile preservation

`plus` MUST retain its native Codex allocation and behavior.

External `muse-max` MUST retain its external Muse adapter/session/capability-hint path and external-harness internal-agent disabling behavior.

Adding `muse-native` MUST NOT require `muse_worker.py`, Muse session registry/lease, Muse JSONL/raw-run retention, `--disable-sandbox`, one-cell Muse wait, or `MuseCapabilityHints` for the native path merely for symmetry.

## Internal-agent enablement and switching

Internal Codex agents MUST be enabled for `plus` and `muse-native`, and disabled for external `muse-max` according to the existing fail-closed settings contract.

Switching profiles MUST remain transactional/idempotent, preserve unrelated settings, and restore selected-profile state coherently across existing update/preservation paths.

## Native orchestration invariants

When M08 behavior is materialized, `muse-native` MUST preserve quiet milestone communication, no Main-driven liveness polling, same-worker ordinary continuation, genuinely fresh contexts when required, independent Tester repair/recheck, exact-three Investigator lanes, direct-to-Main reporting, controlled concurrency, bounded material-event semantics, native MCP/skill capability behavior, and safe cancellation/recovery as defined by R3/DEC-007.

These are behavior contracts, not permission to pre-create a second durable scheduler/session registry. Evidence that native lifecycle cannot satisfy them routes through the plan/Definition re-evaluation gates.

## Live acceptance boundary

Static/documented provider, MCP, skill and lifecycle support is insufficient for final acceptance. Live evidence MUST ultimately cover the REQ-043 matrix in the installed environment.

An unconfigured auth environment is a precise blocker for auth-backed live gates, not permission to weaken acceptance or make repository code own credentials.
