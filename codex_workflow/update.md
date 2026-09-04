# Workflow Update

Supported command forms:

    codex_workflow --update

Use Python 3.11 or newer. Apply the validated update directly with the lifecycle
CLI. An approved, verified private/local package source is required.

## Source

Public release discovery is disabled for this private downstream. Obtain the
approved private ZIP and matching `SHA256SUMS` built from a clean checkout of
the reviewed, pushed private commit. Verify the checksum, extract the ZIP
safely, and validate the incoming package before updating:

```text
python3 <verified-private-package-root>/workflow.py validate \
  --package-root <verified-private-package-root> \
  --json
```

Do not query or install from the public `viettran-edgeAI` release channel. An
update without an explicit source must fail closed.

## Update

Run:

```text
python3 ~/.codex/codex_workflow/workflow.py update \
  --source <verified-private-package-root> \
  --project <project>
```

For migration from a pre-script installation, run the incoming package's
`workflow.py` instead of an older installed launcher.

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
approved downgrade. In particular, SemVer orders each `1.1.13-private.N`
prerelease below public `1.1.13`, so a direct transition from an installed
public `1.1.13` requires that approved flag. A fresh private bootstrap does not.

When the shared user-level runtime already matches the incoming private version,
the command may update an older target-project wrapper/state to that version. A
target project that is already current is a no-op.

Report the installed version, backup location, and any failure.
Do not describe a partial or rolled-back update as successful.
