# Legacy local-instruction migration behavior

## Legacy route references

The migration guard MUST recognize these retired workflow-owned project route paths:

- `agent_docs/workflows/medium_route.md`
- `agent_docs/workflows/heavy_route.md`

A reference is stale for migration purposes when selected project-local instructions contain one of those paths and the referenced file is absent from the target project.

## Fail-closed behavior

Bootstrap, install and update MUST validate project-local instructions before importing or preserving them across a workflow rendering boundary.

If unreviewed selected instructions contain a stale legacy route reference, the operation MUST fail before mutation and MUST require explicitly reviewed local instructions.

Reviewed replacement instructions MUST:
- be supplied explicitly through `--legacy-local-instructions <file>`;
- remain subject to reserved-marker protection;
- themselves fail closed if they still reference a missing legacy route file.

The runtime MUST NOT infer replacement content by deleting, rewriting or otherwise interpreting stale route text.

## Command consistency

Bootstrap, install and update MUST accept the same reviewed local-instruction option and pass the reviewed text into the project migration planner.

Reviewed input requires an existing project entry point; supplying it for a project with no entry point MUST fail rather than create policy from an unattached file.

For a recognized current-format project, reviewed input MAY replace the protected project-local region while preserving workflow-managed and personalization boundaries.

For an unrecognized legacy `AGENTS.md`, reviewed input is the explicit local body imported into the protected local region.

## Preservation

Accepted local content MUST be preserved through normal marker rendering except for normalization already defined by the marker contract. Existing workflow-managed drift checks, personalization checks, reserved-marker rejection, transaction safety, T01 update-source/downgrade behavior, and VERSION/release boundaries remain unchanged.
