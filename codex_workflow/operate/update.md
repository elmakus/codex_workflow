# Workflow Update

Supported command form:

    codex_workflow --update

Use Python 3.11 or newer. Updates are always owner-invoked; there is no
background or startup auto-update.

## Default source: owner GitHub Releases

The installed launcher queries GitHub Releases only for:

`elmakus/codex_workflow`

It selects the highest non-draft SemVer release that contains both:

- `codex_workflow-<version>.zip`
- `SHA256SUMS`

Prereleases are valid. The launcher downloads those two assets, verifies the
ZIP's SHA-256 against `SHA256SUMS`, enforces trusted GitHub URL/path and bounded
metadata/download/archive limits, validates ZIP member paths/types, safely
extracts the package into a temporary directory, and delegates the update to the
incoming package's own `runtime/workflow.py`. Never clone a repository as part
of the installed update path.

Run:

```text
python3 ~/.codex/codex_workflow/runtime/workflow.py update --project <project>
```

## Explicit local source fallback

A previously reviewed/extracted package may still be supplied through the
internal `--source <package-root>` path for recovery, testing, or an explicit
manual migration. That path must not perform release discovery or network
download.

Validate a local package before using it:

```text
python3 <verified-package-root>/runtime/workflow.py validate \
  --package-root <verified-package-root> \
  --json
```

Then run:

```text
python3 <verified-package-root>/runtime/workflow.py update \
  --source <verified-package-root> \
  --project <project>
```

## What the update changes

The incoming package is the complete desired definition of workflow-owned
runtime files:

- workflow-owned files present in the incoming package are created or replaced;
- workflow-owned files recorded by the previous install but absent from the
  incoming package are removed;
- worker TOMLs and workflow-owned skills follow the same ownership-aware rule;
- obsolete workflow-owned Codex settings, including the old fixed concurrency
  key, are retired when no longer part of the incoming contract;
- unrelated Codex settings, unrelated workers/skills, user content outside the
  managed user `AGENTS.md` region, project-local instructions, personalization,
  `agent_docs/`, and enabled/disabled project state are preserved.

The update creates a verified timestamped backup first and applies planned
mutations through one compensating transaction. A failure must not be reported
as a successful partial update.

The `~/.codex` runtime and worker definitions are shared across projects and are
replaced once. One `--project` invocation updates only that project's wrapper
and state, so migrate every intended existing project explicitly after changing
the shared runtime. No automatic project scanner or auto-install is implied.

If a legacy project entry point contains merged local edits, expect the update
to stop. Review and extract only the project-local instructions into a temporary
file, then rerun with:

```text
--legacy-local-instructions <reviewed-file>
```

Add `--allow-downgrade` only for an explicitly approved SemVer downgrade.

When the shared runtime already matches the incoming version, the command may
still bring an older target-project wrapper/state up to that version. A target
project already current is a no-op.

Report the installed version, backup location, and any failure.
