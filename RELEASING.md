# Owner release preparation

`elmakus/codex_workflow` is the release source for this fork. Building a package
never changes an installed runtime or project. Publication is a separate,
explicit owner action after review and verification.

## Source and version

The current version is `1.1.17-private.3`, based directly on upstream `v1.1.17`
commit `414a5d301ff17ca6e655330474c8346863d0d5d0`. Keep
`codex_workflow/operate/VERSION` and the marker in
`codex_workflow/operate/user_AGENTS.md` identical.

Only publish a release from a reviewed commit intended for this fork's `main`.
Do not publish a candidate branch merely to make the updater see it.

## Artifact

The ZIP includes only `codex_workflow/`. Repository documentation, tests,
images, Git metadata, and old ZIPs are not part of the package.

Use Python 3.11 or newer from a clean checkout of the exact reviewed commit:

```sh
python3 -B scripts/test_workflow_runtime.py -v
python3 -B codex_workflow/runtime/workflow.py validate --package-root codex_workflow --json
python3 -B scripts/package_release.py --output-dir /absolute/path/to/fresh-output
python3 -B scripts/package_release.py --verify /absolute/path/to/fresh-output/codex_workflow-1.1.17-private.3.zip
```

The main runtime regression suite includes the material-event `send_message`
policy contract; no separate release-only regression command is required.

Expected release assets:

- `codex_workflow-1.1.17-private.3.zip`
- `SHA256SUMS`

Record the exact source commit and completed verification in the release notes or
other durable provenance record.

## GitHub Release publication

After the candidate is approved and merged to the intended release commit:

1. create a GitHub Release in `elmakus/codex_workflow` for tag
   `v1.1.17-private.3`;
2. attach exactly the verified versioned ZIP and its `SHA256SUMS`;
3. include concise release notes and the source commit SHA;
4. publish only after both assets are present and verified.

The installed updater ignores drafts and releases lacking either expected asset.
Prereleases are valid. There is deliberately no automatic release-publishing
workflow; publication remains an explicit owner action.

## Installation boundary

This repository preparation does not install or update the workflow. After a
reviewed owner release is published, an already compatible private runtime may
normally use:

```text
codex_workflow --check-update
codex_workflow --update
```

The explicit verified local `--source` path remains available for recovery and
manual migration when needed.

The runtime under `~/.codex` and worker definitions are shared. The target
project's `AGENTS.md`, protected state, and `agent_docs/` are project-specific.
An update changes the shared runtime once and migrates only explicitly selected
project wrappers. Same-runtime project catch-up handles later targets.
