# M08-T02 workstation preflight blocker

Date: 2026-09-21
Card: `M08-T02 — First live native worker and capability gate`

## User-owned prerequisite recheck

After the user reported setup complete, read-only preflight on the exact `Tower` workstation established:

- external CLIProxyAPI Muse/Meta OAuth state now exists (Meta credential file present; contents not read);
- CLIProxyAPI config contains one client API-key entry; its value was not read or printed;
- `chatgpt-ce-workstation` can reach `http://192.168.2.104:8317/v1/models`; an unauthenticated request returns HTTP 401;
- `127.0.0.1:8317` and `host.docker.internal:8317` are not reachable from that container;
- Codex user config `/home/codex/.codex/config.toml` still contains no `[model_providers.cliproxyapi]` route;
- no proxy/API-key/token/auth environment variable is present in the `chatgpt-ce-workstation` container environment;
- active workflow profile remains `muse-max`.

## Fail-closed profile attempt

The existing installed transactional profile command was invoked once as the concrete required operation:

`python3 /home/codex/.codex/codex_workflow/runtime/workflow.py profile muse-native --json`

It rejected `muse-native` at argument validation because the installed workflow runtime currently accepts only `plus | muse-max`. Readback confirmed `compute_profile = "muse-max"`; no profile/config/worker mutation occurred.

This shows the installed package has the same displayed version `1.1.18-private.3` but predates the workstream's M07 `muse-native` runtime implementation.

## Required prerequisite before retry

Before M08-T02 may start profile mutation:

1. Codex must have a user-owned custom provider route named `cliproxyapi`, using the reachable workstation endpoint and Responses wire API.
2. Codex must have non-repository client authentication for that provider (for example an `env_key` whose environment variable is available to the Codex process and contains the existing CLIProxyAPI client key).
3. The bounded probe must invoke the workstream implementation of the transactional `muse-native` profile operation, or the installed runtime must first contain that already-accepted M07 functionality. A full release/deployment remains outside M08-T02 scope unless separately authorized.

No credential/token/key value was read, copied, printed, persisted or changed.
