# Decision — two-profile compute model

- Decision ID: `DEC-002`
- Date: `2026-09-20`
- Status: `accepted`
- Authority: `user`
- Supersedes: `none`
- Related requirements: `REQ-011, REQ-012, REQ-013`
- Related milestone/card: `none`

## Context

The fork currently exposes `plus`, `luna-xhigh`, `pro-x5`, and `muse-max`. The desired architecture reduces profile surface while retaining both native Codex-worker and Muse-backed execution modes.

## Decision

Only two compute profiles remain:
- `plus`
- `muse-max`

Remove `luna-xhigh` and `pro-x5` plus their profile-specific code, tests, commands, documentation and compatibility branches.

Under `plus`, workflow workers use the internal Codex worker lifecycle.

Under `muse-max`, all remaining worker roles use the existing Muse process/session lifecycle. There is no internal Companion exception because Companion is removed.

Do not adopt upstream's `multi_agent_v2` timeout values or change multi-agent versioning as part of this scope. Existing workflow ownership of `[features] multi_agent = true` and non-ownership/removal of `multi_agent_v2` settings remains unless changed by a future separately accepted decision.

## Rationale

Two profiles preserve the meaningful execution-mode distinction while removing profile complexity that no longer provides desired product value.

## Alternatives considered

- Keep all four profiles: rejected.
- Replace current multi-agent configuration with upstream V2 timeout ownership: explicitly not part of this change.

## Consequences

Profile rendering, CLI choices, worker model mapping, tests, docs and release behavior must contain no stale `luna-xhigh` or `pro-x5` assumptions.

## Required authoritative updates

- Requirements / Project Definition: captured in `requirements/REQUIREMENTS.md`.
- Planning: must cover safe profile removal and compatibility/regression checks.
- Task Card/OpenSpec: none yet.
- PROJECT.md: decision pointer required.

## Provenance

- Source discussion/request: `brainstorming/upstream-1.1.18-alignment.md`
- Evidence/research: `research/upstream-1.1.18-audit.md`
