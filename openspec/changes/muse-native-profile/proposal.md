# Muse native profile contract

## Why

The fork adds a native-Codex Muse path so the same Contributor/Max worker allocation can run through native Codex lifecycle without deleting the proven external `muse-max` path or weakening its orchestration guarantees.

## Authority

- `requirements/REQUIREMENTS.md` Revision R3 — REQ-030 through REQ-044
- `decisions/DEC-007-muse-native-profile.md`
- `planning/MASTER_PLAN.md` Revision R4
- `implementation/workstreams/feature-muse-native-profile/cards/M07-T01.md`

## Change

Define `muse-native` as the third compute profile. Its six workers use native Codex lifecycle, target `muse-spark-1.3-contributor` at `max`, and select the configured CLIProxyAPI provider without silent fallback. Profile rendering owns only the minimum selector/config surface and preserves unrelated provider settings and authentication material.

The native profile preserves the profile-independent orchestration guarantees from Definition while replacing external-Muse transport mechanisms with native Codex lifecycle/capability mechanisms. Existing `plus` and external `muse-max` behavior remain regression boundaries.

## Non-goals

No login/token ownership, no retirement of `muse-max`, no copied Muse subprocess/session/JSONL/wait stack for symmetry, no VERSION/release/deployment change, and no silent provider/model fallback.
