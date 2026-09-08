# Owner release preparation

`elmakus/codex_workflow` is the release source for this fork. Building a package
never changes an installed runtime or project. Publication is a separate,
explicit owner action after review and verification.

## Source and version

The current version is `1.1.14-private.3`. Keep
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
python3 -B scripts/package_release.py --verify /absolute/path/to/fresh-output/codex_workflow-1.1.14-private.3.zip
```

Expected release assets:

- `codex_workflow-1.1.14-private.3.zip`
- `SHA256SUMS`

Record the exact source commit and completed verification in the release notes or
other durable provenance record.

## GitHub Release publication

After the candidate is approved and merged to the intended release commit:

1. create a GitHub Release in `elmakus/codex_workflow` for the matching SemVer
   tag, for example `v1.1.14-private.3`;
2. attach exactly the verified versioned ZIP and its `SHA256SUMS`;
3. include concise release notes and the source commit SHA;
4. publish only after both assets are present and verified.

The installed updater ignores drafts and ignores any release that lacks either
the expected versioned ZIP or `SHA256SUMS`. Prereleases are valid because this
fork uses SemVer prerelease versions.

There is deliberately no automatic release-publishing workflow here. Publishing
a release remains an explicit owner action, while consuming an already published
owner release is automated by `codex_workflow --check-update` and
`codex_workflow --update`.

## Installation boundary

`1.1.14-private.2` predates owner-release discovery. Its first migration to
`1.1.14-private.3` therefore still uses the incoming package's explicit local
source path:

```text
python3 <verified-package-root>/runtime/workflow.py update \
  --source <verified-package-root> \
  --project <selected-project>
```

After private.3 is installed, future releases can normally use:

```text
codex_workflow --check-update
codex_workflow --update
```

The runtime under `~/.codex` and worker definitions are shared. The target
project's `AGENTS.md`, protected state and `agent_docs/` are project-specific.
A first migration changes shared runtime behavior and one project wrapper;
continue with the remaining intended project wrappers explicitly. Same-runtime
project catch-up handles those later targets.
