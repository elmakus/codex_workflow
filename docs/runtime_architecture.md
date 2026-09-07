# Lifecycle Runtime Architecture

The lifecycle runtime separates fixed release definitions, installation state,
generated outputs, and project-owned content.

## Data ownership

- Heavy route and worker TOMLs: authoritative behavior distributed by a release.
- `~/.codex/codex_workflow/operate/`: user command guides, the user-level
  instruction source, and package version metadata.
- `~/.codex/codex_workflow/install_state.json`: installed version and ownership
  manifests.
- Heavy and Archivist contracts: fixed release inputs copied unchanged.
- Worker TOMLs and workflow-owned Codex settings: materialized outputs.
- Project personalization: structured project state materialized into its own
  marker region.
- Project-local instructions: opaque preserved content in a separate marker
  region.
- Project documentation updates: main owns `project_diary.md`; Archivist owns
  assigned public and project documents, including closing progress and
  latest-session updates.

## Module boundaries

- `layout.py`: package and target path contracts.
- `platform_settings.py`: fixed workflow-owned Codex TOML keys.
- `markers.py`: strict text-region parsing and rendering.
- `project_ops.py`: project entry point, personalization, and documents.
- `runtime_ops.py`: user-level runtime and generated outputs.
- `backup.py`: persistent update backups.
- `transaction.py`: atomic file writes and compensating rollback.
- `plan.py`: validated mutation plans and compact summaries.
- `lifecycle.py`: composition only; it owns no low-level transformation.
- `release.py`: semantic-version parsing and ordering only; no network access.
- `runtime/workflow.py`: CLI parsing, direct application, two-phase removal, and
  incoming-runtime delegation.

The removal plan deletes the recognized project entry point and private
workflow resource, strips only the marked workflow region from the user-level
`AGENTS.md`, removes workflow-owned Codex settings and worker files, and
cleans the dedicated runtime directory. It deliberately preserves
`agent_docs/` and unrelated user-level content.

## Upgrade contract

1. The owner supplies an explicitly selected, verified local package. No
   command checks for releases or downloads an incoming package.
2. The incoming CLI validates and applies the update using the target
   version's runtime; the installed launcher does not apply its own
   version-specific package schema to that incoming release.
3. The incoming release replaces the installed Heavy route and worker definitions.
   Worker surfaces are copied from the incoming role files.
4. Each project entry point is validated against the source backup for the
   workflow version recorded in its project state. Project-local regions,
   personalization, unrelated user files, and enabled/disabled state are
   preserved as opaque data.
5. Marker drift or ambiguous legacy content stops before live writes.
6. Every write command validates and applies one mutation plan with rollback.

Changing built-in behavior requires updating its owning Heavy route, worker, or
platform module and the corresponding tests; installed retuning is unsupported.
