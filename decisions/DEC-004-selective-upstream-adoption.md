# Decision — selective upstream 1.1.18 adoption

- Decision ID: `DEC-004`
- Date: `2026-09-20`
- Status: `accepted`
- Authority: `user`
- Supersedes: `none`
- Related requirements: `REQ-001, REQ-002, REQ-003, REQ-004, REQ-016, REQ-017, REQ-018`
- Related milestone/card: `none`

## Context

The fork and upstream have materially diverged since the common 1.1.17 baseline. Whole-branch synchronization would mix useful runtime hardening with conflicting orchestration choices.

## Decision

Adopt selected upstream 1.1.18 behavior semantically rather than merging/cherry-picking the release wholesale.

Adopt:
- narrower project-only same-version update behavior;
- no redundant release download when installed runtime already matches the selected release;
- backup only existing target-project files actually changed by project-only update;
- true current-project no-op without a new backup;
- stale legacy route-reference rejection;
- reviewed `--legacy-local-instructions` handling for bootstrap/install/update;
- the `workflow_break_down.md` → `workflow_breakdown.md` rename;
- useful upstream benchmark/deep-dive documentation, adapted to the fork's resulting architecture.

Preserve:
- existing historical `.source_backup/<version>` project-source resolution;
- existing multi-project catch-up behavior;
- explicit downgrade protection, including on the new project-only path.

Keep Medium route and Deployment Token Report absent.

## Rationale

This captures independently valuable fixes and documentation while preserving fork-specific Muse architecture and accepted product decisions.

## Alternatives considered

- Merge upstream 1.1.18 wholesale: rejected.
- Cherry-pick broad multi-agent commits unchanged: rejected.

## Consequences

Implementation must re-express upstream behavior in the fork rather than assume source-level compatibility. Tests must protect the fork-specific downgrade and profile/runtime semantics during adaptation.

## Required authoritative updates

- Requirements / Project Definition: captured in `requirements/REQUIREMENTS.md`.
- Planning: must sequence runtime hardening separately from orchestration cleanup where appropriate.
- Task Card/OpenSpec: none yet.
- PROJECT.md: decision pointer required.

## Provenance

- Source discussion/request: `brainstorming/upstream-1.1.18-alignment.md`
- Evidence/research: `research/upstream-1.1.18-audit.md`
