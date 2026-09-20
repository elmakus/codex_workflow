# Decision — fork release version tracks aligned upstream generation

- Decision ID: `DEC-005`
- Date: `2026-09-20`
- Status: `accepted`
- Authority: `user`
- Supersedes: `none`
- Related requirements: `REQ-021`
- Related milestone/card: `upstream-1-1-18-alignment`

## Context

The fork may adopt an upstream release selectively by behavior rather than by wholesale merge or cherry-pick. The previous private release numbering kept the historical common source baseline in the SemVer core, which made a fork that had completed the accepted upstream 1.1.18 alignment appear to remain on the 1.1.17 generation.

## Decision

For future fork releases, the SemVer core `X.Y.Z` tracks the upstream generation that the fork has deliberately aligned to as its current release generation, even when the fork preserves intentional divergence and adopts upstream behavior selectively.

The private suffix restarts for a new aligned upstream generation:

- first private release aligned to upstream 1.1.18: `1.1.18-private.1`;
- later private-only changes on that generation increment the suffix: `1.1.18-private.2`, `1.1.18-private.3`, and so on;
- alignment to a later upstream generation starts that generation at `private.1`.

This version label does **not** claim source identity with upstream and does not override accepted fork-specific decisions. Release documentation must distinguish semantic alignment from direct source ancestry.

## Consequences

- The completed upstream-1.1.18 alignment is released as `1.1.18-private.1`.
- The already-published `1.1.17-private.13` remains immutable historical provenance but is superseded by `1.1.18-private.1`.
- README/RELEASING provenance must describe selective alignment to upstream 1.1.18 and retain the 1.1.17 common baseline only as ancestry context.
- Release regression expectations advance from `1.1.18-private.1` to `1.1.18-private.2`.

## Provenance

- User decision: current session, 2026-09-20.
- Related alignment authority: `decisions/DEC-004-selective-upstream-adoption.md`.
- Related research: `research/upstream-1.1.18-audit.md`.
