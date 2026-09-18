# Owner release preparation

`elmakus/codex_workflow` is the release source for this fork. Building a package
never changes an installed runtime or project. Publication happens only after a
reviewed change is merged to `main`.

## Source and version

The current version is `1.1.17-private.10`, based directly on upstream `v1.1.17`
commit `414a5d301ff17ca6e655330474c8346863d0d5d0`. Keep
`codex_workflow/operate/VERSION`, the marker in
`codex_workflow/operate/user_AGENTS.md`, README, and this document synchronized.

This release line contains the experimental mixed-harness `muse-max` profile.
Main remains the user-selected Codex model. Companion remains one persistent
internal Codex GPT-5.6 Luna XHigh worker; the six other workflow roles route
through native Muse Code with `muse-spark-1.3-contributor` and `max` reasoning.
Each Muse role is still a fresh bounded one-shot process. Project Workflow/Main
may concurrently await already-authorized independent lanes through the managed
adapter helper, while executor/tester/repair order remains sequential inside a
lane.

The existing `plus`, `luna-xhigh`, and `pro-x5` Codex-backed profiles remain
available and retain their existing allocations. The six Muse-assigned role
TOMLs remain canonical semantic contracts and `runtime/muse_worker.py` supplies
the external harness. On the current unprivileged workstation Docker boundary,
the nested Muse bubblewrap sandbox is disabled with `--disable-sandbox`; Docker
remains the outer isolation boundary. The runner does not use `--yolo`.

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
python3 -B scripts/package_release.py --verify /absolute/path/to/fresh-output/codex_workflow-1.1.17-private.10.zip
```

Expected release assets:

- `codex_workflow-1.1.17-private.10.zip`
- `SHA256SUMS`

Record the exact source commit and completed verification in the release notes or
other durable provenance record.

## GitHub Release publication

The repository release workflow is triggered by a `main` push that changes
`codex_workflow/operate/VERSION`. It re-runs the runtime regression suite,
validates and builds the package, verifies the archive and `SHA256SUMS`, then
publishes a prerelease for tag `v1.1.17-private.10` with exactly the expected ZIP
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
codex_workflow --profile luna-xhigh
codex_workflow --profile pro-x5
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
