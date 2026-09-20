# MF-T01 — Fail closed on post-compaction worker misrouting

- Milestone: `micro-fix`

> This file is a stable Task Card contract. Mutable execution/review/result state lives only in the selected manifest-bound workstream Task Board.

## Authority slice

- Master Plan / milestone contract: none — qualified micro-fix under R6 + `implementation/workstreams/issue-compaction-runtime-routing/INTAKE.md`
- Requirements: `requirements/REQUIREMENTS.md` REQ-011, REQ-012, REQ-013, REQ-014
- Accepted decisions: `decisions/DEC-002-compute-profiles.md`; `decisions/DEC-003-communication-context.md`
- Relevant OpenSpec: none
- Accepted dependency results: none

### Must preserve

- `plus` keeps all six supported workflow roles on the internal Codex worker lifecycle.
- `muse-max` keeps all six supported workflow roles on Muse Spark 1.3 Contributor / max through the retained Muse process/session adapter; there is no internal Codex workflow-role exception.
- Existing Muse logical-session identity, resume, timeout/cancellation, isolation and normalized-result semantics remain unchanged.
- Unrelated user-owned Codex configuration is preserved.
- Profile switching and update/bootstrap behavior remain transactional and idempotent.
- The compaction correction stays token-light: no mandatory full Heavy/delegation/document reload after compaction.

### Must not / rationale that must travel

- Do not treat the observed workflow-version upgrade as the primary cause; the guard must work when the workflow version is unchanged.
- Do not rely only on prose in Heavy/delegation context, because that context can be weakened or stale after compaction.
- Do not silently claim fail-closed protection when an effective MultiAgentV2 override would re-expose internal agents.
- Do not disable Muse worker execution or change `plus` worker availability.

## Dependencies

- none

## Outcome

A forgotten or stale post-compaction Main routing decision cannot successfully dispatch an internal Codex workflow worker while `muse-max` is active. The always-injected contract also forces a minimal active-profile revalidation before worker dispatch so stale session memory is not authoritative.

## Scope

### Included

- Make workflow-owned Codex internal-agent enablement profile-aware through `[agents].enabled`.
- Set `[agents].enabled = false` under `muse-max` and `true` under `plus`, while preserving DEC-002's `[features].multi_agent = true` contract.
- Update profile changes as well as bootstrap/update materialization so the effective guard follows the active profile.
- Fail closed when a known external MultiAgentV2 override would defeat the `muse-max` internal-agent guard.
- Add a compact always-injected dispatch invariant to `codex_workflow/AGENTS.md`.
- Add focused regression coverage and run the existing workflow/Muse suites.

### Excluded

- General Codex compaction implementation changes.
- Project Workflow policy/router persistence; that is handled in its own repository/workstream.
- Changes to Muse model/session/process semantics.
- Reworking the separate `feat/muse-main-orchestration-efficiency` feature workstream.
- Release publication or production Workstation deployment.

## Acceptance

1. Rendering/applying `plus` sets `[agents].enabled = true` and preserves `[features].multi_agent = true`.
2. Rendering/applying `muse-max` sets `[agents].enabled = false` while preserving `[features].multi_agent = true`; with MultiAgentV2 disabled, the supported Codex runtime therefore does not expose `spawn_agent` / wait/list/send internal-agent tools.
3. Switching `plus -> muse-max -> plus` updates `[agents].enabled` deterministically without changing unrelated config.
4. `muse-max` fails closed with a clear validation error when an effective externally-owned MultiAgentV2 enable would override the internal-agent disable gate.
5. The always-injected AGENTS contract requires reading only the active `settings.toml` immediately before each worker dispatch, rejects remembered pre-compaction routing as authority, and forbids internal Codex worker APIs under `muse-max` even if a stale long-lived session still exposes them.
6. Existing `muse-max` profile allocation remains six Muse roles; existing `plus` allocations remain unchanged.
7. Existing Muse adapter/session tests and workflow runtime/profile regressions remain GREEN.
8. No full-document post-compaction reload is introduced.

## Required tests / checks

- Focused platform/profile unit tests for both profiles and profile switching.
- Regression test for external MultiAgentV2 conflict fail-closed behavior.
- Contract test for the compact AGENTS dispatch invariant.
- Existing workflow runtime regression suite.
- Existing Muse profile and Muse worker adapter suites.
- Python compile / diff-check / package validation as normally required for this repository.

## External write/readback needs

none

## Independent review

RECOMMENDED — behavioral/runtime-configuration micro-fix that changes worker tool availability and fail-closed behavior.

## Contract overrides

None.
