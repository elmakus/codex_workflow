# Muse capability-hint protocol

## Structured value

The runtime MUST expose frozen `MuseCapabilityHints` with these ordered tuple fields:

- `required_skills`
- `relevant_skills`
- `required_capabilities`
- `suggested_capabilities`

`MuseWorkerInvocation` MUST carry one value, defaulting to an empty instance.

## Identifier contract

Each identifier MUST be a non-empty, bounded opaque identifier of at most 128 characters and MUST match a conservative runtime-safe character grammar composed of ASCII letters, digits and `._:/@+-`. The first character MUST be alphanumeric. Whitespace, backslashes, shell quoting characters and arbitrary prose MUST fail validation before Muse launch.

V1 MUST NOT resolve aliases or consult a registry.

## Normalization

Construction is the single normalization boundary used by Python and CLI callers.

Within every category, preserve first caller order and remove exact duplicates.

Within the skill namespace, any identifier in `required_skills` MUST be removed from `relevant_skills`. Within the capability namespace, any identifier in `required_capabilities` MUST be removed from `suggested_capabilities`. No cross-namespace suppression occurs.

## CLI parity

Normal CLI dispatch MUST expose repeatable:

- `--required-skill`
- `--relevant-skill`
- `--required-capability`
- `--suggested-capability`

The four CLI collections MUST be converted to the same `MuseCapabilityHints` constructor used by Python callers before execution or dry-run output.

## Prompt semantics

Every Muse invocation MUST render one deterministic `CURRENT MUSE CAPABILITY HINTS` section, including when all categories are empty.

The section MUST state that:
- it is the complete authoritative hint set for this invocation;
- it replaces/supersedes prior-turn capability hints, including on resumed logical sessions;
- unavailable required skills/capabilities must be reported fail-visibly;
- unavailable relevant/suggested entries are advisory and non-blocking;
- hints do not authorize install/configure/authenticate/update/remove operations;
- Muse remains responsible for native skill loading and tool/MCP use.

Only normalized opaque identifiers may appear in the four category values.

## Invocation semantics

Direct execution and `execute_workers_concurrently(...)` MUST forward each invocation's normalized hints independently. A resumed turn MUST construct a fresh prompt from the current invocation value; no adapter-side hint state is retained in the logical session registry.

Executor and Tester session identity rules remain unchanged.

## Compatibility

Omitting hints is equivalent to passing `MuseCapabilityHints()`. Capability-free calls continue to execute with an explicit empty prompt block. Non-`muse-max` compute profile behavior is unchanged because the capability-hint contract lives only on the Muse adapter path.
