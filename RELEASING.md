# Private package preparation

The private repository is the source of truth. This package is prepared for
later explicit installation; building it never changes an installed runtime
or project. There is no GitHub Release publication workflow.

## Source and artifact

The current version is `1.1.14-private.1`. Keep
`codex_workflow/operate/VERSION` and the marker in
`codex_workflow/operate/user_AGENTS.md` identical.

The ZIP includes only `codex_workflow/`. Repository documentation, tests,
images, Git metadata, and old public ZIPs are not part of the package.
Do not include the retired reporting skill or its script.

## Preparation order

1. Review changes against the pinned upstream and run lifecycle tests.
2. Commit and push the private candidate branch.
3. Create a clean checkout of the pushed commit.
4. Build a deterministic ZIP into a fresh directory and verify its contents.
5. Record the exact source commit and SHA-256 beside the ZIP.
6. Deliver the artifact without installing it. A later authorized rollout will
   cover all existing projects together.

Use Python 3.11 or newer. From the clean checkout:

```sh
python3 -B scripts/test_workflow_runtime.py -v
python3 -B codex_workflow/runtime/workflow.py validate --package-root codex_workflow --json
python3 -B scripts/package_release.py --output-dir /absolute/path/to/fresh-output
python3 -B scripts/package_release.py --verify /absolute/path/to/fresh-output/codex_workflow-1.1.14-private.1.zip
```

On Windows use the equivalent `py -3.11` invocation and native paths. All
lifecycle tests must use disposable homes and project roots; never test by
installing into the owner's actual `~/.codex` or projects.

The output is `codex_workflow-1.1.14-private.1.zip` and `SHA256SUMS`. Keep a
separate provenance record with the source commit and completed verification.
Do not publish a release, create a tag, or install as part of package creation.

## Later installation boundary

Read the bundled `operate/bootstrap.md` or `operate/update.md` at the time of
an owner-requested installation. The local migration entry point is
`codex_workflow/runtime/workflow.py update --source <verified-package-root>
--project <selected-project>`. The old 1.1.13 launcher does not understand the
new package layout.

The runtime under `~/.codex` and worker definitions are shared. The target
project's `AGENTS.md`, protected state and `agent_docs/` are project-specific.
A first migration changes shared runtime behavior and one project wrapper;
continue with all remaining existing project wrappers in the same coordinated
rollout. Same-runtime project catch-up handles these later targets. There is
no permanent mixed-version or selective-project rollout planned.
