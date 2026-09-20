# M02 structured Muse capability hints

## Why

Muse-backed workers execute in a separate capability plane from Codex Main. Each invocation needs a small, validated contract that tells Muse which Muse-side skills and external capabilities are required or useful without copying implementations, credentials, or mutation authority into the task capsule.

## Authority

- `elmakus/muse-capability-admin@8aecaa42d0ffd40efa2342b5bbace85fcc976d7e:planning/MASTER_PLAN.md#M02`
- `MCA-REQ-004` through `MCA-REQ-009` and `MCA-REQ-017`
- `MCA-DEC-001-STRUCTURED_CAPABILITY_HINTS.md`
- `MCA-DEC-002-ADMIN_AUTH_AND_SECRET_REUSE.md`
- `implementation/workstreams/change-structured-muse-capability-hints/cards/M02-T01.md`

## Change

Add an immutable `MuseCapabilityHints` value with four ordered categories and carry it through Python invocation, concurrent forwarding, CLI dispatch and prompt construction. Normalize all inputs through the value object, validate opaque identifiers, stable-deduplicate, and give required entries precedence over advisory duplicates in the same namespace.

Every prompt receives one deterministic current-invocation capability block. The block explicitly replaces all prior-turn hints, including on resume with an empty set, makes required unavailability fail-visible, leaves advisory unavailability non-blocking, and forbids interpreting hints as installation/authentication authority.

## Non-goals

No capability installation/configuration/authentication/removal, secret lookup, capability registry/catalog, alias resolution, workstation substrate changes, VERSION bump, release or deployment.
