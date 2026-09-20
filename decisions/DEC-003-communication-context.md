# Decision — worker communication and context policy

- Decision ID: `DEC-003`
- Date: `2026-09-20`
- Status: `accepted`
- Authority: `user`
- Supersedes: `none`
- Related requirements: `REQ-008, REQ-013, REQ-014, REQ-015`
- Related milestone/card: `none`

## Context

The fork currently contains Material Event Push and exceptional sibling messaging, while Muse workers do not expose the same internal Codex `send_message` channel. Upstream 1.1.18 uses direct parent-child reports and requires a complete session-level documentation intake.

## Decision

All normal worker communication is worker ↔ Main. Direct sibling worker messaging is removed.

Material Event Push remains available only to internal Codex workers under `plus`, and only for the bounded material event classes already defined by the fork (BLOCKER, COURSE_CHANGE, CRITICAL_PARTIAL). It is not part of the `muse-max` contract and must not be emulated there.

Retain proportionate documentation intake: Main reads decision-critical project context directly and expands only when needed. Explorer handles bounded broader context discovery. Do not introduce upstream's mandatory complete `agent_docs/` session intake.

## Rationale

The resulting communication topology is simpler and deterministic, and avoids specifying a capability for Muse that the runtime does not provide. Proportionate intake better preserves Main context than mandatory whole-framework loading.

## Alternatives considered

- Keep sibling worker messaging: rejected.
- Emulate Material Event Push for Muse: rejected.
- Adopt complete session-level `agent_docs/` intake: rejected.

## Consequences

Heavy/delegation/worker instructions must describe direct Main routing consistently. Muse-specific text about unavailable material-event push should be removed rather than retained as a negative contract.

## Required authoritative updates

- Requirements / Project Definition: captured in `requirements/REQUIREMENTS.md`.
- Planning: must cover policy cleanup and regression checks.
- Task Card/OpenSpec: none yet.
- PROJECT.md: decision pointer required.

## Provenance

- Source discussion/request: `brainstorming/upstream-1.1.18-alignment.md`
- Evidence/research: `research/upstream-1.1.18-audit.md`
