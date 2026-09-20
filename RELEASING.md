# Owner release preparation

`elmakus/codex_workflow` is the release source for this fork. Building a package
never changes an installed runtime or project. Publication happens only after a
reviewed change is merged to `main`.

## Source and version

The current version is `1.1.18-private.1`, selectively aligned to upstream
`v1.1.18` while preserving intentional fork-specific divergence. The meaningful
common source baseline remains upstream `v1.1.17` commit
`414a5d301ff17ca6e655330474c8346863d0d5d0`. Keep
`codex_workflow/operate/VERSION`, the marker in
`codex_workflow/operate/user_AGENTS.md`, README, and this document synchronized.

The SemVer core tracks the deliberately aligned upstream generation; the private
suffix restarts at `private.1` for a newly aligned generation. This identifies
release-generation alignment, not source identity with upstream.

This release line supports exactly two compute profiles: `plus` and
`muse-max`. Main remains the user-selected Codex model. The supported worker
set is Explorer, Investigator, Default Executor, Senior Executor, Tester, and
Archivist.

Under `plus`, all six workflow workers use the internal Codex worker lifecycle.
Under `muse-max`, all six route through native Muse Code with
`muse-spark-1.3-contributor` and `max` reasoning via
`runtime/muse_worker.py`. Muse workers use the retained logical-session/process
lifecycle: fresh independent boundaries receive distinct logical sessions, while
safe bounded follow-up or repair may resume the same retained session. Managed
batching is only for already-authorized independent lanes with isolated
workspaces; executor/tester/repair ordering remains sequential where the
workflow contract requires it.

The six role TOMLs remain canonical semantic contracts. On the current
unprivileged workstation Docker boundary, nested Muse bubblewrap cannot run, so
the Muse path uses `--disable-sandbox` and Docker remains the outer isolation
boundary. The runner does not use `--yolo`.

Only publish a release from a reviewed commit intended for this fork's `main`.
Do not publish a candidate branch merely to make the updater see it.

## Artifact

The ZIP includes only `codex_workflow/`. Repository documentation, tests,
images, Git metadata, and old ZIPs are not part of the package.

Use Python 3.11 or newer from a clean checkout of the exact reviewed commit:

```sh
python3 -B scripts/test_workflow_runtime.py -v
python3 -B scripts/test_muse_profile.py -v
python3 -B codex_workflow/runtime/workflow.py validate --package-root codex_workflow --json
python3 -B scripts/package_release.py --output-dir /absolute/path/to/fresh-output
python3 -B scripts/package_release.py --verify /absolute/path/to/fresh-output/codex_workflow-1.1.18-private.1.zip
```

Expected release assets:

- `codex_workflow-1.1.18-private.1.zip`
- `SHA256SUMS`

Record the exact source commit and completed verification in the release notes or
other durable provenance record.

## GitHub Release publication

The repository release workflow is triggered by a `main` push that changes
`codex_workflow/operate/VERSION`. It re-runs the runtime regression suite,
validates and builds the package, verifies the archive and `SHA256SUMS`, then
publishes a prerelease for tag `v1.1.18-private.1` with exactly the expected ZIP
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
codex_workflow --profile muse-max
```

`muse-max` additionally requires the official `muse` CLI on `PATH`, completed
Muse authentication, and account access to Muse Spark 1.3 Contributor Max.

The explicit verified local `--source` path remains available for recovery and
manual migration when needed.

The runtime under `~/.codex` and worker definitions are shared. The target
project's `AGENTS.md`, protected state, and `agent_docs/` are project-specific.
An update changes the shared runtime once and migrates only explicitly selected
project wrappers. Same-runtime project catch-up handles later targets.
