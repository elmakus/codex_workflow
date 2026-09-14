# Owner release preparation

`elmakus/codex_workflow` is the release source for this fork. Building a package
never changes an installed runtime or project. Publication happens only after a
reviewed change is merged to `main`.

## Source and version

The current version is `1.1.17-private.6`, based directly on upstream `v1.1.17`
commit `414a5d301ff17ca6e655330474c8346863d0d5d0`. Keep
`codex_workflow/operate/VERSION`, the marker in
`codex_workflow/operate/user_AGENTS.md`, and this document synchronized.

This release changes fresh/independent context routing. Fresh Codex boundaries,
independent reviews, and context resets now use new internal workers with
`fork_turns="none"` by default rather than app-level `create_thread` sessions.
`create_thread` is reserved for explicit top-level-thread requests or tasks that
need a capability/isolation property unavailable to internal workers. App-created
children are not assumed to inherit the parent's effective permission profile.

The release retains the global `plus` and `pro-x5` compute profiles introduced in
`1.1.17-private.5`. `plus` preserves the historical Luna-heavy allocation.
`pro-x5` uses GPT-5.6 Sol / low for ordinary workflow workers while keeping
Senior Executor at GPT-5.6 Sol / medium. Main-agent selection is unchanged.
Profile selection is explicit, persistent, and preserved across updates.

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
python3 -B scripts/package_release.py --verify /absolute/path/to/fresh-output/codex_workflow-1.1.17-private.6.zip
```

Expected release assets:

- `codex_workflow-1.1.17-private.6.zip`
- `SHA256SUMS`

Record the exact source commit and completed verification in the release notes or
other durable provenance record.

## GitHub Release publication

The repository release workflow is triggered by a `main` push that changes
`codex_workflow/operate/VERSION`. It re-runs the runtime regression suite,
validates and builds the package, verifies the archive and `SHA256SUMS`, then
publishes a prerelease for tag `v1.1.17-private.6` with exactly the expected ZIP
and checksum assets. The workflow finally verifies the published release.

The installed updater ignores drafts and releases lacking either expected asset.
Prereleases are valid.

## Installation boundary

Publishing does not install or update the workflow on a user machine. After the
reviewed owner release is published, an already compatible private runtime may
normally use:

```text
codex_workflow --check-update
codex_workflow --update
```

After updating, choose the desired global compute profile explicitly:

```text
codex_workflow --profile
codex_workflow --profile plus
codex_workflow --profile pro-x5
```

The explicit verified local `--source` path remains available for recovery and
manual migration when needed.

The runtime under `~/.codex` and worker definitions are shared. The target
project's `AGENTS.md`, protected state, and `agent_docs/` are project-specific.
An update changes the shared runtime once and migrates only explicitly selected
project wrappers. Same-runtime project catch-up handles later targets.
