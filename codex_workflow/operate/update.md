# Workflow Update

Supported command forms:

    codex_workflow --update

Use Python 3.11 or newer. Apply the validated update directly with the lifecycle
CLI. An approved, verified private/local package source is required. This is a
manual local migration; no network access is part of the procedure.

## Source

Use an approved private ZIP and matching `SHA256SUMS` built from a clean
checkout of the reviewed, pushed private commit. Verify the checksum, extract
the ZIP safely, and validate the incoming package before updating:

```text
python3 <verified-private-package-root>/runtime/workflow.py validate \
  --package-root <verified-private-package-root> \
  --json
```

Do not query, download, or install from any public release channel. An update
without an explicit local `--source` must fail closed.

## Update

Run:

```text
python3 <verified-private-package-root>/runtime/workflow.py update \
  --source <verified-private-package-root> \
  --project <project>
```

The `~/.codex` runtime and worker definitions are shared across projects and
are replaced once; the authorized rollout migrates every existing project's
wrapper. One `--project` selects only one project's wrapper and documents per
invocation, not full per-project runtime isolation, so repeat the explicit
command for each project. No automatic project scanner or auto-install is
implied.

When the installed package still stores `VERSION` at its root, run the incoming
package's `runtime/workflow.py` instead of the installed launcher. The incoming
runtime recognizes that historical layout and migrates it transactionally.

Let the script replace installed routes, worker TOMLs, and workflow-owned skills
with the incoming release's fixed definitions. Expect it to preserve unrelated
Codex settings and skills, project documents, personalization, project-local
instructions, source backups, and the project's enabled/disabled state. For a
project still using an older workflow version, expect the script to validate its
managed region against that version's source backup. Expect it to remove
obsolete workflow-owned files and the retired workflow-owned `agent_docs/`
`.gitignore` rule, create a verified timestamped backup, and apply user/project
state through one compensating transaction. Preserve an `agent_docs/` ignore
rule that the user owns outside the workflow-managed block.

If a legacy project entry point contains merged local edits, expect the update
to stop. Review and extract only the project-local instructions into a temporary
file, then rerun with:

```text
--legacy-local-instructions <reviewed-file>
```

Treat this as a one-time migration into the dedicated local region. Never infer
the content automatically. Add `--allow-downgrade` only for an explicitly
approved downgrade. In particular, SemVer orders each `1.1.14-private.N`
prerelease below public `1.1.14`, so a direct transition from an installed
public `1.1.14` requires that approved flag. Moving from `1.1.13-private.2`
to `1.1.14-private.1` is a normal upgrade and does not require
`--allow-downgrade`; a fresh private bootstrap does not either.

When the shared user-level runtime already matches the incoming private version,
the command may update an older target-project wrapper/state to that version. A
target project that is already current is a no-op.

Report the installed version, backup location, and any failure.
Do not describe a partial or rolled-back update as successful.
