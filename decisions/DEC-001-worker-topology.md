# Decision — simplified worker topology

- Decision ID: `DEC-001`
- Date: `2026-09-20`
- Status: `accepted`
- Authority: `user`
- Supersedes: `none`
- Related requirements: `REQ-005, REQ-006, REQ-007, REQ-008, REQ-009, REQ-010`
- Related milestone/card: `none`

## Context

The fork had diverged from upstream with persistent Companion and Micro Executor roles. Upstream 1.1.18 instead separates context discovery into Explorer, solution/fault research into Investigator, and returns worker results directly to Main.

## Decision

The target worker topology is:
- Explorer;
- Investigator;
- Default Executor;
- Senior Executor;
- Tester;
- Archivist.

Companion and Micro Executor are removed.

Explorer owns bounded read-only project-context discovery and evidence mapping. Investigator owns bounded fault hypotheses, solution alternatives, feasibility and prior-art research.

Every bounded problem that requires Investigator uses exactly three independent Investigator lanes with one shared Problem ID, distinct Task IDs and complementary search angles. Main compares evidence and disagreement; lanes do not vote or coordinate with one another.

Workers return results directly to Main. Sibling worker messaging is removed.

Hard report word caps are removed. Worker reports must instead be the smallest complete, evidence-linked, decision-ready report and reference bulky logs/diffs rather than reproducing them.

## Rationale

This adopts the upstream role separation and direct parent-child reporting while removing fork-specific roles that are no longer desired. It reduces topology and communication complexity without removing independent verification or specialist execution.

## Alternatives considered

- Keep persistent Companion: rejected.
- Keep Micro Executor: rejected.
- Add Explorer while retaining Companion: rejected.
- Keep optional 1/N Investigator lane count: rejected in favor of exactly three lanes when Investigator is required.

## Consequences

Worker definitions, route contracts, package validation, tests and documentation must be reconciled to the six-role topology. No stale Companion/Micro or sibling-messaging behavior may remain.

## Required authoritative updates

- Requirements / Project Definition: captured in `requirements/REQUIREMENTS.md`.
- Planning: must organize safe removal/addition and regression coverage.
- Task Card/OpenSpec: none yet.
- PROJECT.md: decision pointer required.

## Provenance

- Source discussion/request: `brainstorming/upstream-1.1.18-alignment.md`
- Evidence/research: `research/upstream-1.1.18-audit.md`
